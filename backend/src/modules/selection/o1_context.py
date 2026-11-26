"""Option O1 Selected CRM Context domain model, hard caps, and SEC 02 allowlist validation.

Traceability:
- RFP Reference: Mục 1-2 (Scope), DAT 07 (3rd CSV schema), SEC 02 (PII minimization).
- Hard Caps: CAP-18 (<= 2,000 init rows, <= 5,000 retained rows, <= 1 record/pkg).
- Annex C & Legal: R02 (DPIA), R03 (Legal basis), SEC 01 (CRM parity).
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from src.config import settings
from src.modules.selection.schemas import ScopeDimensions

# Hard caps per CAP-18 / DAT 07
MAX_O1_INIT_ROWS: int = 2000
MAX_O1_RETAINED_ROWS: int = 5000
MAX_O1_RECORDS_PER_PACKAGE: int = 1

# Approved field allowlist per SEC 02 / DAT 07
O1_ALLOWED_FIELDS: frozenset[str] = frozenset(
    {
        "customer_id",
        "customer_tier",
        "industry_code",
        "assigned_branch",
        "assigned_company",
    }
)

# Forbidden sensitive PII attributes per SEC 02 / Annex F
O1_FORBIDDEN_PII_FIELDS: frozenset[str] = frozenset(
    {
        "phone",
        "phone_number",
        "sdt",
        "email",
        "cccd",
        "cmnd",
        "id_card",
        "national_id",
        "tax_id",
        "mst_ca_nhan",
        "bank_account",
        "so_tai_khoan",
        "salary",
        "thu_nhap",
        "mailbox",
        "dossier",
        "ho_so_chi_tiet",
    }
)


class CustomerContextO1(BaseModel):
    """Controlled Selected CRM Context record adhering strictly to SEC 02 allowlist."""

    model_config = ConfigDict(extra="forbid")

    customer_id: str = Field(
        ...,
        description="Anonymized customer identifier (e.g. 'CUST-001', 'KH-B2B-01').",
    )
    customer_tier: str = Field(
        ...,
        description="Customer tier / category (e.g. 'b2b', 'b2c', 'vip', 'loyal').",
    )
    industry_code: str | None = Field(
        default=None,
        description="Standard industry classification code.",
    )
    assigned_branch: str | None = Field(
        default=None,
        description="Branch managing this customer account (e.g. 'Hà Nội', 'TP.HCM').",
    )
    assigned_company: str | None = Field(
        default=None,
        description="Company legal entity code (e.g. 'Song Nhật').",
    )


def validate_o1_customer_record(raw_record: dict[str, Any]) -> CustomerContextO1:
    """Validate a raw CRM context record against SEC 02 allowlist and PII prohibitions.

    Raises:
        ValueError: If forbidden PII or unapproved fields are present.
    """
    raw_keys_lower = {str(k).strip().lower() for k in raw_record}

    # Check for forbidden PII fields
    pii_violations = raw_keys_lower.intersection(O1_FORBIDDEN_PII_FIELDS)
    if pii_violations:
        err_msg = (
            f"SEC 02 violation: forbidden PII fields detected in O1 context: "
            f"{sorted(pii_violations)}"
        )
        raise ValueError(err_msg)

    # Check for unapproved fields (must only contain allowed keys)
    unapproved = raw_keys_lower - O1_ALLOWED_FIELDS
    if unapproved:
        err_msg = (
            f"SEC 02 allowlist violation: unapproved fields detected in O1 record: "
            f"{sorted(unapproved)}"
        )
        raise ValueError(err_msg)

    normalized = {str(k).strip().lower(): v for k, v in raw_record.items()}
    if len(normalized) != len(raw_record):
        raise ValueError("Duplicate keys after normalization in O1 record.")
    return CustomerContextO1(**normalized)


def validate_o1_batch_caps(records: list[dict[str, Any]], *, is_init: bool = False) -> None:
    """Enforce CAP-18 / DAT 07 batch volume caps (<= 2000 init, <= 5000 retained).

    Raises:
        ValueError: If record count exceeds RFP boundary caps.
    """
    limit = MAX_O1_INIT_ROWS if is_init else MAX_O1_RETAINED_ROWS
    if len(records) > limit:
        raise ValueError(
            f"DAT 07 / CAP-18 cap exceeded: batch contains {len(records)} records, "
            f"limit is {limit} rows."
        )


def apply_o1_to_scope_dimensions(
    dimensions: ScopeDimensions,
    context: CustomerContextO1 | None,
) -> ScopeDimensions:
    """Enrich 6-dimension scope matching context with approved O1 customer context (DAT 04/07).

    Deterministic logic (0% LLM):
    - Infers branch from assigned_branch if dimension is unset or wildcard.
    - Infers customer_category from customer_tier if dimension is unset or wildcard.
    - Infers company from assigned_company if dimension is unset or wildcard.
    """
    if context is None:
        return dimensions

    if not settings.ENABLE_O1_CONTEXT_IMPORT:
        raise PermissionError(
            "O1_OPTION_DISABLED_IN_BASE_SCOPE: Cannot apply O1 customer context "
            "when ENABLE_O1_CONTEXT_IMPORT is False."
        )

    dim_dict = dimensions.model_dump()

    # Fill customer_category if unset or wildcard
    cur_cat = dim_dict.get("customer_category")
    if not cur_cat or cur_cat in {"all", "*", "any"}:
        dim_dict["customer_category"] = context.customer_tier

    # Fill branch if unset or wildcard
    cur_branch = dim_dict.get("branch")
    if not cur_branch or cur_branch in {"all", "*", "any"}:
        if context.assigned_branch:
            dim_dict["branch"] = context.assigned_branch

    # Fill company if unset or wildcard
    cur_company = dim_dict.get("company")
    if not cur_company or cur_company in {"all", "*", "any"}:
        if context.assigned_company:
            dim_dict["company"] = context.assigned_company

    return ScopeDimensions(**dim_dict)
