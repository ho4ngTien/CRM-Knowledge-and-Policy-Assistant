"""
legacy/s4/services/database.py
Quản lý kết nối SQLite và lưu trữ cục bộ an toàn:
- CKPA-45 / KNW 05: Referral cục bộ
- CKPA-46 / KNW 07: Feedback (5 nhóm hợp lệ, hữu ích/không, cờ thiếu ngoại lệ, cờ không căn cứ)
- CKPA-47 / ANS 06: HOLD logs (mã lý do, giải thích, thời gian)
- WP04: Ghi phiên bản PROMPT_VERSION và CONFIG_VERSION vào bản ghi lưu vết

Quy tắc an toàn:
- Mọi câu lệnh SQL đều sử dụng parameterized query (dùng dấu ?) để chống SQL Injection.
- Di chuyển an toàn (Migration): Dùng PRAGMA table_info và ALTER TABLE, không xóa bảng hay dữ liệu cũ.
- Hỗ trợ biến môi trường TEST_DATABASE_PATH để cách ly hoàn toàn dữ liệu kiểm thử,
  không bao giờ ghi đè hoặc làm biến đổi legacy/data/app.db thực tế khi chạy test.
"""

import os
import sqlite3
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from legacy.s4 import config

logger = logging.getLogger(__name__)

# Xác định thư mục gốc của legacy
BASE_DIR = Path(__file__).resolve().parents[2]

# 5 nhóm phản hồi hợp lệ duy nhất theo tiêu chuẩn CKPA-46
VALID_FEEDBACK_TYPES = {
    "Missing Source",
    "Outdated Rule",
    "Wrong Scope",
    "Missing Exception",
    "Refusal"
}


def get_database_path() -> Path:
    """
    Trả về đường dẫn database SQLite.
    Ưu tiên TEST_DATABASE_PATH nếu đang chạy kiểm thử để cách ly legacy/data/app.db thật.
    """
    custom = os.environ.get("TEST_DATABASE_PATH") or os.environ.get("APP_DATABASE_PATH")
    if custom:
        return Path(custom)
    return BASE_DIR / "data" / "app.db"


def get_connection() -> sqlite3.Connection:
    """Tạo kết nối đến SQLite database."""
    db_path = get_database_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection


def _ensure_column_exists(connection: sqlite3.Connection, table_name: str, column_name: str, column_def: str) -> None:
    """Kiểm tra và thêm cột nếu chưa có (Safe Migration bằng ALTER TABLE)."""
    cursor = connection.execute(f"PRAGMA table_info({table_name})")
    columns = [row["name"] for row in cursor.fetchall()]
    if column_name not in columns:
        connection.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_def}")


