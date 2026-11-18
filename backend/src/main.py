"""FastAPI application entrypoint mounting all 12 SRS modules & fail-closed handlers [CKPA-17].

Gate: G1 | SRS: Mục 4.3, Mục 7.2, SRS-FR-06.1 | RFP: ANS03, ANS04, DEL02
Responsible: C1 (Phạm Lương Yến Nhi — Lead LLM Eng), B2 (Hữu Tài — Policy Eng), B3 (Phạm Quý Hải — Retrieval Eng)
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.config import settings
from src.modules.admin.router import router as admin_router
from src.modules.answer.router import router as answer_router
from src.modules.audit.router import router as audit_router
from src.modules.evaluation.router import router as evaluation_router
from src.modules.feedback.router import router as feedback_router
from src.modules.identity.router import router as identity_router
from src.modules.ingestion.router import router as ingestion_router
from src.modules.knowledge.router import router as knowledge_router
from src.modules.policy.router import router as policy_router
from src.modules.referral.router import router as referral_router
from src.modules.retrieval.router import router as retrieval_router
from src.modules.validation.router import router as validation_router
from src.shared.exceptions import (
    AccessDenied,
    AuthorityUnavailable,
    CitationValidationFailed,
    CriticalFieldMissing,
    InsufficientEvidence,
    PolicyNotFound,
    PolicyWithdrawn,
    QuotaExceeded,
    SourceConflict,
    StaleAnswerBlocked,
)

app = FastAPI(
    title="SongNhat CRM Knowledge & Policy Assistant API",
    version="0.1.0",
    description="Grounded Vietnamese CRM policy assistant strictly scoped to SongNhat RFP.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

_EXCEPTION_STATUS_MAP: tuple[tuple[type[Exception], int, str], ...] = (
    (PolicyNotFound, status.HTTP_404_NOT_FOUND, "POLICY_NOT_FOUND"),
    (AccessDenied, status.HTTP_403_FORBIDDEN, "ACCESS_DENIED"),
    (PolicyWithdrawn, status.HTTP_409_CONFLICT, "POLICY_WITHDRAWN"),
    (StaleAnswerBlocked, status.HTTP_409_CONFLICT, "STALE_ANSWER_BLOCKED"),
    (SourceConflict, status.HTTP_409_CONFLICT, "SOURCE_CONFLICT"),
    (InsufficientEvidence, status.HTTP_422_UNPROCESSABLE_CONTENT, "INSUFFICIENT_EVIDENCE"),
    (CitationValidationFailed, status.HTTP_422_UNPROCESSABLE_CONTENT, "CITATION_INVALID"),
    (CriticalFieldMissing, status.HTTP_422_UNPROCESSABLE_CONTENT, "CRITICAL_FIELD_MISSING"),
    (QuotaExceeded, status.HTTP_429_TOO_MANY_REQUESTS, "QUOTA_EXCEEDED"),
    (AuthorityUnavailable, status.HTTP_503_SERVICE_UNAVAILABLE, "AUTHORITY_UNAVAILABLE"),
)


def _register_exception_handlers(application: FastAPI) -> None:
    for exc_cls, http_status, code in _EXCEPTION_STATUS_MAP:

        async def _handler(
            request: Request,
            exc: Exception,
            *,
            _status: int = http_status,
            _code: str = code,
        ) -> JSONResponse:
            _ = request
            return JSONResponse(
                status_code=_status,
                content={"error_code": _code, "detail": str(exc)},
            )

        application.add_exception_handler(exc_cls, _handler)


_register_exception_handlers(app)

API = "/api/v1"
app.include_router(identity_router, prefix=f"{API}/identity", tags=["Identity"])
app.include_router(knowledge_router, prefix=f"{API}/knowledge", tags=["Knowledge"])
app.include_router(ingestion_router, prefix=f"{API}/ingestion", tags=["Ingestion"])
app.include_router(policy_router, prefix=f"{API}/policy", tags=["Policy"])
app.include_router(retrieval_router, prefix=f"{API}/retrieval", tags=["Retrieval"])
app.include_router(answer_router, prefix=f"{API}/answer", tags=["Answer"])
app.include_router(validation_router, prefix=f"{API}/validation", tags=["Validation"])
app.include_router(referral_router, prefix=f"{API}/referral", tags=["Referral"])
app.include_router(feedback_router, prefix=f"{API}/feedback", tags=["Feedback"])
app.include_router(audit_router, prefix=f"{API}/audit", tags=["Audit"])
app.include_router(evaluation_router, prefix=f"{API}/evaluation", tags=["Evaluation"])
app.include_router(admin_router, prefix=f"{API}/admin", tags=["Admin"])


@app.get("/health", tags=["Health"])
async def health() -> dict[str, object]:
    """Liveness and governance-flag telemetry endpoint."""
    return {
        "status": "ok",
        "version": "0.1.0",
        "timezone": settings.APP_TIMEZONE,
        "streaming_enabled": settings.ENABLE_ANSWER_STREAMING,
        "mounted_modules": 12,
    }
