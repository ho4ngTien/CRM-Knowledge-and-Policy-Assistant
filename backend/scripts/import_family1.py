"""Run the CKPA-52 Family 1 import into ingestion staging and write its audit log."""

import asyncio
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from src.db import AsyncSessionLocal
from src.modules.ingestion.service import IngestionService
from src.shared.enums import BatchType

ROOT = Path(__file__).resolve().parents[2]
FAMILY1 = ROOT / "data" / "g1" / "family1"
REPORT_PATH = ROOT / "data" / "g1" / "reports" / "CKPA-52_Import_Log_Ho1.md"
VN_TZ = ZoneInfo("Asia/Ho_Chi_Minh")


async def main() -> None:
    service = IngestionService()
    artifacts = (
        (
            "passages",
            "Policy_Corpus_Family1.csv",
            "40",
            "CKPA-52-family1-passages-v1",
        ),
        (
            "critical_fields",
            "Critical_Fields_Family1.csv",
            "16",
            "CKPA-52-family1-critical-fields-v1",
        ),
    )
    results = []
    async with AsyncSessionLocal() as db:
        for source_type, filename, expected, idempotency_key in artifacts:
            report = await service.import_csv_bytes(
                db,
                (FAMILY1 / filename).read_bytes(),
                source_type=source_type,
                batch_type=BatchType.FULL_SNAPSHOT,
                expected_rows=int(expected),
                manifest_bytes=(
                    FAMILY1 / "Source_URI_And_Checksum_Manifest_Family1.csv"
                ).read_bytes(),
                idempotency_key=idempotency_key,
                submitted_by="CKPA-52",
            )
            if report.rejected_rows:
                raise RuntimeError(
                    f"{source_type} import rejected {report.rejected_rows} row(s): "
                    f"{[issue.reason_code for issue in report.quarantine_issues]}"
                )
            if report.expected_rows != report.accepted_rows + report.quarantined_rows:
                raise RuntimeError(f"{source_type} import failed row-count reconciliation.")
            if report.imported_rows != report.accepted_rows:
                raise RuntimeError(f"{source_type} accepted rows were not fully staged.")
            if source_type == "passages" and (
                report.expected_rows != 40
                or report.accepted_rows != 39
                or report.quarantined_rows != 1
                or not any(
                    issue.record_id == "PAS-040"
                    and issue.reason_code == "MISSING_ESSENTIAL_ATTACHMENTS"
                    for issue in report.quarantine_issues
                )
            ):
                raise RuntimeError("Passages did not match the approved 40 = 39 + 1 baseline.")
            if source_type == "critical_fields" and (
                report.expected_rows != 16
                or report.accepted_rows != 16
                or report.quarantined_rows != 0
            ):
                raise RuntimeError(
                    "Critical fields did not match the approved 16 = 16 + 0 baseline."
                )
            results.append((source_type, filename, report))

    generated_at = datetime.now(VN_TZ).isoformat()
    lines = [
        "# CKPA-52 Import Log — Họ 1",
        "",
        f"- Thời điểm chạy: `{generated_at}`",
        "- Chế độ: `FULL_SNAPSHOT`; dữ liệu hợp lệ lưu trong `import_records` (staging),",
        "  dữ liệu lỗi lưu trong `quarantine_rows`; không tự phát hành vào retrieval.",
        "- Nguồn kiểm checksum: `Source_URI_And_Checksum_Manifest_Family1.csv`.",
        "",
        "| CSV | Batch ID | Expected | Received | Imported | Quarantined | Rejected |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for source_type, filename, report in results:
        lines.append(
            f"| `{filename}` | `{report.batch_id}` | {report.expected_rows} | "
            f"{report.received_rows} | {report.imported_rows} | {report.quarantined_rows} | "
            f"{report.rejected_rows} |"
        )
    lines.extend(["", "## Quarantine"])
    issues = [
        (filename, issue) for _, filename, report in results for issue in report.quarantine_issues
    ]
    if issues:
        lines.extend(
            f"- `{filename}` row {issue.row_number} (`{issue.record_id}`): "
            f"`{issue.reason_code}` — {issue.reason_detail}"
            for filename, issue in issues
        )
    else:
        lines.append("- Không có dòng quarantine.")
    lines.extend(
        [
            "",
            "## Reconciliation",
            "",
            "- Passages: `40 = 39 imported + 1 quarantined` (PAS-040 /",
            "  `MISSING_ESSENTIAL_ATTACHMENTS`).",
            "- Critical fields: `16 = 16 imported + 0 quarantined`.",
            "- Mỗi lô được bảo vệ bằng idempotency key; chạy lại cùng nội dung không tạo bản sao.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(REPORT_PATH)


if __name__ == "__main__":
    asyncio.run(main())
