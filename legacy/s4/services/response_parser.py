"""
legacy/s4/services/response_parser.py
Bộ phân tích đầu ra LLM nghiêm ngặt (CKPA-41).
Quy tắc:
1. Parse JSON bằng thư viện chuẩn (stdlib json), tuyệt đối không dùng regex "cứu" JSON hỏng.
2. Kiểm tra schema cố định: Bất kỳ khóa lạ, thiếu khóa, sai kiểu dữ liệu hoặc văn bản ngoài JSON
   đều bị từ chối với mã lỗi HoldReason.INVALID_LLM_FORMAT.
3. Không để LLM tự điền metadata (effective_date, scope, policy_owner). CODE sẽ lấy trực tiếp từ S3 chunks.
4. Tích hợp kiểm tra trích dẫn (verify_all_citations) và kiểm tra cấu trúc (validate_answer).
"""

import json
from typing import Dict, List, Optional, Tuple
from legacy.s4.models import (
    PolicyResponse,
    ResponseStatus,
    UncertaintyLevel,
    Citation,
    EvidenceChunk,
    validate_answer,
)
from legacy.s4.services.citation_verifier import verify_all_citations
from legacy.s4.services.hold_reasons import HoldReason, get_hold_info

# Tập hợp các trường hợp lệ trong JSON của LLM
ALLOWED_KEYS = {
    "status",
    "short_explanation",
    "required_information",
    "uncertainty_level",
    "citations",
    "hold_reason_code",
}

VALID_UNCERTAINTIES = {
    "CAO": UncertaintyLevel.CAO,
    "TRUNG_BINH": UncertaintyLevel.TRUNG_BINH,
    "THAP": UncertaintyLevel.THAP,
    "KHONG_XAC_DINH": UncertaintyLevel.KHONG_XAC_DINH,
}


