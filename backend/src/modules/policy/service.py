"""Policy applicability, authority matrix, and deterministic threshold logic (DAT 03-06)."""

from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.modules.policy.models import AuthorityEntry, CriticalField
from src.modules.policy.schemas import (
    ApplicabilityCandidate,
    ApplicabilityResult,
    AuthorityEntryResponse,
    CriticalFieldItem,
)
from src.shared.auth import AuthenticatedUser, check_policy_audience
from src.shared.contracts import PolicyGateDecision
from src.shared.enums import (
    AuthorityTier,
    ComparisonOperator,
    CriticalFieldType,
    PolicyFamily,
    PolicyLifecycleStatus,
    UserRole,
)

_PRIVILEGED_POLICY_ROLES: frozenset[UserRole] = frozenset(
    {
        UserRole.POLICY_OWNER,
        UserRole.STEWARD,
        UserRole.ADMINISTRATOR,
    }
)


class PolicyService:
    """Enforces VN governing-date logic, conflict hold, and typed critical field arithmetic."""

    def resolve_governing_date_vn(
        self, requested_date: date | None
    ) -> tuple[date, bool, bool]:
        """Resolve effective calendar date in Asia/Ho_Chi_Minh and historical/future flags."""
        today_vn = datetime.now(ZoneInfo(settings.APP_TIMEZONE)).date()
        target = requested_date or today_vn
        return target, target < today_vn, target > today_vn

    def evaluate_candidates(
        self,
        candidates: list[ApplicabilityCandidate],
        *,
        requested_date: date | None = None,
        allow_future_preview: bool = False,
    ) -> ApplicabilityResult:
        """Select applicable versions without inferring implicit contract override precedence."""
        tz = ZoneInfo(settings.APP_TIMEZONE)
        gov_date, is_historical, is_future = self.resolve_governing_date_vn(requested_date)
        future_preview = is_future and allow_future_preview
        eligible: list[ApplicabilityCandidate] = []

        for c in candidates:
            if not self._is_status_eligible(
                c.status,
                is_historical=is_historical,
                is_future_preview=future_preview,
            ):
                continue

            eff_from = self._to_vn_date(c.effective_from, tz)
            eff_to = self._to_vn_date(c.effective_to, tz) if c.effective_to else None
            if eff_from <= gov_date and (eff_to is None or gov_date <= eff_to):
                eligible.append(c)

        tiers = {c.authority_tier for c in eligible if c.authority_tier != AuthorityTier.STAFF_NOTE}
        non_note = [c for c in eligible if c.authority_tier != AuthorityTier.STAFF_NOTE]
        multiple_same_scope = len(non_note) > 1
        contract_vs_policy = (
            AuthorityTier.CUSTOMER_CONTRACT in tiers and AuthorityTier.POLICY in tiers
        )
        has_conflict = contract_vs_policy or multiple_same_scope
        hold_reason = (
            "DAT 05 Hold: Phát hiện hiệu lực chồng lấn hoặc tương tác hợp đồng-chính sách "
            "chưa có quy tắc ưu tiên được phê duyệt; cần chuyển chủ sở hữu chính sách."
            if has_conflict
            else None
        )
        return ApplicabilityResult(
            governing_date=gov_date,
            timezone=settings.APP_TIMEZONE,
            is_historical=is_historical,
            is_future_preview=future_preview,
            applicable_version_ids=[c.version_id for c in non_note],
            has_conflict=has_conflict,
            hold_reason=hold_reason,
        )

    def evaluate_policy_gate(
        self,
        candidates: list[ApplicabilityCandidate],
        *,
        requested_date: date | None = None,
        allow_future_preview: bool = False,
        critical_fields: list[CriticalFieldItem] | None = None,
        snapshot_age_hours: float | None = None,
        is_snapshot_stale: bool = False,
    ) -> PolicyGateDecision:
        """Evaluate Layer 2 deterministic applicability, conflict hold, and critical fields."""
        if requested_date is None:
            today_vn = datetime.now(ZoneInfo(settings.APP_TIMEZONE)).date()
            return PolicyGateDecision(
                governing_date=today_vn,
                timezone=settings.APP_TIMEZONE,
                is_historical=False,
                is_future_preview=False,
                applicable_version_ids=(),
                has_conflict=False,
                can_proceed=False,
                hold_reason=(
                    "OPS 03 / DAT 04 Hold: Thiếu ngày chi phối (requested_date=None); "
                    "không thể xác định phiên bản chính sách áp dụng."
                ),
                critical_fields=(),
                snapshot_age_hours=snapshot_age_hours,
                is_snapshot_stale=is_snapshot_stale,
            )

        applicability = self.evaluate_candidates(
            candidates,
            requested_date=requested_date,
            allow_future_preview=allow_future_preview,
        )
        applicable_ids = tuple(applicability.applicable_version_ids)
        applicable_set = set(applicable_ids)

        filtered_fields: tuple[CriticalFieldItem, ...] = ()
        if critical_fields and applicable_set:
            filtered_fields = tuple(
                cf
                for cf in critical_fields
                if self._is_status_eligible(
                    cf.status,
                    is_historical=applicability.is_historical,
                    is_future_preview=applicability.is_future_preview,
                )
                and (
                    cf.policy_version_id in applicable_set
                    or cf.document_version_id in applicable_set
                )
            )

        hold_reason = applicability.hold_reason
        if not applicability.has_conflict and not applicable_ids:
            hold_reason = (
                "DAT 04 Hold: Không tìm thấy phiên bản chính sách hiệu lực cho ngày chi phối; "
                "cần chuyển chủ sở hữu chính sách."
            )

        return PolicyGateDecision(
            governing_date=applicability.governing_date,
            timezone=applicability.timezone,
            is_historical=applicability.is_historical,
            is_future_preview=applicability.is_future_preview,
            applicable_version_ids=applicable_ids,
            has_conflict=applicability.has_conflict,
            can_proceed=bool(applicable_ids) and not applicability.has_conflict,
            hold_reason=hold_reason,
            critical_fields=filtered_fields,
            snapshot_age_hours=snapshot_age_hours,
            is_snapshot_stale=is_snapshot_stale,
        )

    def _to_vn_date(self, dt: datetime, tz: ZoneInfo) -> date:
        localized = dt.astimezone(tz) if dt.tzinfo is not None else dt.replace(tzinfo=tz)
        return localized.date()

    def _is_status_eligible(
        self,
        status: PolicyLifecycleStatus,
        *,
        is_historical: bool,
        is_future_preview: bool,
    ) -> bool:
        if status in {
            PolicyLifecycleStatus.DRAFT,
            PolicyLifecycleStatus.OWNER_REVIEWED,
            PolicyLifecycleStatus.APPROVED,
            PolicyLifecycleStatus.WITHDRAWN,
            PolicyLifecycleStatus.QUARANTINED,
            PolicyLifecycleStatus.FEEDBACK_CANDIDATE,
        }:
            return False
        if status == PolicyLifecycleStatus.SCHEDULED and not is_future_preview:
            return False
        if status == PolicyLifecycleStatus.SUPERSEDED and not is_historical:
            return False
        return True

    def evaluate_numeric_threshold(
        self, operator: ComparisonOperator, actual: Decimal, target: str
    ) -> bool:
        """Compute threshold checks deterministically in Python instead of in the LLM."""
        if operator == ComparisonOperator.REQUIRED:
            if isinstance(actual, bool):
                return False
            if isinstance(actual, Decimal):
                return actual.is_finite()
            return bool(str(actual).strip())
        if operator == ComparisonOperator.IN:
            sep = ";" if ";" in target else ","
            items = [part.strip() for part in target.split(sep) if part.strip()]
            if not items:
                return False
            parsed_targets: set[Decimal] = set()
            for item in items:
                try:
                    parsed_targets.add(Decimal(item))
                except InvalidOperation:
                    return False
            return actual in parsed_targets
        if operator == ComparisonOperator.BETWEEN:
            low_s, high_s = [part.strip() for part in target.split(";", maxsplit=1)]
            return Decimal(low_s) <= actual <= Decimal(high_s)
        bound = Decimal(target.strip())
        comparators = {
            ComparisonOperator.LE: actual <= bound,
            ComparisonOperator.LT: actual < bound,
            ComparisonOperator.GE: actual >= bound,
            ComparisonOperator.GT: actual > bound,
            ComparisonOperator.EQ: actual == bound,
        }
        return comparators.get(operator, False)

    async def list_authority_entries(self, db: AsyncSession) -> list[AuthorityEntryResponse]:
        """Return configured 5-tier authority hierarchy rows."""
        rows = (await db.execute(select(AuthorityEntry))).scalars().all()
        return [
            AuthorityEntryResponse(
                id=row.id,
                authority_tier=AuthorityTier(row.authority_tier),
                policy_family=PolicyFamily(row.policy_family),
                owner_name=row.owner_name,
                owner_role=row.owner_role,
                backup_owner=row.backup_owner,
                escalation_sla_hours=row.escalation_sla_hours,
            )
            for row in rows
        ]

    async def list_critical_fields(
        self,
        db: AsyncSession,
        user: AuthenticatedUser,
        policy_version_id: str,
        *,
        allow_historical: bool = False,
    ) -> list[CriticalFieldItem]:
        """Fetch deterministic structured critical fields guarded by audience & lifecycle RBAC."""
        rows = (
            await db.execute(
                select(CriticalField).where(
                    CriticalField.policy_version_id == policy_version_id,
                    CriticalField.status != PolicyLifecycleStatus.WITHDRAWN.value,
                    CriticalField.is_tombstoned.is_(False),
                )
            )
        ).scalars().all()

        is_reader_only = not bool(user.roles & _PRIVILEGED_POLICY_ROLES)
        allowed_reader_statuses = {PolicyLifecycleStatus.EFFECTIVE.value}
        if allow_historical:
            allowed_reader_statuses.add(PolicyLifecycleStatus.SUPERSEDED.value)

        visible_rows: list[CriticalField] = []
        for r in rows:
            audiences = [a.strip() for a in r.audience.split(",") if a.strip()]
            if not check_policy_audience(user, audiences):
                continue
            if is_reader_only and r.status not in allowed_reader_statuses:
                continue
            visible_rows.append(r)

        return [
            CriticalFieldItem(
                field_id=r.id,
                policy_id=r.policy_id,
                policy_version_id=r.policy_version_id,
                document_version_id=r.document_version_id,
                field_name=r.field_name,
                field_type=CriticalFieldType(r.field_type),
                operator=ComparisonOperator(r.operator),
                value=r.value,
                unit=r.unit,
                currency=r.currency,
                approval_role=r.approval_role,
                time_limit=r.time_limit,
                exception_condition=r.exception_condition,
                required_documents=(
                    [d.strip() for d in r.required_documents.split(";") if d.strip()]
                    if r.required_documents
                    else []
                ),
                source_clause=r.source_clause,
                status=PolicyLifecycleStatus(r.status),
            )
            for r in visible_rows
        ]
