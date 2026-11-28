"""Verified AnswerPackage orchestrator (ANS 01-08, KNW 01-04, Common Bid Basis bounds)."""

import html
import uuid
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.modules.answer.models import AnswerCitationRecord, AnswerPackageRecord
from src.modules.answer.schemas import AnswerCitation, AnswerPackage, AnswerQueryRequest
from src.modules.audit.service import AuditService
from src.modules.knowledge.schemas import PassageSummary
from src.modules.policy.schemas import ApplicabilityCandidate, CriticalFieldItem
from src.modules.policy.service import PolicyService
from src.modules.retrieval.service import RetrievalService
from src.modules.selection.o1_context import (
    CustomerContextO1,
    apply_o1_to_scope_dimensions,
    validate_o1_customer_record,
)
from src.modules.selection.schemas import ScopeDimensions
from src.modules.validation.service import ValidationService
from src.shared.auth import AuthenticatedUser
from src.shared.contracts import (
    AuditMeterPort,
    HybridQuerySpec,
    LLMGenerationRequest,
    LLMGeneratorPort,
    PolicyGatePort,
    RetrievalPort,
    ValidationGatePort,
)
from src.shared.enums import AnswerStatus
from src.shared.exceptions import AccessDenied
from src.shared.pii_guard import scan_query_for_pii

INTERNAL_USE_WARNING_VI = (
    "Hướng dẫn làm việc nội bộ — nhân viên phải kiểm tra hoàn cảnh, nguồn hiện hành và thẩm quyền "
    "trước khi hành động; không thay thế phê duyệt hay thực thi."
)

_OUT_OF_SCOPE_MARKERS: tuple[tuple[str, str], ...] = (
    ("pháp lý", "Tư vấn pháp lý nằm ngoài phạm vi trợ lý (ANS 07)."),
    ("luật", "Tư vấn pháp lý nằm ngoài phạm vi trợ lý (ANS 07)."),
    ("thuế", "Tư vấn thuế nằm ngoài phạm vi trợ lý (ANS 07)."),
    ("duyệt bảo hành", "Hệ thống không tự phê duyệt bảo hành; chuyển Policy Owner."),
    ("duyệt chiết khấu", "Hệ thống không tự phê duyệt chiết khấu; chuyển cấp có thẩm quyền."),
    ("sửa chữa thiết bị", "Hướng dẫn sửa chữa/an toàn thiết bị nằm ngoài phạm vi (ANS 07)."),
)

_BACKEND_ROOT = Path(__file__).resolve().parents[3]
_REPO_ROOT = Path(__file__).resolve().parents[4]


_SCOPE_DIMENSION_KEYS: tuple[str, ...] = (
    "company",
    "branch",
    "role",
    "customer_category",
    "product",
    "transaction_scope",
)


def _escape_xml_value(text: str) -> str:
    """Neutralize XML/tag delimiter characters in untrusted inputs (ANS 08)."""
    return html.escape(text, quote=True)


def parse_scope_dimensions_6dim(scope_str: str) -> dict[str, str]:
    """Deterministically parse a scope string into the 6 DAT 04 dimensions."""
    parsed: dict[str, str] = {key: "unspecified" for key in _SCOPE_DIMENSION_KEYS}
    for token in scope_str.split(";"):
        part = token.strip()
        if not part:
            continue
        sep = ":" if ":" in part else ("=" if "=" in part else None)
        if sep is None:
            continue
        raw_key, raw_val = part.split(sep, maxsplit=1)
        key = raw_key.strip().lower()
        if key == "customer_group":
            key = "customer_category"
        if key in parsed:
            val = raw_val.strip()
            if val:
                parsed[key] = val
    return parsed


def count_vietnamese_words(text: str) -> int:
    """Count whitespace-delimited words for 100-250w Vietnamese guidance telemetry."""
    return len(text.split())


