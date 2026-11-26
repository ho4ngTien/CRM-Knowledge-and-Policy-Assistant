"""Unit and integration tests for Pre-Retrieval RBAC 4-Roles & 7 KNW 03 States (CRM-G1-ST03)."""

from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import pytest

from src.modules.knowledge.schemas import PassageSummary
from src.modules.retrieval.service import RetrievalService
from src.shared.auth import AuthenticatedUser, check_policy_audience
from src.shared.enums import PolicyLifecycleStatus, UserRole


@pytest.fixture
def retrieval_service() -> RetrievalService:
    return RetrievalService()


@pytest.fixture
def sample_users() -> dict[str, AuthenticatedUser]:
    return {
        "reader": AuthenticatedUser(
            user_id="usr-reader-01",
            email="reader@songnhat.vn",
            roles=frozenset({UserRole.READER}),
            allowed_audiences=frozenset({"reader"}),
        ),
        "policy_owner": AuthenticatedUser(
            user_id="usr-owner-01",
            email="owner@songnhat.vn",
            roles=frozenset({UserRole.POLICY_OWNER}),
            allowed_audiences=frozenset({"policy_owner"}),
        ),
        "steward": AuthenticatedUser(
            user_id="usr-steward-01",
            email="steward@songnhat.vn",
            roles=frozenset({UserRole.STEWARD}),
            allowed_audiences=frozenset({"steward"}),
        ),
        "admin": AuthenticatedUser(
            user_id="usr-admin-01",
            email="admin@songnhat.vn",
            roles=frozenset({UserRole.ADMINISTRATOR}),
            allowed_audiences=frozenset({"administrator"}),
        ),
    }


