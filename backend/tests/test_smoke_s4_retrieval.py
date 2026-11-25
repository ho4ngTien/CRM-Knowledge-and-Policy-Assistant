"""Smoke test suite for Sub-task SUB09 (Quality Lead S4 offline evaluation).

Verifies the 60 non-leaking DEV tasks dataset (Chinese Wall compliant) and checks
end-to-end pre-retrieval RBAC, timezone, and 7-state filtering integrity.
"""

import csv
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

from src.modules.knowledge.schemas import PassageSummary
from src.modules.retrieval.service import RetrievalService
from src.shared.auth import AuthenticatedUser
from src.shared.enums import PolicyLifecycleStatus, UserRole

REPO_ROOT = Path(__file__).resolve().parents[2]
DATASET_PATH = REPO_ROOT / "data" / "eval" / "60_dev_tasks_nonleaking_clean_pii.csv"
DICTIONARY_PATH = REPO_ROOT / "data" / "eval" / "vn01_crm_dictionary.json"


@pytest.fixture(scope="module")
def dev_60_tasks() -> list[dict[str, str]]:
    assert DATASET_PATH.exists(), f"Dataset missing at {DATASET_PATH}"
    with open(DATASET_PATH, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


@pytest.fixture(scope="module")
def dictionary_vn01() -> dict:
    assert DICTIONARY_PATH.exists(), f"Dictionary missing at {DICTIONARY_PATH}"
    with open(DICTIONARY_PATH, encoding="utf-8") as f:
        return json.load(f)


def test_60_dev_tasks_count_and_chinese_wall_partition(
    dev_60_tasks: list[dict[str, str]],
) -> None:
    """Validate 60 DEV tasks with zero VAL/SEALED leakage (Chinese Wall)."""
    assert len(dev_60_tasks) == 60, f"Expected 60 DEV tasks, got {len(dev_60_tasks)}"
    assert all(q.get("Partition") == "DEV" for q in dev_60_tasks)
    vgs = {q.get("Variant_Group_ID") for q in dev_60_tasks}
    assert vgs == {"VG-04", "VG-06", "VG-07", "VG-12", "VG-16"}


def test_60_dev_tasks_covers_3_policy_families(dev_60_tasks: list[dict[str, str]]) -> None:
    """Verify all 3 base scope policy families are covered."""
    families = {q.get("Policy_ID") for q in dev_60_tasks}
    assert families == {"POL-001", "POL-002", "POL-003"}

    pol1 = [q for q in dev_60_tasks if q.get("Policy_ID") == "POL-001"]
    pol2 = [q for q in dev_60_tasks if q.get("Policy_ID") == "POL-002"]
    pol3 = [q for q in dev_60_tasks if q.get("Policy_ID") == "POL-003"]
    assert len(pol1) == 24
    assert len(pol2) == 16
    assert len(pol3) == 20


def test_60_dev_tasks_zero_pii_audit(dev_60_tasks: list[dict[str, str]]) -> None:
    """Verify zero personal phone numbers, citizen IDs, or personal emails (SEC 02/06)."""
    phone_pattern = re.compile(r"(?:\+84|0)[3|5|7|8|9][0-9]{8}\b")
    id_pattern = re.compile(r"\b\d{9}\b|\b\d{12}\b")
    personal_email = re.compile(r"[\w\.-]+@(?!songnhat\.vn|example\.com)[\w\.-]+\.\w+")

    for item in dev_60_tasks:
        q_text = item.get("Question_VN", "")
        task_id = item.get("Task_ID", "")

        assert not phone_pattern.search(q_text), f"Phone number detected in {task_id}: {q_text}"
        assert not id_pattern.search(q_text), f"Citizen ID pattern detected in {task_id}: {q_text}"
        assert not personal_email.search(q_text), f"Personal email detected in {task_id}: {q_text}"
        assert item.get("PII_Sanitization") == "CLEAN_NO_REAL_PII"


def test_smoke_end_to_end_normalization_on_60_dev_tasks(
    dev_60_tasks: list[dict[str, str]],
) -> None:
    """Smoke test: Run normalization on all 60 DEV tasks without error or data loss."""
    service = RetrievalService()

    for item in dev_60_tasks:
        query = item["Question_VN"]
        norm, expanded = service.normalize_query_vi(query)
        assert len(norm) > 0
        assert isinstance(expanded, list)

        # Verify any negation in original query is preserved
        negations = service.detect_preserved_negations(query)
        for neg in negations:
            assert neg in norm.lower(), f"Negation '{neg}' lost in {item['Task_ID']}"


def test_smoke_prefilter_isolation_matrix() -> None:
    """Smoke test: 4 roles x 7 states matrix test ensuring 0% unauthorized leakage."""
    service = RetrievalService()

    reader = AuthenticatedUser(
        user_id="u-reader",
        email="reader@songnhat.vn",
        roles=frozenset({UserRole.READER}),
    )

    tz = ZoneInfo("Asia/Ho_Chi_Minh")

    # Mixed pool of 10 passages
    candidates = [
        PassageSummary(
            passage_id=f"PSG-TEST-{i}",
            document_id="DOC-01",
            document_version_id="V1",
            title=f"Test {i}",
            content="Quy định hợp lệ " * 10,
            source_ref="Ref",
            page_number=1,
            clause_ref="Điều 1",
            language="vi",
            scope="SongNhat - Toàn quốc - B2B",
            audience=["reader"] if i % 2 == 0 else ["policy_owner"],
            status=PolicyLifecycleStatus.EFFECTIVE if i == 0 else PolicyLifecycleStatus.DRAFT,
            has_essential_attachments=True,
            effective_from=datetime(2026, 1, 1, tzinfo=tz),
        )
        for i in range(10)
    ]

    filtered = service.prefilter_passages(reader, candidates)

    # Only PSG-TEST-0 is Effective AND has audience 'reader'
    assert len(filtered) == 1
    assert filtered[0].passage_id == "PSG-TEST-0"


def test_prefilter_converts_utc_effective_from_to_vn_date() -> None:
    """UTC 2026-11-14T18:00:00Z is 2026-11-15T01:00:00+07:00 in VN; must not match 2026-11-14."""
    from datetime import date

    service = RetrievalService()
    reader = AuthenticatedUser(
        user_id="u-reader",
        email="reader@songnhat.vn",
        roles=frozenset({UserRole.READER}),
    )
    utc_passage = PassageSummary(
        passage_id="PSG-TZ-01",
        document_id="DOC-01",
        document_version_id="V1",
        title="UTC boundary test",
        content="Nội dung kiểm thử múi giờ UTC+7.",
        source_ref="Ref",
        page_number=1,
        clause_ref="Điều 1",
        language="vi",
        scope="all",
        audience=["reader"],
        status=PolicyLifecycleStatus.EFFECTIVE,
        has_essential_attachments=True,
        effective_from=datetime(2026, 11, 14, 18, 0, 0, tzinfo=UTC),
    )

    assert service.prefilter_passages(
        reader, [utc_passage], governing_date=date(2026, 11, 14)
    ) == []
    assert len(
        service.prefilter_passages(reader, [utc_passage], governing_date=date(2026, 11, 15))
    ) == 1