def bound_deterministic_critical_fields(
    fields: list[CriticalFieldItem],
) -> tuple[list[CriticalFieldItem], str | None]:
    """Bound critical fields to <= 8 rows and check <= 6000 Unicode chars without silent loss."""
    warnings: list[str] = []
    max_items = settings.ANSWER_MAX_PASSAGES
    max_chars = settings.PASSAGE_MAX_CHARS
    if len(fields) > max_items:
        warnings.append(
            f"Vượt trần hiển thị ({len(fields)}/{max_items} trường trọng yếu); "
            f"chỉ giữ {max_items} mục đầu tiên."
        )
    bounded = list(fields[:max_items])
    for cf in bounded:
        entry_text = " ".join(
            [
                cf.field_name,
                cf.value,
                cf.approval_role,
                cf.time_limit or "",
                cf.exception_condition or "",
                cf.source_clause,
                *cf.required_documents,
            ]
        )
        if len(entry_text) > max_chars:
            warnings.append(
                f"Trường {cf.field_id} ({cf.field_name}) dài {len(entry_text)}/{max_chars} "
                "ký tự Unicode (OPS 08: không cắt ngắn âm thầm)."
            )
    return bounded, (" ".join(warnings) if warnings else None)


def _format_scope_from_dimensions(dims: ScopeDimensions) -> str:
    data = dims.model_dump()
    return ";".join(f"{k}:{data.get(k) or 'all'}" for k in _SCOPE_DIMENSION_KEYS)


