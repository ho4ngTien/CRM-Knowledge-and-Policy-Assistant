"""Post-generation verification state structures (ANS 04, KNW 04)."""

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class ValidationOutcome:
    """Authoritative final-gate verification result prior to UI delivery."""

    is_valid: bool
    is_stale: bool
    failure_reasons: tuple[str, ...] = field(default_factory=tuple)
