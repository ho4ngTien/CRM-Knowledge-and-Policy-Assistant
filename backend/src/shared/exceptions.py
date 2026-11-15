"""Domain exceptions — mapped fail-closed to HTTP responses in global handlers."""


class PolicyNotFound(Exception):
    """Raised when a requested document, passage, or policy version does not exist."""


class AccessDenied(Exception):
    """Raised when a user lacks organizational role or policy audience permission."""


class PolicyWithdrawn(Exception):
    """Raised when any backing policy version was withdrawn prior to delivery."""


class InsufficientEvidence(Exception):
    """Raised when approved sources cannot safely substantiate a definitive answer."""


class CitationValidationFailed(Exception):
    """Raised when generated claims fail post-generation citation/source verification."""


class CriticalFieldMissing(Exception):
    """Raised when a required deterministic critical policy parameter is missing."""


class SourceConflict(Exception):
    """Raised when overlapping effective versions or authorities conflict."""


class AuthorityUnavailable(Exception):
    """Raised when authoritative PostgreSQL state cannot be verified."""


class QuotaExceeded(Exception):
    """Raised when monthly package/LLM call budgets (Common Bid Basis) are exceeded."""


class StaleAnswerBlocked(Exception):
    """Raised when an open or in-flight answer relies on stale/withdrawn evidence."""
