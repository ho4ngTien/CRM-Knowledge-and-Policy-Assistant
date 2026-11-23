"""
legacy/tests/test_phase1.py
Kiểm thử tự động cho Giai đoạn 1 (Nền tảng kiến trúc, Cấu hình và Hợp đồng tích hợp):
- Kiểm tra legacy/s4/config.py
- Kiểm tra NullEvidenceProvider
- Kiểm tra MockLLMClient (chạy offline)
- Kiểm tra Database Schema, Safe Migration, và Validation
"""

import pytest
import sqlite3
import logging
from unittest.mock import patch
from legacy.s4 import config
from legacy.s4.services.evidence_provider import EvidenceProvider, NullEvidenceProvider
from legacy.s4.services.llm_client import LLMClient, MockLLMClient
from legacy.s4.services.database import (
    init_database,
    get_connection,
    save_feedback,
    save_referral,
    save_hold_log,
    get_recent_feedbacks,
    get_recent_referrals,
    get_recent_hold_logs,
    VALID_FEEDBACK_TYPES
)


class TestConfig:
    """Kiểm tra các thông số cấu hình và giới hạn an toàn trong legacy/s4/config.py."""

    def test_token_limits(self):
        assert config.MAX_LLM_CALLS_PER_PACKAGE == 2
        assert config.MAX_INPUT_TOKENS == 6000
        assert config.MAX_OUTPUT_TOKENS == 900

    def test_explanation_word_limits(self):
        assert config.EXPLANATION_MIN_WORDS == 100
        assert config.EXPLANATION_MAX_WORDS == 250
        assert config.EXPLANATION_MIN_WORDS < config.EXPLANATION_MAX_WORDS

    def test_versions_defined(self):
        assert isinstance(config.PROMPT_VERSION, str)
        assert len(config.PROMPT_VERSION) > 0
        assert isinstance(config.CONFIG_VERSION, str)
        assert len(config.CONFIG_VERSION) > 0


class TestEvidenceProvider:
    """Kiểm tra EvidenceProvider và NullEvidenceProvider (Adapter cho S3)."""

    def test_null_evidence_provider_inheritance(self):
        provider = NullEvidenceProvider()
        assert isinstance(provider, EvidenceProvider)

    def test_null_evidence_provider_returns_empty(self):
        provider = NullEvidenceProvider()
        citations = provider.retrieve_evidence("Khách hàng có được mở thẻ không?")
        assert citations == []
        assert len(citations) == 0


class TestMockLLMClient:
    """Kiểm tra MockLLMClient chạy hoàn toàn offline."""

    def test_mock_llm_client_offline_generation(self):
        mock_response = '{"status": "HOLD", "reason": "Testing offline"}'
        client = MockLLMClient(predefined_response=mock_response)
        assert isinstance(client, LLMClient)

        result = client.generate(
            prompt="Câu hỏi test",
            system_prompt="System prompt test",
            max_tokens=config.MAX_OUTPUT_TOKENS
        )
        assert result == mock_response
        assert client.call_count == 1
        assert client.last_max_tokens == 900
        assert client.last_prompt == "Câu hỏi test"
        assert client.last_system_prompt == "System prompt test"