class AnswerOrchestratorService:
    """Produces non-streamed, post-validated 7-part AnswerPackages bounded by RFP limits."""

    def __init__(
        self,
        policy_gate: PolicyGatePort | None = None,
        retrieval_port: RetrievalPort | None = None,
        llm_generator: LLMGeneratorPort | None = None,
        validation_gate: ValidationGatePort | None = None,
        audit_meter: AuditMeterPort | None = None,
    ) -> None:
        self._policy_service = PolicyService()
        self._policy_gate: PolicyGatePort = policy_gate or self._policy_service
        selected_retrieval: RetrievalPort
        if retrieval_port is not None:
            selected_retrieval = retrieval_port
        else:
            selected_retrieval = RetrievalService()
        self._retrieval_port = selected_retrieval
        self._llm_generator: LLMGeneratorPort | None = llm_generator
        self._validation_gate: ValidationGatePort = validation_gate or ValidationService()
        self._audit_meter: AuditMeterPort = audit_meter or AuditService()

    def load_system_prompt(self, prompt_path: str | Path | None = None) -> str:
        """Load the authoritative Vietnamese system prompt from configured repository path."""
        raw_path = Path(prompt_path or settings.ANSWER_SYSTEM_PROMPT_PATH)
        candidates = (
            (raw_path,)
            if raw_path.is_absolute()
            else (raw_path, _BACKEND_ROOT / raw_path, _REPO_ROOT / raw_path)
        )
        for candidate in candidates:
            if candidate.is_file():
                return candidate.read_text(encoding="utf-8").strip()
        raise FileNotFoundError(f"Answer system prompt file not found: {raw_path}")

    def build_untrusted_prompt_envelope(
        self,
        question: str,
        passages: list[PassageSummary],
        critical_fields: list[CriticalFieldItem],
    ) -> str:
        """Isolate untrusted question/passages from system rules with explicit XML boundaries."""
        safe_question = _escape_xml_value(question)
        passage_blocks = [
            (
                f'  <passage id="{_escape_xml_value(p.passage_id)}" '
                f'doc_version="{_escape_xml_value(p.document_version_id)}" '
                f'clause="{_escape_xml_value(p.clause_ref)}" '
                f'page="{p.page_number}" '
                f'status="{_escape_xml_value(p.status.value)}">\n'
                f"    <title>{_escape_xml_value(p.title)}</title>\n"
                f"    <content>{_escape_xml_value(p.content)}</content>\n"
                f"  </passage>"
            )
            for p in passages
        ]
        cf_blocks = [
            (
                f'  <critical_field id="{_escape_xml_value(cf.field_id)}" '
                f'name="{_escape_xml_value(cf.field_name)}" '
                f'operator="{_escape_xml_value(cf.operator.value)}" '
                f'value="{_escape_xml_value(cf.value)}" '
                f'unit="{_escape_xml_value(cf.unit or "")}" '
                f'currency="{_escape_xml_value(cf.currency or "")}" '
                f'approval_role="{_escape_xml_value(cf.approval_role)}" '
                f'source_clause="{_escape_xml_value(cf.source_clause)}" '
                f'status="{_escape_xml_value(cf.status.value)}" />'
            )
            for cf in critical_fields
        ]
        passages_xml = "\n".join(passage_blocks) if passage_blocks else "  <!-- none -->"
        cf_xml = "\n".join(cf_blocks) if cf_blocks else "  <!-- none -->"
        return (
            "<prompt_envelope>\n"
            f"<user_question>\n{safe_question}\n</user_question>\n\n"
            f"<retrieved_passages>\n{passages_xml}\n</retrieved_passages>\n\n"
            f"<critical_fields>\n{cf_xml}\n</critical_fields>\n"
            "</prompt_envelope>"
        )

    def _resolve_o1_context(
        self, request: AnswerQueryRequest
    ) -> tuple[bool, CustomerContextO1 | None, str]:
        """Enforce Option O1 Base Scope lock and enrich 6-dim scope when O1 is enabled."""
        if request.o1_context is not None and not settings.ENABLE_O1_CONTEXT_IMPORT:
            raise AccessDenied("O1_OPTION_DISABLED_IN_BASE_SCOPE")

        if not settings.ENABLE_O1_CONTEXT_IMPORT:
            return False, None, request.scope

        if request.o1_context is None:
            return True, None, request.scope

        validated_o1 = validate_o1_customer_record(request.o1_context.model_dump())
        parsed = parse_scope_dimensions_6dim(request.scope)
        base_dims = ScopeDimensions(
            **{
                k: (None if parsed[k] == "unspecified" else parsed[k])
                for k in _SCOPE_DIMENSION_KEYS
            }
        )
        enriched_dims = apply_o1_to_scope_dimensions(base_dims, validated_o1)
        return True, validated_o1, _format_scope_from_dimensions(enriched_dims)

    def build_guarded_response(
        self,
        user: AuthenticatedUser,
        request: AnswerQueryRequest,
        *,
        is_regenerate: bool = False,
    ) -> AnswerPackage:
        """Execute Base Scope guards, PII scan, VN date resolution, and boundary checks."""
        _ = user
        self._assert_non_streaming()
        o1_enabled, o1_record, effective_scope = self._resolve_o1_context(request)

        task_id = request.task_id or f"TASK-{uuid.uuid4().hex[:8].upper()}"
        answer_id = f"ANS-{uuid.uuid4().hex[:10].upper()}"
        pii_scan = scan_query_for_pii(request.question)
        pii_warning = pii_scan.warning_message_vi or None
        gov_date, is_hist, is_future = self._policy_gate.resolve_governing_date_vn(
            request.governing_date
        )
        is_future_preview = is_future and request.allow_future_preview

        refusal_reason = self._detect_out_of_scope(request.question)
        if refusal_reason is not None:
            return self._build_answer_package(
                answer_id=answer_id,
                task_id=task_id,
                status=AnswerStatus.REFUSED_OUT_OF_SCOPE,
                request=request,
                effective_scope=effective_scope,
                o1_enabled=o1_enabled,
                o1_record=o1_record,
                governing_date=gov_date,
                is_historical=is_hist,
                is_future_preview=is_future_preview,
                guidance_text=(
                    "Yêu cầu nằm ngoài thẩm quyền hỗ trợ của CKPA. Vui lòng chuyển xử lý tới "
                    "chủ sở hữu/phòng ban chuyên trách."
                ),
                hold_reason=refusal_reason,
                uncertainty_note="Ngoài ranh giới nghiệp vụ Base Scope (`ANS 07`).",
                pii_warning=pii_warning,
            )

        action_note = "Tạo lại gói trả lời" if is_regenerate else "Khung điều phối hợp đồng 7 phần"
        return self._build_answer_package(
            answer_id=answer_id,
            task_id=task_id,
            status=AnswerStatus.HOLD,
            request=request,
            effective_scope=effective_scope,
            o1_enabled=o1_enabled,
            o1_record=o1_record,
            governing_date=gov_date,
            is_historical=is_hist,
            is_future_preview=is_future_preview,
            guidance_text=(
                f"{action_note}: chưa có bằng chứng chính sách hợp lệ được nạp cho câu hỏi này; "
                "hệ thống HOLD kết luận và không dùng trí nhớ mô hình để suy đoán."
            ),
            missing_facts=["Cần nguồn chính sách/SOP hiệu lực đã kiểm chứng cho phạm vi đã chọn."],
            hold_reason="Insufficient verified curated evidence; fail-closed HOLD enforced.",
            uncertainty_note="Vui lòng bổ sung ngày giao dịch/phạm vi hoặc tạo Local Referral.",
            pii_warning=pii_warning,
        )

    async def execute_pipeline(
        self,
        user: AuthenticatedUser,
        request: AnswerQueryRequest,
        *,
        db: AsyncSession | None = None,
        candidates: list[ApplicabilityCandidate] | None = None,
        critical_fields: list[CriticalFieldItem] | None = None,
        emergency_disabled: bool = False,
        is_regenerate: bool = False,
    ) -> AnswerPackage:
        """Execute 5-layer Modular Monolith + Deterministic Policy Gate + Constrained RAG flow."""
        self._assert_non_streaming()
        o1_enabled, o1_record, effective_scope = self._resolve_o1_context(request)

        task_id = request.task_id or f"TASK-{uuid.uuid4().hex[:8].upper()}"
        answer_id = f"ANS-{uuid.uuid4().hex[:10].upper()}"
        pii_scan = scan_query_for_pii(request.question)
        pii_warning = pii_scan.warning_message_vi or None
        llm_question = (
            pii_scan.redacted_preview if pii_scan.has_suspected_pii else request.question
        )
        gov_date, is_hist, is_future = self._policy_gate.resolve_governing_date_vn(
            request.governing_date
        )
        is_future_preview = is_future and request.allow_future_preview

        # Layer 1: Emergency disable, out-of-scope boundary, and monthly quota checks.
        if emergency_disabled:
            pkg = self._build_answer_package(
                answer_id=answer_id,
                task_id=task_id,
                status=AnswerStatus.HOLD,
                request=request,
                effective_scope=effective_scope,
                o1_enabled=o1_enabled,
                o1_record=o1_record,
                governing_date=gov_date,
                is_historical=is_hist,
                is_future_preview=is_future_preview,
                guidance_text=(
                    "Trợ lý đang tạm dừng theo chế độ khẩn cấp (OPS 05); vui lòng tra cứu "
                    "nguồn CSV nội bộ hoặc liên hệ chủ sở hữu chính sách."
                ),
                hold_reason="OPS 05 Emergency Disable active; fail-closed HOLD enforced.",
                uncertainty_note="Chế độ tra cứu CSV thủ công vẫn hoạt động.",
                pii_warning=pii_warning,
            )
            return await self._record_and_return(db, user, pkg)

        refusal_reason = self._detect_out_of_scope(request.question)
        if refusal_reason is not None:
            pkg = self._build_answer_package(
                answer_id=answer_id,
                task_id=task_id,
                status=AnswerStatus.REFUSED_OUT_OF_SCOPE,
                request=request,
                effective_scope=effective_scope,
                o1_enabled=o1_enabled,
                o1_record=o1_record,
                governing_date=gov_date,
                is_historical=is_hist,
                is_future_preview=is_future_preview,
                guidance_text=(
                    "Yêu cầu nằm ngoài thẩm quyền hỗ trợ của CKPA. Vui lòng chuyển xử lý tới "
                    "chủ sở hữu/phòng ban chuyên trách."
                ),
                hold_reason=refusal_reason,
                uncertainty_note="Ngoài ranh giới nghiệp vụ Base Scope (`ANS 07`).",
                pii_warning=pii_warning,
            )
            return await self._record_and_return(db, user, pkg)

        quota = await self._audit_meter.check_monthly_quota(db)
        if not quota.allowed:
            pkg = self._build_answer_package(
                answer_id=answer_id,
                task_id=task_id,
                status=AnswerStatus.HOLD,
                request=request,
                effective_scope=effective_scope,
                o1_enabled=o1_enabled,
                o1_record=o1_record,
                governing_date=gov_date,
                is_historical=is_hist,
                is_future_preview=is_future_preview,
                guidance_text=(
                    "Hệ thống đạt giới hạn ngân sách tháng (OPS 06); kết luận HOLD để chờ "
                    "xử lý thủ công từ chủ sở hữu chính sách."
                ),
                hold_reason=quota.reason or "Common Bid Basis monthly quota exceeded.",
                pii_warning=pii_warning,
            )
            return await self._record_and_return(db, user, pkg)

        # Layer 2: Deterministic Policy Gate (VN date, conflict hold, typed critical fields).
        effective_requested_date = (
            request.governing_date
            or datetime.now(ZoneInfo(settings.APP_TIMEZONE)).date()
        )
        gate = self._policy_gate.evaluate_policy_gate(
            candidates or [],
            requested_date=effective_requested_date,
            allow_future_preview=request.allow_future_preview,
            critical_fields=critical_fields,
        )
        if not gate.can_proceed:
            pkg = self._build_answer_package(
                answer_id=answer_id,
                task_id=task_id,
                status=AnswerStatus.HOLD,
                request=request,
                effective_scope=effective_scope,
                o1_enabled=o1_enabled,
                o1_record=o1_record,
                governing_date=gate.governing_date,
                is_historical=gate.is_historical,
                is_future_preview=gate.is_future_preview,
                guidance_text=(
                    "Cổng chính sách xác định HOLD do thiếu phiên bản hiệu lực hoặc phát hiện "
                    "xung đột phạm vi/thẩm quyền (DAT 04/05)."
                ),
                critical_fields=list(gate.critical_fields),
                missing_facts=["Cần xác nhận phiên bản chính sách hiệu lực cho ngày chi phối."],
                hold_reason=gate.hold_reason or "Policy gate failed closed.",
                pii_warning=pii_warning,
                snapshot_age_hours=gate.snapshot_age_hours,
            )
            return await self._record_and_return(db, user, pkg)

        # Layer 3: Pre-filtered hybrid Vietnamese retrieval (bounded <= ANSWER_MAX_PASSAGES).
        spec = HybridQuerySpec(
            query=request.question,
            governing_date=gate.governing_date,
            scope_filter=effective_scope,
            applicable_version_ids=gate.applicable_version_ids,
            allow_historical=gate.is_historical,
            allow_future_preview=gate.is_future_preview,
            top_k=settings.ANSWER_MAX_PASSAGES,
        )
        passages = await self._retrieval_port.search_hybrid(user, spec)
        if not passages:
            action_note = "Tạo lại gói trả lời" if is_regenerate else "Khung điều phối 5 tầng"
            pkg = self._build_answer_package(
                answer_id=answer_id,
                task_id=task_id,
                status=AnswerStatus.HOLD,
                request=request,
                effective_scope=effective_scope,
                o1_enabled=o1_enabled,
                o1_record=o1_record,
                governing_date=gate.governing_date,
                is_historical=gate.is_historical,
                is_future_preview=gate.is_future_preview,
                guidance_text=(
                    f"{action_note}: không có đoạn văn bản hợp lệ sau tiền lọc RBAC/hiệu lực; "
                    "hệ thống HOLD kết luận và không dùng trí nhớ mô hình để suy đoán."
                ),
                critical_fields=list(gate.critical_fields),
                missing_facts=[
                    "Cần nguồn chính sách/SOP hiệu lực đã kiểm chứng cho phạm vi đã chọn."
                ],
                hold_reason="Insufficient verified curated evidence; fail-closed HOLD enforced.",
                uncertainty_note="Vui lòng bổ sung ngày giao dịch/phạm vi hoặc tạo Local Referral.",
                pii_warning=pii_warning,
                snapshot_age_hours=gate.snapshot_age_hours,
            )
            return await self._record_and_return(db, user, pkg)

        # Layer 4: Bounded non-streamed LLM generation with untrusted-data XML isolation.
        if self._llm_generator is None:
            pkg = self._build_answer_package(
                answer_id=answer_id,
                task_id=task_id,
                status=AnswerStatus.HOLD,
                request=request,
                effective_scope=effective_scope,
                o1_enabled=o1_enabled,
                o1_record=o1_record,
                governing_date=gate.governing_date,
                is_historical=gate.is_historical,
                is_future_preview=gate.is_future_preview,
                guidance_text=(
                    "Bộ sinh ngôn ngữ (Layer 4) chưa được cấu hình (dự kiến Gate G1); "
                    "hệ thống HOLD kết luận an toàn."
                ),
                critical_fields=list(gate.critical_fields),
                hold_reason="LLM generator port not configured (scheduled Gate G1).",
                pii_warning=pii_warning,
                snapshot_age_hours=gate.snapshot_age_hours,
            )
            return await self._record_and_return(db, user, pkg)

        system_prompt = self.load_system_prompt()
        envelope = self.build_untrusted_prompt_envelope(
            llm_question, passages, list(gate.critical_fields)
        )
        gen_req = LLMGenerationRequest(
            task_id=task_id,
            question=llm_question,
            system_prompt=system_prompt,
            user_prompt_envelope=envelope,
            governing_date=gate.governing_date,
            passages=tuple(passages),
            critical_fields=gate.critical_fields,
            max_input_tokens=settings.LLM_MAX_INPUT_TOKENS,
            max_output_tokens=settings.LLM_MAX_OUTPUT_TOKENS,
            timeout_seconds=settings.LLM_REQUEST_TIMEOUT_SECONDS,
        )
        gen_res = await self._llm_generator.generate(gen_req)

        if gen_res.llm_calls_used > settings.LLM_MAX_CALLS_PER_PACKAGE:
            pkg = self._build_answer_package(
                answer_id=answer_id,
                task_id=task_id,
                status=AnswerStatus.HOLD,
                request=request,
                effective_scope=effective_scope,
                o1_enabled=o1_enabled,
                o1_record=o1_record,
                governing_date=gate.governing_date,
                is_historical=gate.is_historical,
                is_future_preview=gate.is_future_preview,
                guidance_text="Số lượt gọi LLM vượt ngưỡng cho phép; kết luận HOLD an toàn.",
                critical_fields=list(gate.critical_fields),
                hold_reason="LLM_MAX_CALLS_PER_PACKAGE exceeded.",
                pii_warning=pii_warning,
                snapshot_age_hours=gate.snapshot_age_hours,
                llm_calls_used=settings.LLM_MAX_CALLS_PER_PACKAGE,
            )
            return await self._record_and_return(
                db,
                user,
                pkg,
                input_tokens=gen_res.input_tokens,
                output_tokens=gen_res.output_tokens,
                is_error=True,
            )

        has_conditions = (
            gate.is_historical
            or gate.is_future_preview
            or bool(gen_res.uncertainty_note)
            or bool(gen_res.missing_facts)
            or any(cf.exception_condition for cf in gate.critical_fields)
        )
        if gen_res.hold_reason:
            resolved_status = AnswerStatus.HOLD
        elif has_conditions:
            resolved_status = AnswerStatus.ANSWERED_WITH_CONDITIONS
        else:
            resolved_status = AnswerStatus.ANSWERED

        candidate_pkg = self._build_answer_package(
            answer_id=answer_id,
            task_id=task_id,
            status=resolved_status,
            request=request,
            effective_scope=effective_scope,
            o1_enabled=o1_enabled,
            o1_record=o1_record,
            governing_date=gate.governing_date,
            is_historical=gate.is_historical,
            is_future_preview=gate.is_future_preview,
            guidance_text=gen_res.guidance_text,
            verbatim_quotes=list(gen_res.verbatim_quotes),
            citations=list(gen_res.citations),
            critical_fields=list(gate.critical_fields),
            missing_facts=list(gen_res.missing_facts),
            hold_reason=gen_res.hold_reason,
            uncertainty_note=gen_res.uncertainty_note,
            referral_target="policy_owner" if gen_res.hold_reason else None,
            pii_warning=pii_warning,
            snapshot_age_hours=gate.snapshot_age_hours,
            llm_calls_used=gen_res.llm_calls_used,
        )

        # Layer 5: Post-generation authoritative re-fetch, validation & usage/audit metering.
        passage_ids = list(
            dict.fromkeys(
                [c.passage_id for c in candidate_pkg.citations] + [p.passage_id for p in passages]
            )
        )
        authoritative_passages = await self._retrieval_port.fetch_authoritative_passages(
            user, passage_ids, db
        )
        verified = self._validation_gate.verify_final_delivery(
            user,
            candidate_pkg,
            authoritative_passages,
            emergency_disabled=emergency_disabled,
        )
        return await self._record_and_return(
            db,
            user,
            verified,
            input_tokens=gen_res.input_tokens,
            output_tokens=gen_res.output_tokens,
        )

    def _assert_non_streaming(self) -> None:
        if settings.ENABLE_ANSWER_STREAMING:
            raise ValueError(
                "Pre-verification token streaming is forbidden in Base Scope (KNW 04)."
            )

    def _build_answer_package(
        self,
        *,
        answer_id: str,
        task_id: str,
        status: AnswerStatus,
        request: AnswerQueryRequest,
        effective_scope: str | None = None,
        o1_enabled: bool = False,
        o1_record: CustomerContextO1 | None = None,
        governing_date: date,
        is_historical: bool,
        is_future_preview: bool,
        guidance_text: str,
        verbatim_quotes: list[str] | None = None,
        citations: list[AnswerCitation] | None = None,
        critical_fields: list[CriticalFieldItem] | None = None,
        missing_facts: list[str] | None = None,
        hold_reason: str | None = None,
        uncertainty_note: str | None = None,
        referral_target: str | None = "policy_owner",
        pii_warning: str | None = None,
        snapshot_age_hours: float | None = None,
        llm_calls_used: int = 0,
    ) -> AnswerPackage:
        final_scope = effective_scope or request.scope
        bounded_citations = (citations or [])[: settings.ANSWER_MAX_PASSAGES]
        bounded_cfs, cf_cap_warning = bound_deterministic_critical_fields(critical_fields or [])
        return AnswerPackage(
            answer_id=answer_id,
            task_id=task_id,
            status=status,
            original_question=request.question,
            governing_date=governing_date,
            timezone=settings.APP_TIMEZONE,
            scope=final_scope,
            scope_matched_dimensions=parse_scope_dimensions_6dim(final_scope),
            is_historical=is_historical,
            is_future_preview=is_future_preview,
            guidance_text=guidance_text,
            guidance_word_count=count_vietnamese_words(guidance_text),
            verbatim_quotes=verbatim_quotes or [],
            citations=bounded_citations,
            critical_fields=bounded_cfs,
            critical_field_cap_warning=cf_cap_warning,
            missing_facts=missing_facts or [],
            hold_reason=hold_reason,
            uncertainty_note=uncertainty_note,
            referral_target=referral_target,
            internal_use_warning=INTERNAL_USE_WARNING_VI,
            o1_enabled=o1_enabled,
            o1_record=o1_record,
            pii_warning=pii_warning,
            snapshot_age_hours=snapshot_age_hours,
            llm_calls_used=llm_calls_used,
        )

    async def _record_and_return(
        self,
        db: AsyncSession | None,
        user: AuthenticatedUser,
        package: AnswerPackage,
        *,
        input_tokens: int = 0,
        output_tokens: int = 0,
        is_error: bool = False,
    ) -> AnswerPackage:
        if db is not None:
            await self._persist_answer_package(db, user, package)
        await self._audit_meter.record_usage_meter(
            db,
            task_id=package.task_id,
            answer_package_id=package.answer_id,
            llm_calls=package.llm_calls_used,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            is_hold=package.status
            in {AnswerStatus.HOLD, AnswerStatus.HOLD_AND_REFER, AnswerStatus.STALE},
            is_error=is_error,
        )
        await self._audit_meter.record_audit_event(
            db,
            actor_id=user.user_id,
            actor_role=",".join(sorted(r.value for r in user.roles)),
            action="answer_execute_pipeline",
            resource_type="answer_package",
            resource_id=package.answer_id,
            outcome=package.status.value,
            detail=package.hold_reason,
        )
        return package

    async def _persist_answer_package(
        self,
        db: AsyncSession,
        user: AuthenticatedUser,
        package: AnswerPackage,
    ) -> None:
        """Persist citation links so KNW 04 can invalidate active answer packages."""
        record = await db.get(AnswerPackageRecord, package.answer_id)
        if record is None:
            record = AnswerPackageRecord(
                id=package.answer_id,
                task_id=package.task_id,
                user_id=user.user_id,
                original_question=package.original_question,
                governing_date=package.governing_date,
                scope=package.scope,
                status=package.status.value,
                guidance_text=package.guidance_text,
                hold_reason=package.hold_reason,
                referral_target=package.referral_target,
                is_stale=package.status == AnswerStatus.STALE,
                llm_calls_used=package.llm_calls_used,
                package_payload=package.model_dump(mode="json"),
            )
            db.add(record)
        else:
            record.status = package.status.value
            record.guidance_text = package.guidance_text
            record.hold_reason = package.hold_reason
            record.referral_target = package.referral_target
            record.is_stale = record.is_stale or package.status == AnswerStatus.STALE
            record.llm_calls_used = package.llm_calls_used
            record.package_payload = package.model_dump(mode="json")
            await db.execute(
                delete(AnswerCitationRecord).where(
                    AnswerCitationRecord.answer_package_id == package.answer_id
                )
            )

        for citation in package.citations:
            db.add(
                AnswerCitationRecord(
                    answer_package_id=package.answer_id,
                    passage_id=citation.passage_id,
                    document_version_id=citation.document_version_id,
                    page_number=citation.page_number,
                    clause_ref=citation.clause_ref,
                )
            )

    def _detect_out_of_scope(self, question: str) -> str | None:
        lowered = question.lower()
        for keyword, reason in _OUT_OF_SCOPE_MARKERS:
            if keyword in lowered:
                return reason
        return None
