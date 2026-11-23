"""
legacy/tests/conftest.py
Cấu hình kiểm thử dùng chung cho toàn bộ pytest suite:
- Tự động thiết lập TEST_DATABASE_PATH trỏ vào database tạm thời.
- Đảm bảo legacy/data/app.db THẬT không bao giờ bị ghi hoặc làm biến đổi khi chạy test.
"""

import os
import tempfile
from pathlib import Path
import pytest

# Thiết lập đường dẫn database tạm cho toàn bộ phiên chạy test ngay khi import
_TEST_DB_PATH = Path(tempfile.gettempdir()) / f"crm_assistant_pytest_{os.getpid()}.db"
os.environ["TEST_DATABASE_PATH"] = str(_TEST_DB_PATH)

from legacy.s4.services.database import init_database, get_connection


@pytest.fixture(autouse=True)
def isolate_demo_mode_env(monkeypatch):
    """
    Tự động xóa biến môi trường DEMO_MODE cho mọi test để kết quả không phụ thuộc
    vào môi trường shell của người chạy.
    Các test cần DEMO_MODE thì tự đặt bằng monkeypatch.setenv.
    """
    monkeypatch.delenv("DEMO_MODE", raising=False)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database_session():
    """Khởi tạo database kiểm thử phiên."""
    init_database()
    yield _TEST_DB_PATH
    try:
        if _TEST_DB_PATH.exists():
            _TEST_DB_PATH.unlink()
    except Exception:
        pass