class TestDatabaseSchemaAndValidation:
    """Kiểm tra cấu trúc Database, migration an toàn và hàm validate."""

    @pytest.fixture(autouse=True)
    def setup_db(self):
        init_database()

    def test_database_columns_after_init(self):
        with get_connection() as conn:
            # Kiểm tra bảng feedback
            fb_cols = [r["name"] for r in conn.execute("PRAGMA table_info(feedback)").fetchall()]
            for expected in ["id", "question", "feedback_type", "comment", "is_helpful", "flag_missing_exception", "flag_unfounded_claim", "created_at"]:
                assert expected in fb_cols, f"Thiếu cột {expected} trong feedback"

            # Kiểm tra bảng referrals
            ref_cols = [r["name"] for r in conn.execute("PRAGMA table_info(referrals)").fetchall()]
            for expected in ["id", "question", "reason", "policy_owner", "status", "created_at"]:
                assert expected in ref_cols, f"Thiếu cột {expected} trong referrals"

            # Kiểm tra bảng hold_logs
            hold_cols = [r["name"] for r in conn.execute("PRAGMA table_info(hold_logs)").fetchall()]
            for expected in ["id", "question", "reason_code", "reason_text", "created_at"]:
                assert expected in hold_cols, f"Thiếu cột {expected} trong hold_logs"

    def test_save_feedback_valid_and_reject_invalid_types(self):
        # 1. Từ chối loại feedback không hợp lệ
        invalid_saved = save_feedback("Câu hỏi test", "Tùy tiện bịa loại lỗi")
        assert invalid_saved is False

        # 2. Chấp nhận các loại feedback hợp lệ với cờ và mức độ hữu ích
        for fb_type in VALID_FEEDBACK_TYPES:
            saved = save_feedback(
                question="Câu hỏi kiểm thử feedback",
                feedback_type=fb_type,
                comment=f"Góp ý chi tiết cho {fb_type}",
                is_helpful=False,
                flag_missing_exception=True,
                flag_unfounded_claim=False
            )
            assert saved is True

        # Đọc lại và xác minh dữ liệu
        feedbacks = get_recent_feedbacks(limit=5)
        assert len(feedbacks) > 0
        latest = feedbacks[0]
        assert latest["is_helpful"] == 0
        assert latest["flag_missing_exception"] == 1
        assert latest["flag_unfounded_claim"] == 0

    def test_save_referral_with_status_and_read_back(self):
        saved = save_referral(
            question="Xin cấp hạn mức thẻ tín dụng vượt khung",
            reason="Khách hàng doanh nghiệp lớn",
            policy_owner="Khối Khách hàng Doanh nghiệp",
            status="PENDING"
        )
        assert saved is True

        referrals = get_recent_referrals(limit=1)
        assert len(referrals) > 0
        assert referrals[0]["status"] == "PENDING"
        assert referrals[0]["policy_owner"] == "Khối Khách hàng Doanh nghiệp"

    def test_save_hold_log_with_reason_code_and_read_back(self):
        saved = save_hold_log(
            question="Quy định miễn phí bảo lãnh",
            reason="Không tìm thấy văn bản quy định",
            reason_code="HOLD_NO_EVIDENCE"
        )
        assert saved is True

        logs = get_recent_hold_logs(limit=1)
        assert len(logs) > 0
        assert logs[0]["reason_code"] == "HOLD_NO_EVIDENCE"
        assert logs[0]["reason_text"] == "Không tìm thấy văn bản quy định"

    def test_database_write_failure_simulation_and_no_question_in_logs(self, caplog):
        """Mô phỏng lỗi ghi DB: hàm trả về False rõ ràng, ghi log lỗi không chứa câu hỏi gốc (Fail Visibly)."""
        secret_question = "CÂU_HỎI_BÍ_MẬT_KHÔNG_ĐƯỢC_LỘ_TRONG_LOG_123456"
        
        class FailingConnectionContext:
            def __enter__(self):
                return self
            def __exit__(self, exc_type, exc_val, exc_tb):
                return False
            def execute(self, *args, **kwargs):
                raise sqlite3.OperationalError("database is locked")

        with patch("legacy.s4.services.database.get_connection", return_value=FailingConnectionContext()):
            with caplog.at_level(logging.ERROR):
                fb_ok = save_feedback(secret_question, "Missing Source", "comment")
                ref_ok = save_referral(secret_question, "reason", "policy_owner")
                hold_ok = save_hold_log(secret_question, "reason", "HOLD_NO_EVIDENCE")

                assert fb_ok is False
                assert ref_ok is False
                assert hold_ok is False

                # Kiểm tra log ghi lỗi nhưng KHÔNG chứa nội dung câu hỏi gốc
                log_text = caplog.text
                assert secret_question not in log_text
                assert "OperationalError" in log_text

