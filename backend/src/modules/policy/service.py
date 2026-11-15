"""Policy applicability, authority matrix, and deterministic threshold logic (DAT 03-06)."""

from datetime import date, datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.modules.policy.models import AuthorityEntry, CriticalField
from src.modules.policy.schemas import (
    ApplicabilityCandidate,
    ApplicabilityResult,
    AuthorityEntryResponse,
    CriticalFieldItem,
)
from src.shared.enums import (
    AuthorityTier,
    ComparisonOperator,
    CriticalFieldType,
    PolicyFamily,
    PolicyLifecycleStatus,
)


class PolicyService:
    """Enforces VN governing-date logic, conflict hold, and typed critical field arithmetic."""

    def resolve_governing_date_vn(
        self, requested_date: date | None
    ) -> tuple[date, bool, bool]:
        """Resolve effective calendar date in Asia/Ho_Chi_Minh and historical/future flags."""
        today_vn = datetime.now(ZoneInfo(settings.APP_TIMEZONE)).date()
        target = requested_date or today_vn
        return target, target < today_vn, target > today_vn

    def evaluate_candidates(
        self,
        candidates: list[ApplicabilityCandidate],
        *,
        requested_date: date | None = None,
        allow_future_preview: bool = False,
    ) -> ApplicabilityResult:
        """Select applicable versions without inferring implicit contract override precedence."""
        tz = ZoneInfo(settings.APP_TIMEZONE)
        gov_date, is_historical, is_future = self.resolve_governing_date_vn(requested_date)
        eligible: list[ApplicabilityCandidate] = []

        for c in candidates:
            if c.status in {
                PolicyLifecycleStatus.DRAFT,
                PolicyLifecycleStatus.OWNER_REVIEWED,
                PolicyLifecycleStatus.APPROVED,
                PolicyLifecycleStatus.WITHDRAWN,
                PolicyLifecycleStatus.QUARANTINED,
            }:
                continue
            if c.status == PolicyLifecycleStatus.SCHEDULED and not (
                is_future and allow_future_preview
            ):
                continue
            if c.status == PolicyLifecycleStatus.SUPERSEDED and not is_historical:
                continue

            eff_from = c.effective_from.astimezone(tz).date()
            eff_to = c.effective_to.astimezone(tz).date() if c.effective_to else None
            if eff_from <= gov_date and (eff_to is None or gov_date <= eff_to):
                eligible.append(c)

        tiers = {c.authority_tier for c in eligible if c.authority_tier != AuthorityTier.STAFF_NOTE}
        non_note = [c for c in eligible if c.authority_tier != AuthorityTier.STAFF_NOTE]
        multiple_same_scope = len(non_note) > 1
        contract_vs_policy = (
            AuthorityTier.CUSTOMER_CONTRACT in tiers and AuthorityTier.POLICY in tiers
        )
        has_conflict = contract_vs_policy or multiple_same_scope
        hold_reason = (
            "DAT 05 Hold: Phát hiện hiệu lực chồng lấn hoặc tương tác hợp đồng-chính sách "
            "chưa có quy tắc ưu tiên được phê duyệt; cần chuyển chủ sở hữu chính sách."
            if has_conflict
            else None
        )
        return ApplicabilityResult(
            governing_date=gov_date,
            timezone=settings.APP_TIMEZONE,
            is_historical=is_historical,
            is_future_preview=is_future and allow_future_preview,
            applicable_version_ids=[c.version_id for c in eligible],
            has_conflict=has_conflict,
            hold_reason=hold_reason,
        )

    def evaluate_numeric_threshold(
        self, operator: ComparisonOperator, actual: Decimal, target: str
    ) -> bool:
        """Compute threshold checks deterministically in Python instead of in the LLM."""
        if operator == ComparisonOperator.BETWEEN:
            low_s, high_s = [part.strip() for part in target.split(";", maxsplit=1)]
            return Decimal(low_s) <= actual <= Decimal(high_s)
        bound = Decimal(target.strip())
        comparators = {
            ComparisonOperator.LE: actual <= bound,
            ComparisonOperator.LT: actual < bound,
            ComparisonOperator.GE: actual >= bound,
            ComparisonOperator.GT: actual > bound,
            ComparisonOperator.EQ: actual == bound,
        }
        return comparators.get(operator, False)

    async def list_authority_entries(self, db: AsyncSession) -> list[AuthorityEntryResponse]:
        """Return configured 5-tier authority hierarchy rows."""
        rows = (await db.execute(select(AuthorityEntry))).scalars().all()
        return [
            AuthorityEntryResponse(
                id=row.id,
                authority_tier=AuthorityTier(row.authority_tier),
                policy_family=PolicyFamily(row.policy_family),
                owner_name=row.owner_name,
                owner_role=row.owner_role,
                backup_owner=row.backup_owner,
                escalation_sla_hours=row.escalation_sla_hours,
            )
            for row in rows
        ]

    async def list_critical_fields(
        self, db: AsyncSession, policy_version_id: str
    ) -> list[CriticalFieldItem]:
        """Fetch deterministic structured critical fields for a policy version."""
        rows = (
            await db.execute(
                select(CriticalField).where(
                    CriticalField.policy_version_id == policy_version_id,
                    CriticalField.status != PolicyLifecycleStatus.WITHDRAWN.value,
                )
            )
        ).scalars().all()
        return [
            CriticalFieldItem(
                field_id=r.id,
                policy_id=r.policy_id,
                policy_version_id=r.policy_version_id,
                document_version_id=r.document_version_id,
                field_name=r.field_name,
                field_type=CriticalFieldType(r.field_type),
                operator=ComparisonOperator(r.operator),
                value=r.value,
                unit=r.unit,
                currency=r.currency,
                approval_role=r.approval_role,
                time_limit=r.time_limit,
                exception_condition=r.exception_condition,
                required_documents=(
                    [d.strip() for d in r.required_documents.split(";") if d.strip()]
                    if r.required_documents
                    else []
                ),
                source_clause=r.source_clause,
                status=PolicyLifecycleStatus(r.status),
            )
            for r in rows
        ]