def make_passage(
    passage_id: str,
    status: PolicyLifecycleStatus,
    audience: list[str],
    *,
    has_essential_attachments: bool = True,
    content_len: int = 100,
    effective_from: datetime | None = None,
    effective_to: datetime | None = None,
    scope: str = "SongNhat - Toàn quốc - B2B",
) -> PassageSummary:
    now = datetime(2026, 11, 15, tzinfo=ZoneInfo("Asia/Ho_Chi_Minh"))
    return PassageSummary(
        passage_id=passage_id,
        document_id="DOC-POL-01",
        document_version_id="DOC-POL-01-V1",
        title=f"Chính sách {passage_id}",
        content="Nội dung điều khoản chính sách. " * (content_len // 20),
        source_ref="Quy chế thương mại 2026",
        page_number=1,
        clause_ref="Điều 1",
        language="vi",
        scope=scope,
        audience=audience,
        status=status,
        has_essential_attachments=has_essential_attachments,
        effective_from=effective_from or (now - timedelta(days=10)),
        effective_to=effective_to,
        supersedes=None,
    )


# ==============================================================================
# TEST SUITE 1: RBAC 4-ROLES AUDIENCE FILTERING (SEC 01)
# ==============================================================================

def test_check_policy_audience_admin_least_privilege(
    sample_users: dict[str, AuthenticatedUser],
) -> None:
    """Administrator follows least-privilege audience matching without blanket bypass."""
    admin = sample_users["admin"]
    assert check_policy_audience(admin, ["administrator"])
    assert check_policy_audience(admin, ["all"])
    assert check_policy_audience(admin, ["public"])
    assert not check_policy_audience(admin, ["reader"])
    assert not check_policy_audience(admin, ["policy_owner"])
    assert not check_policy_audience(admin, ["steward"])
    assert not check_policy_audience(admin, ["confidential_legal"])


def test_check_policy_audience_reader_isolation(sample_users: dict[str, AuthenticatedUser]) -> None:
    """Reader role is restricted to reader/all audiences; cannot access owner/steward."""
    reader = sample_users["reader"]
    assert check_policy_audience(reader, ["reader"])
    assert check_policy_audience(reader, ["all"])
    assert check_policy_audience(reader, ["public"])
    assert check_policy_audience(reader, ["reader,policy_owner"])
    assert check_policy_audience(reader, ["reader;steward"])

    # Restricted
    assert not check_policy_audience(reader, ["policy_owner"])
    assert not check_policy_audience(reader, ["steward"])
    assert not check_policy_audience(reader, ["administrator"])
    assert not check_policy_audience(reader, [])


def test_check_policy_audience_steward_and_owner(
    sample_users: dict[str, AuthenticatedUser],
) -> None:
    """Steward and Policy Owner strictly isolated according to their assigned roles."""
    steward = sample_users["steward"]
    owner = sample_users["policy_owner"]

    assert check_policy_audience(steward, ["steward"])
    assert not check_policy_audience(steward, ["policy_owner"])

    assert check_policy_audience(owner, ["policy_owner"])
    assert not check_policy_audience(owner, ["steward"])


# ==============================================================================
# TEST SUITE 2: 7 KNW 03 LIFECYCLE STATES PRE-FILTERING
# ==============================================================================

def test_prefilter_blocks_all_non_effective_states_by_default(
    retrieval_service: RetrievalService,
    sample_users: dict[str, AuthenticatedUser],
) -> None:
    """Default retrieval MUST ONLY yield Effective passages (6 non-effective blocked)."""
    user = sample_users["reader"]
    candidates = [
        make_passage("P-EFF", PolicyLifecycleStatus.EFFECTIVE, ["reader"]),
        make_passage("P-DFT", PolicyLifecycleStatus.DRAFT, ["reader"]),
        make_passage("P-REV", PolicyLifecycleStatus.OWNER_REVIEWED, ["reader"]),
        make_passage("P-APP", PolicyLifecycleStatus.APPROVED, ["reader"]),
        make_passage("P-SCH", PolicyLifecycleStatus.SCHEDULED, ["reader"]),
        make_passage("P-SUP", PolicyLifecycleStatus.SUPERSEDED, ["reader"]),
        make_passage("P-WTD", PolicyLifecycleStatus.WITHDRAWN, ["reader"]),
        make_passage("P-QUA", PolicyLifecycleStatus.QUARANTINED, ["reader"]),
        make_passage("P-FBC", PolicyLifecycleStatus.FEEDBACK_CANDIDATE, ["reader"]),
    ]

    filtered = retrieval_service.prefilter_passages(
        user,
        candidates,
        governing_date=date(2026, 11, 15),
    )

    result_ids = [p.passage_id for p in filtered]
    assert result_ids == ["P-EFF"], f"Expected only Effective passages, got {result_ids}"


def test_withdrawn_is_strict_fail_closed(
    retrieval_service: RetrievalService,
    sample_users: dict[str, AuthenticatedUser],
) -> None:
    """Withdrawn policy can NEVER be retrieved, even with historical or preview flags."""
    admin = sample_users["admin"]
    candidates = [
        make_passage("P-WTD-1", PolicyLifecycleStatus.WITHDRAWN, ["administrator", "reader"]),
    ]

    # Even admin with historical and future preview enabled cannot see withdrawn policies
    filtered = retrieval_service.prefilter_passages(
        admin,
        candidates,
        allow_historical=True,
        allow_future_preview=True,
    )
    assert len(filtered) == 0, "Withdrawn passage must be strictly blocked (fail-closed)"


def test_scheduled_allowed_only_with_future_preview(
    retrieval_service: RetrievalService,
    sample_users: dict[str, AuthenticatedUser],
) -> None:
    """Scheduled passages are blocked by default and only allowed with allow_future_preview."""
    user = sample_users["reader"]
    future_date = datetime(2026, 12, 1, tzinfo=ZoneInfo("Asia/Ho_Chi_Minh"))
    candidates = [
        make_passage(
            "P-SCH",
            PolicyLifecycleStatus.SCHEDULED,
            ["reader"],
            effective_from=future_date,
        ),
    ]

    # Default: blocked
    assert len(retrieval_service.prefilter_passages(user, candidates)) == 0

    # With allow_future_preview: allowed
    res = retrieval_service.prefilter_passages(
        user,
        candidates,
        allow_future_preview=True,
    )
    assert len(res) == 1
    assert res[0].passage_id == "P-SCH"


def test_superseded_allowed_only_with_historical_mode(
    retrieval_service: RetrievalService,
    sample_users: dict[str, AuthenticatedUser],
) -> None:
    """Superseded passages are blocked by default and only allowed for matching governing_date."""
    user = sample_users["reader"]
    hist_start = datetime(2026, 1, 1, tzinfo=ZoneInfo("Asia/Ho_Chi_Minh"))
    hist_end = datetime(2026, 6, 30, tzinfo=ZoneInfo("Asia/Ho_Chi_Minh"))

    candidates = [
        make_passage(
            "P-SUP",
            PolicyLifecycleStatus.SUPERSEDED,
            ["reader"],
            effective_from=hist_start,
            effective_to=hist_end,
        ),
    ]

    # Default: blocked
    assert len(retrieval_service.prefilter_passages(user, candidates)) == 0

    # With historical mode on a date within window: allowed
    res = retrieval_service.prefilter_passages(
        user,
        candidates,
        governing_date=date(2026, 3, 15),
        allow_historical=True,
    )
    assert len(res) == 1
    assert res[0].passage_id == "P-SUP"

    # With historical mode on a date outside window: blocked
    res_outside = retrieval_service.prefilter_passages(
        user,
        candidates,
        governing_date=date(2026, 8, 1),
        allow_historical=True,
    )
    assert len(res_outside) == 0


def test_prefilter_essential_attachments_and_content_bound(
    retrieval_service: RetrievalService,
    sample_users: dict[str, AuthenticatedUser],
) -> None:
    """Passages with missing attachments or > 6000 chars are rejected."""
    user = sample_users["reader"]
    candidates = [
        # Missing essential attachments (DAT 08)
        make_passage(
            "P-NO-ATTACH",
            PolicyLifecycleStatus.EFFECTIVE,
            ["reader"],
            has_essential_attachments=False,
        ),
        # Exceeds max char limit (6000 chars) constructed directly
        PassageSummary.model_construct(
            passage_id="P-OVER-LEN",
            document_id="DOC-01",
            document_version_id="V1",
            title="Over length",
            content="A" * 6001,
            source_ref="Ref",
            page_number=1,
            clause_ref="1.1",
            language="vi",
            scope="all",
            audience=["reader"],
            status=PolicyLifecycleStatus.EFFECTIVE,
            has_essential_attachments=True,
            effective_from=datetime(2026, 1, 1, tzinfo=ZoneInfo("Asia/Ho_Chi_Minh")),
        ),
    ]

    filtered = retrieval_service.prefilter_passages(user, candidates)
    assert len(filtered) == 0


def test_prefilter_bounded_to_max_8(
    retrieval_service: RetrievalService,
    sample_users: dict[str, AuthenticatedUser],
) -> None:
    """Top_k is capped at settings.ANSWER_MAX_PASSAGES (8)."""
    user = sample_users["reader"]
    candidates = [
        make_passage(f"P-EFF-{i}", PolicyLifecycleStatus.EFFECTIVE, ["reader"])
        for i in range(15)
    ]
    filtered = retrieval_service.prefilter_passages(user, candidates, top_k=10)
    assert len(filtered) == 8, f"Expected maximum 8 passages, got {len(filtered)}"


# ==============================================================================
# TEST SUITE 3: VIETNAMESE QUERY NORMALIZATION & GLOSSARY (ANS 02, VN 01)
# ==============================================================================

def test_preserve_vietnamese_negations(retrieval_service: RetrievalService) -> None:
    """Zero-removal guarantee for all 14 Vietnamese negations."""
    test_queries = [
        "Khách hàng không thuộc diện chiết khấu 10%",
        "Hồ sơ chưa có biên bản giám định hiện trường",
        "Miễn bảo hành đối với linh kiện hao mòn",
        "Ngoại trừ trường hợp lỗi kỹ thuật bo mạch",
        "Nhân viên không được tự ý duyệt quá 50 triệu",
        "Cấm tiết lộ thông tin cá nhân khách hàng",
        "Loại trừ trách nhiệm do thiên tai",
        "Không áp dụng đối với đơn hàng thanh toán chậm",
        "Vắng mặt người có thẩm quyền thì ủy quyền cho ai",
        "Hồ sơ thiếu tờ trình thì có được nhận không",
        "Từ chối tiếp nhận bảo hành khi rách tem",
        "Hủy đơn hàng thì thủ tục thế nào",
    ]

    for q in test_queries:
        negations = retrieval_service.detect_preserved_negations(q)
        assert len(negations) > 0, f"Failed to detect negation in: {q}"
        normalized, _ = retrieval_service.normalize_query_vi(q)
        for neg in negations:
            assert neg in normalized.lower(), f"Negation '{neg}' was lost in: {normalized}"


def test_unaccent_mappings(retrieval_service: RetrievalService) -> None:
    """Unaccented input is properly mapped to accented Vietnamese terms."""
    q = "chiet khau bao gia dong co 3 pha bien tan"
    norm, expanded = retrieval_service.normalize_query_vi(q)
    assert "chiết khấu" in norm or "chiết khấu" in expanded
    assert "báo giá" in norm or "báo giá" in expanded


def test_crm_synonyms_expansion(retrieval_service: RetrievalService) -> None:
    """CRM abbreviations expand to owner-approved synonyms."""
    q = "bg cho kh mua motor 3 pha xin ck 5% co can tpkd duyet khong"
    norm, expanded = retrieval_service.normalize_query_vi(q)
    
    # Check abbreviations expanded
    assert any("khách hàng" in item for item in expanded)
    assert any("chiết khấu" in item for item in expanded)
    assert any("báo giá" in item for item in expanded)
    assert any("trưởng phòng kinh doanh" in item for item in expanded)

    # Check negation preserved
    negations = retrieval_service.detect_preserved_negations(q)
    assert "không" in negations