def parse_llm_json_response(
    raw_response: str,
    question: str,
    evidence_chunks: List[EvidenceChunk]
) -> PolicyResponse:
    """
    Phân tích chuỗi đầu ra từ LLM theo schema chuẩn và liên kết với metadata từ S3.
    """
    cleaned = raw_response.strip()

    # 1. Kiểm tra văn bản thừa ngoài JSON
    if not (cleaned.startswith("{") and cleaned.endswith("}")):
        hold_info = get_hold_info(HoldReason.INVALID_LLM_FORMAT)
        return PolicyResponse(
            question=question,
            status=ResponseStatus.HOLD,
            uncertainty_level=UncertaintyLevel.KHONG_XAC_DINH,
            hold_reason_code=hold_info.code,
            hold_reason=f"{hold_info.message} (Phát hiện văn bản ngoài JSON hoặc định dạng không hợp lệ)",
            guidance=hold_info.guidance,
            citations=[]
        )

    # 2. Parse JSON
    try:
        data = json.loads(cleaned)
    except Exception:
        hold_info = get_hold_info(HoldReason.INVALID_LLM_FORMAT)
        return PolicyResponse(
            question=question,
            status=ResponseStatus.HOLD,
            uncertainty_level=UncertaintyLevel.KHONG_XAC_DINH,
            hold_reason_code=hold_info.code,
            hold_reason=f"{hold_info.message} (Lỗi cú pháp JSON)",
            guidance=hold_info.guidance,
            citations=[]
        )

    if not isinstance(data, dict):
        hold_info = get_hold_info(HoldReason.INVALID_LLM_FORMAT)
        return PolicyResponse(
            question=question,
            status=ResponseStatus.HOLD,
            uncertainty_level=UncertaintyLevel.KHONG_XAC_DINH,
            hold_reason_code=hold_info.code,
            hold_reason=f"{hold_info.message} (Đầu ra không phải JSON object)",
            guidance=hold_info.guidance,
            citations=[]
        )

    # 3. Kiểm tra khóa lạ (extra keys)
    extra_keys = set(data.keys()) - ALLOWED_KEYS
    if extra_keys:
        hold_info = get_hold_info(HoldReason.INVALID_LLM_FORMAT)
        return PolicyResponse(
            question=question,
            status=ResponseStatus.HOLD,
            uncertainty_level=UncertaintyLevel.KHONG_XAC_DINH,
            hold_reason_code=hold_info.code,
            hold_reason=f"{hold_info.message} (Phát hiện các trường lạ ngoài schema: {sorted(list(extra_keys))})",
            guidance=hold_info.guidance,
            citations=[]
        )

    # 4. Kiểm tra các trường bắt buộc phải có
    required_keys = {"status", "short_explanation", "required_information", "uncertainty_level", "citations"}
    missing_keys = required_keys - set(data.keys())
    if missing_keys:
        hold_info = get_hold_info(HoldReason.INVALID_LLM_FORMAT)
        return PolicyResponse(
            question=question,
            status=ResponseStatus.HOLD,
            uncertainty_level=UncertaintyLevel.KHONG_XAC_DINH,
            hold_reason_code=hold_info.code,
            hold_reason=f"{hold_info.message} (Thiếu các trường bắt buộc: {sorted(list(missing_keys))})",
            guidance=hold_info.guidance,
            citations=[]
        )

    # 5. Kiểm tra kiểu dữ liệu của các trường
    if not isinstance(data["short_explanation"], str) or not isinstance(data["required_information"], str):
        hold_info = get_hold_info(HoldReason.INVALID_LLM_FORMAT)
        return PolicyResponse(
            question=question,
            status=ResponseStatus.HOLD,
            uncertainty_level=UncertaintyLevel.KHONG_XAC_DINH,
            hold_reason_code=hold_info.code,
            hold_reason=f"{hold_info.message} (Sai kiểu dữ liệu trường chuỗi)",
            guidance=hold_info.guidance,
            citations=[]
        )

    if not isinstance(data["citations"], list):
        hold_info = get_hold_info(HoldReason.INVALID_LLM_FORMAT)
        return PolicyResponse(
            question=question,
            status=ResponseStatus.HOLD,
            uncertainty_level=UncertaintyLevel.KHONG_XAC_DINH,
            hold_reason_code=hold_info.code,
            hold_reason=f"{hold_info.message} (citations phải là danh sách)",
            guidance=hold_info.guidance,
            citations=[]
        )

    # 6. Kiểm tra uncertainty_level
    raw_uncertainty = str(data["uncertainty_level"]).strip()
    if raw_uncertainty not in VALID_UNCERTAINTIES:
        hold_info = get_hold_info(HoldReason.INVALID_LLM_FORMAT)
        return PolicyResponse(
            question=question,
            status=ResponseStatus.HOLD,
            uncertainty_level=UncertaintyLevel.KHONG_XAC_DINH,
            hold_reason_code=hold_info.code,
            hold_reason=f"{hold_info.message} (uncertainty_level không hợp lệ: '{raw_uncertainty}')",
            guidance=hold_info.guidance,
            citations=[]
        )
    uncertainty_level = VALID_UNCERTAINTIES[raw_uncertainty]

    # 7. Xử lý trường hợp LLM chủ động trả về tín hiệu HOLD
    status_str = str(data["status"]).strip().upper()
    if status_str == "HOLD":
        hold_code_str = str(data.get("hold_reason_code", "INSUFFICIENT_EVIDENCE")).strip()
        try:
            target_reason = HoldReason(hold_code_str)
        except ValueError:
            target_reason = HoldReason.INSUFFICIENT_EVIDENCE

        hold_info = get_hold_info(target_reason)
        return PolicyResponse(
            question=question,
            status=ResponseStatus.HOLD,
            uncertainty_level=UncertaintyLevel.KHONG_XAC_DINH,
            hold_reason_code=hold_info.code,
            hold_reason=hold_info.message,
            guidance=hold_info.guidance,
            citations=[]
        )

    if status_str != "SUCCESS":
        hold_info = get_hold_info(HoldReason.INVALID_LLM_FORMAT)
        return PolicyResponse(
            question=question,
            status=ResponseStatus.HOLD,
            uncertainty_level=UncertaintyLevel.KHONG_XAC_DINH,
            hold_reason_code=hold_info.code,
            hold_reason=f"{hold_info.message} (status không hợp lệ: '{status_str}')",
            guidance=hold_info.guidance,
            citations=[]
        )

    # 8. Xây dựng danh sách Citation từ chunk metadata của S3 (Task 3.1)
    chunk_map: Dict[str, EvidenceChunk] = {chunk.chunk_id: chunk for chunk in evidence_chunks}
    raw_citations: List[Citation] = []

    for cit_dict in data["citations"]:
        if not isinstance(cit_dict, dict) or "chunk_id" not in cit_dict or "verbatim_quote" not in cit_dict:
            hold_info = get_hold_info(HoldReason.INVALID_LLM_FORMAT)
            return PolicyResponse(
                question=question,
                status=ResponseStatus.HOLD,
                uncertainty_level=UncertaintyLevel.KHONG_XAC_DINH,
                hold_reason_code=hold_info.code,
                hold_reason=f"{hold_info.message} (Cấu trúc citation trong danh sách không đúng schema)",
                guidance=hold_info.guidance,
                citations=[]
            )

        cid = str(cit_dict["chunk_id"]).strip()
        vquote = str(cit_dict["verbatim_quote"])

        chunk = chunk_map.get(cid)
        if not chunk:
            # Chunk ID do LLM trả về không tồn tại trong các chunk được cấp
            continue

        citation = Citation(
            document_name=chunk.document_name,
            section=chunk.section,
            verbatim_quote=vquote,
            chunk_id=chunk.chunk_id,
            clause_code=chunk.clause_code,
            source_url=chunk.source_url,
            effective_date=chunk.effective_date
        )
        raw_citations.append(citation)

    # 9. Xác minh trích dẫn nguyên văn bằng code (verify_all_citations)
    verified_citations, rejections = verify_all_citations(raw_citations, evidence_chunks)
    if not verified_citations:
        hold_info = get_hold_info(HoldReason.CITATION_UNVERIFIED)
        rejection_detail = "; ".join(rejections) if rejections else "Không có trích dẫn hợp lệ"
        return PolicyResponse(
            question=question,
            status=ResponseStatus.HOLD,
            uncertainty_level=UncertaintyLevel.KHONG_XAC_DINH,
            hold_reason_code=hold_info.code,
            hold_reason=f"{hold_info.message} ({rejection_detail})",
            guidance=hold_info.guidance,
            citations=[]
        )

    # 10. Trích xuất metadata từ S3 chunk (Task 3.1)
    primary_chunk = evidence_chunks[0] if evidence_chunks else None
    effective_date = (
        (primary_chunk.effective_date if primary_chunk and primary_chunk.effective_date else None)
        or "Không xác định theo bằng chứng"
    )
    scope = (
        (primary_chunk.scope if primary_chunk and primary_chunk.scope else None)
        or "Không xác định theo bằng chứng"
    )
    policy_owner = (
        (primary_chunk.policy_owner if primary_chunk and primary_chunk.policy_owner else None)
        or "Không xác định theo bằng chứng"
    )

    response = PolicyResponse(
        question=question,
        status=ResponseStatus.SUCCESS,
        effective_date=effective_date,
        scope=scope,
        short_explanation=data["short_explanation"].strip(),
        required_information=data["required_information"].strip(),
        policy_owner=policy_owner,
        uncertainty_level=uncertainty_level,
        citations=verified_citations
    )

    # 11. Kiểm tra validation 7 trường (validate_answer)
    validation_errors = validate_answer(response)
    if validation_errors:
        hold_info = get_hold_info(HoldReason.INVALID_FIELDS)
        return PolicyResponse(
            question=question,
            status=ResponseStatus.HOLD,
            uncertainty_level=UncertaintyLevel.KHONG_XAC_DINH,
            hold_reason_code=hold_info.code,
            hold_reason=f"{hold_info.message} (Chi tiết: {'; '.join(validation_errors)})",
            guidance=hold_info.guidance,
            citations=[]
        )

    return response

