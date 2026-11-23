import sys
from pathlib import Path

# Thêm thư mục gốc vào sys.path để có thể import module 'legacy.s4'
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from legacy.s4.services.database import init_database, check_connection

if __name__ == "__main__":
    init_database()

    if check_connection():
        print("Ket noi SQLite thanh cong!")
        print("Database da duoc khoi tao.")
    else:
        print("Ket noi database that bai!")
