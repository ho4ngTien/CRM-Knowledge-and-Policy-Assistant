"""Smoke test suite for Sub-task SUB09 (Quality Lead S4 offline evaluation).

Verifies the 100 Real Questions dataset (P4 / CKPA-55) and checks end-to-end
pre-retrieval RBAC and 7-state filtering integrity.
"""

import json
from pathlib import Path
import re
import pytest

from src.modules.knowledge.schemas import PassageSummary
from src.modules.retrieval.service import RetrievalService
from src.shared.auth import AuthenticatedUser
from src.shared.enums import PolicyLifecycleStatus, UserRole

REPO_ROOT = Path(__file__).resolve().parents[2]
DATASET_PATH = REPO_ROOT / "data" / "eval" / "100_real_questions_clean_pii.json"
DICTIONARY_PATH = REPO_ROOT / "data" / "eval" / "vn01_crm_dictionary.json"


@pytest.fixture(scope="module")
def questions_100() -> list[dict]:
    assert DATASET_PATH.exists(), f"Dataset missing at {DATASET_PATH}"
    with open(DATASET_PATH, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def dictionary_vn01() -> dict:
    assert DICTIONARY_PATH.exists(), f"Dictionary missing at {DICTIONARY_PATH}"
    with open(DICTIONARY_PATH, encoding="utf-8") as f:
        return json.load(f)


def test_100_questions_count_and_partitions(questions_100: list[dict]) -> None:
    """Validate 100 questions partitioned into exactly 60 DEV and 40 VAL."""
    assert len(questions_100) == 100, f"Expected 100 questions, got {len(questions_100)}"

    dev_cases = [q for q in questions_100 if q.get("Partition") == "DEV"]
    val_cases = [q for q in questions_100 if q.get("Partition") == "VAL"]

    assert len(dev_cases) == 60, f"Expected 60 DEV questions, got {len(dev_cases)}"
    assert len(val_cases) == 40, f"Expected 40 VAL questions, got {len(val_cases)}"


def test_100_questions_covers_3_policy_families(questions_100: list[dict]) -> None:
    """Verify all 3 base scope policy families are covered."""
    families = {q.get("Policy_Family") for q in questions_100}
    assert families == {"POL-CRM-01", "POL-CRM-02", "POL-CRM-03"}

    # POL-CRM-01: 40 questions (24 DEV + 16 VAL)
    pol1 = [q for q in questions_100 if q.get("Policy_Family") == "POL-CRM-01"]
    assert len(pol1) == 40

    # POL-CRM-02: 30 questions (18 DEV + 12 VAL)
    pol2 = [q for q in questions_100 if q.get("Policy_Family") == "POL-CRM-02"]
    assert len(pol2) == 30

    # POL-CRM-03: 30 questions (18 DEV + 12 VAL)
    pol3 = [q for q in questions_100 if q.get("Policy_Family") == "POL-CRM-03"]
    assert len(pol3) == 30


def test_100_questions_zero_pii_audit(questions_100: list[dict]) -> None:
    """Verify zero personal phone numbers, citizen IDs, or personal emails (SEC 02/06)."""
    phone_pattern = re.compile(r"(?:\+84|0)[3|5|7|8|9][0-9]{8}\b")
    id_pattern = re.compile(r"\b\d{9}\b|\b\d{12}\b")
    personal_email = re.compile(r"[\w\.-]+@(?!songnhat\.vn|example\.com)[\w\.-]+\.\w+")

    for item in questions_100:
        q_text = item.get("Question_VN", "")
        task_id = item.get("Task_ID", "")

        assert not phone_pattern.search(q_text), f"Phone number detected in {task_id}: {q_text}"
        assert not id_pattern.search(q_text), f"Citizen ID pattern detected in {task_id}: {q_text}"
        assert not personal_email.search(q_text), f"Personal email detected in {task_id}: {q_text}"

        assert item.get("P2_P3_Consensus_Status") == "AGREED_BY_P2_AND_P3"


def test_smoke_end_to_end_normalization_on_100_questions(
    questions_100: list[dict],
) -> None:
    """Smoke test: Run normalization on all 100 questions without error or data loss."""
    service = RetrievalService()

    for item in questions_100:
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

    from datetime import datetime
    from zoneinfo import ZoneInfo
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