def _ensure_feedback_type_nullable(connection: sqlite3.Connection) -> None:
    """
    Migration an toàn cho cột feedback_type:
    Nếu cột feedback_type đang là NOT NULL (1), tạo bảng mới với feedback_type TEXT (nullable)
    và sao chép toàn bộ dữ liệu sang, tuyệt đối không xóa hay mất dữ liệu hiện hữu.
    """
    cursor = connection.execute("PRAGMA table_info(feedback)")
    cols = cursor.fetchall()
    needs_migration = False
    for col in cols:
        col_name = col["name"] if isinstance(col, sqlite3.Row) else col[1]
        col_notnull = col["notnull"] if isinstance(col, sqlite3.Row) else col[3]
        if col_name == "feedback_type" and col_notnull == 1:
            needs_migration = True
            break

    if needs_migration:
        connection.execute("""
            CREATE TABLE feedback_migration_temp (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                feedback_type TEXT,
                comment TEXT,
                is_helpful INTEGER DEFAULT NULL,
                flag_missing_exception INTEGER DEFAULT 0,
                flag_unfounded_claim INTEGER DEFAULT 0,
                prompt_version TEXT DEFAULT '',
                config_version TEXT DEFAULT '',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        connection.execute("""
            INSERT INTO feedback_migration_temp (
                id, question, feedback_type, comment, is_helpful,
                flag_missing_exception, flag_unfounded_claim,
                prompt_version, config_version, created_at
            )
            SELECT id, question, feedback_type, comment, is_helpful,
                   flag_missing_exception, flag_unfounded_claim,
                   prompt_version, config_version, created_at
            FROM feedback
        """)
        connection.execute("DROP TABLE feedback")
        connection.execute("ALTER TABLE feedback_migration_temp RENAME TO feedback")


def init_database() -> None:
    """
    Khởi tạo database và chạy di chuyển cấu trúc an toàn (Migration).
    Không bao giờ xóa bảng hay mất dữ liệu hiện hữu.
    """
    with get_connection() as connection:
        # 1. Bảng feedback (CKPA-46 & KNW 07, WP04 phiên bản)
        connection.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                feedback_type TEXT,
                comment TEXT,
                is_helpful INTEGER DEFAULT NULL,
                flag_missing_exception INTEGER DEFAULT 0,
                flag_unfounded_claim INTEGER DEFAULT 0,
                prompt_version TEXT DEFAULT '',
                config_version TEXT DEFAULT '',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        _ensure_feedback_type_nullable(connection)
        _ensure_column_exists(connection, "feedback", "is_helpful", "INTEGER DEFAULT NULL")
        _ensure_column_exists(connection, "feedback", "flag_missing_exception", "INTEGER DEFAULT 0")
        _ensure_column_exists(connection, "feedback", "flag_unfounded_claim", "INTEGER DEFAULT 0")
        _ensure_column_exists(connection, "feedback", "prompt_version", "TEXT DEFAULT ''")
        _ensure_column_exists(connection, "feedback", "config_version", "TEXT DEFAULT ''")

        # 2. Bảng referrals (CKPA-45 & KNW 05)
        connection.execute("""
            CREATE TABLE IF NOT EXISTS referrals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                reason TEXT NOT NULL,
                policy_owner TEXT,
                status TEXT DEFAULT 'PENDING',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        _ensure_column_exists(connection, "referrals", "status", "TEXT DEFAULT 'PENDING'")

        # 3. Bảng hold_logs (CKPA-47 & ANS 06, WP04 phiên bản)
        connection.execute("""
            CREATE TABLE IF NOT EXISTS hold_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                reason TEXT NOT NULL DEFAULT '',
                reason_code TEXT DEFAULT 'HOLD_GENERAL',
                reason_text TEXT DEFAULT '',
                prompt_version TEXT DEFAULT '',
                config_version TEXT DEFAULT '',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        _ensure_column_exists(connection, "hold_logs", "reason", "TEXT NOT NULL DEFAULT ''")
        _ensure_column_exists(connection, "hold_logs", "reason_code", "TEXT DEFAULT 'HOLD_GENERAL'")
        _ensure_column_exists(connection, "hold_logs", "reason_text", "TEXT DEFAULT ''")
        _ensure_column_exists(connection, "hold_logs", "prompt_version", "TEXT DEFAULT ''")
        _ensure_column_exists(connection, "hold_logs", "config_version", "TEXT DEFAULT ''")


def check_connection() -> bool:
    """Kiểm tra kết nối database."""
    try:
        with get_connection() as connection:
            result = connection.execute("SELECT 1").fetchone()
            return result is not None and result[0] == 1
    except Exception:
        return False


def save_feedback(
    question: str,
    feedback_type: Optional[str] = None,
    comment: str = "",
    is_helpful: Optional[bool] = None,
    flag_missing_exception: bool = False,
    flag_unfounded_claim: bool = False,
    prompt_version: Optional[str] = None,
    config_version: Optional[str] = None,
) -> bool:
    """
    Ghi nhận phản hồi của người dùng (CKPA-46 & KNW 07, WP04 phiên bản).
    Kiểm tra tính hợp lệ:
    - Khi is_helpful là True (Hữu ích): feedback_type được lưu là None/NULL, hai cờ vẫn lưu được.
    - Khi is_helpful là False (Không hữu ích): bắt buộc feedback_type phải thuộc VALID_FEEDBACK_TYPES. Thiếu hoặc giá trị lạ sẽ bị từ chối (False).
    - Khi is_helpful là None: nếu có feedback_type thì phải hợp lệ, nếu không thì lưu None.
    """
    if is_helpful is True:
        cleaned_type = None
    elif is_helpful is False:
        if not feedback_type or not str(feedback_type).strip():
            return False
        cleaned_type = str(feedback_type).strip()
        if cleaned_type not in VALID_FEEDBACK_TYPES:
            return False
    else:
        if feedback_type and str(feedback_type).strip():
            cleaned_type = str(feedback_type).strip()
            if cleaned_type not in VALID_FEEDBACK_TYPES:
                return False
        else:
            cleaned_type = None

    helpful_val = 1 if is_helpful is True else (0 if is_helpful is False else None)
    missing_exc_val = 1 if flag_missing_exception else 0
    unfounded_val = 1 if flag_unfounded_claim else 0
    p_ver = prompt_version or getattr(config, "PROMPT_VERSION", "v1.1")
    c_ver = config_version or getattr(config, "CONFIG_VERSION", "1.1.0")

    try:
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO feedback (
                    question, feedback_type, comment, is_helpful,
                    flag_missing_exception, flag_unfounded_claim,
                    prompt_version, config_version
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    question.strip(),
                    cleaned_type,
                    comment.strip(),
                    helpful_val,
                    missing_exc_val,
                    unfounded_val,
                    p_ver,
                    c_ver,
                )
            )
        return True
    except Exception as e:
        logger.error("Lỗi khi lưu feedback vào cơ sở dữ liệu: %s", type(e).__name__)
        return False


def save_referral(
    question: str,
    reason: str,
    policy_owner: str = "",
    status: str = "PENDING"
) -> bool:
    """
    Ghi nhận yêu cầu chuyển người phụ trách cục bộ (CKPA-45 & KNW 05).
    Chỉ lưu trữ tối thiểu vào SQLite, không thực hiện bất kỳ lệnh gọi mạng nào.
    """
    try:
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO referrals (question, reason, policy_owner, status)
                VALUES (?, ?, ?, ?)
                """,
                (question.strip(), reason.strip(), policy_owner.strip(), status.strip())
            )
        return True
    except Exception as e:
        logger.error("Lỗi khi lưu referral vào cơ sở dữ liệu: %s", type(e).__name__)
        return False


def save_hold_log(
    question: str,
    reason: str,
    reason_code: str = "HOLD_GENERAL",
    prompt_version: Optional[str] = None,
    config_version: Optional[str] = None,
) -> bool:
    """
    Ghi nhận nhật ký trạng thái HOLD (CKPA-47 & ANS 06, WP04 phiên bản).
    Đồng bộ cả cột reason và reason_text để tương thích tuyệt đối.
    """
    cleaned_reason = reason.strip()
    cleaned_code = reason_code.strip()
    p_ver = prompt_version or getattr(config, "PROMPT_VERSION", "v1.1")
    c_ver = config_version or getattr(config, "CONFIG_VERSION", "1.1.0")
    try:
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO hold_logs (
                    question, reason, reason_code, reason_text,
                    prompt_version, config_version
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (question.strip(), cleaned_reason, cleaned_code, cleaned_reason, p_ver, c_ver)
            )
        return True
    except Exception as e:
        logger.error("Lỗi khi lưu hold log vào cơ sở dữ liệu (mã %s): %s", cleaned_code, type(e).__name__)
        return False


def get_recent_feedbacks(limit: int = 10) -> List[Dict[str, Any]]:
    """Đọc danh sách feedback gần nhất phục vụ kiểm tra."""
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, question, feedback_type, comment, is_helpful,
                   flag_missing_exception, flag_unfounded_claim,
                   prompt_version, config_version, created_at
            FROM feedback
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,)
        ).fetchall()
        return [dict(row) for row in rows]


def get_recent_referrals(limit: int = 10) -> List[Dict[str, Any]]:
    """Đọc danh sách referral gần nhất phục vụ kiểm tra."""
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, question, reason, policy_owner, status, created_at
            FROM referrals
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,)
        ).fetchall()
        return [dict(row) for row in rows]


def get_recent_hold_logs(limit: int = 10) -> List[Dict[str, Any]]:
    """Đọc danh sách hold log gần nhất phục vụ kiểm tra."""
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, question, reason_code, 
                   COALESCE(NULLIF(reason_text, ''), reason) AS reason_text,
                   prompt_version, config_version,
                   created_at
            FROM hold_logs
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,)
        ).fetchall()
        return [dict(row) for row in rows]
