"""Admin governance domain state transitions (KNW 03, KNW 04, OPS 05)."""

from src.shared.enums import PolicyLifecycleStatus

ALLOWED_LIFECYCLE_TRANSITIONS: dict[PolicyLifecycleStatus, frozenset[PolicyLifecycleStatus]] = {
    PolicyLifecycleStatus.DRAFT: frozenset(
        {
            PolicyLifecycleStatus.OWNER_REVIEWED,
            PolicyLifecycleStatus.QUARANTINED,
            PolicyLifecycleStatus.WITHDRAWN,
        }
    ),
    PolicyLifecycleStatus.QUARANTINED: frozenset(
        {PolicyLifecycleStatus.DRAFT, PolicyLifecycleStatus.WITHDRAWN}
    ),
    PolicyLifecycleStatus.OWNER_REVIEWED: frozenset(
        {
            PolicyLifecycleStatus.DRAFT,
            PolicyLifecycleStatus.APPROVED,
            PolicyLifecycleStatus.WITHDRAWN,
        }
    ),
    PolicyLifecycleStatus.APPROVED: frozenset(
        {
            PolicyLifecycleStatus.SCHEDULED,
            PolicyLifecycleStatus.EFFECTIVE,
            PolicyLifecycleStatus.WITHDRAWN,
        }
    ),
    PolicyLifecycleStatus.SCHEDULED: frozenset(
        {
            PolicyLifecycleStatus.EFFECTIVE,
            PolicyLifecycleStatus.WITHDRAWN,
        }
    ),
    PolicyLifecycleStatus.EFFECTIVE: frozenset(
        {
            PolicyLifecycleStatus.SUPERSEDED,
            PolicyLifecycleStatus.WITHDRAWN,
        }
    ),
    PolicyLifecycleStatus.SUPERSEDED: frozenset(),
    PolicyLifecycleStatus.WITHDRAWN: frozenset(),
}
