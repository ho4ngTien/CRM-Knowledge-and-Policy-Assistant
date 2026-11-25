"""FastAPI application entrypoint mounting all 13 SRS modules & fail-closed handlers [CKPA-17].

Gate: G1 | SRS: Mục 4.3, Mục 7.2, SRS-FR-06.1 | RFP: ANS03, ANS04, DEL02
Responsible: C1 (Phạm Lương Yến Nhi — Lead LLM Eng), B2 (Hữu Tài — Policy Eng),
B3 (Phạm Quý Hải — Retrieval Eng)
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI, Request, status
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
from src.modules.selection.router import router as selection_router
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


@asynccontextmanager
async def lifespan(_application: FastAPI) -> AsyncIterator[None]:
    """Verify SEC 06 Test/Prod isolation and SEC 04 training locks at startup."""
    settings.verify_sec06_test_prod_isolation()
    yield


app = FastAPI(
    title="SongNhat CRM Knowledge & Policy Assistant API",
    version="0.1.0",
    description="Grounded Vietnamese CRM policy assistant strictly scoped to SongNhat RFP.",
    lifespan=lifespan,
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
_MOUNTED_ROUTERS: tuple[tuple[APIRouter, str, str], ...] = (
    (identity_router, f"{API}/identity", "Identity"),
    (knowledge_router, f"{API}/knowledge", "Knowledge"),
    (ingestion_router, f"{API}/ingestion", "Ingestion"),
    (policy_router, f"{API}/policy", "Policy"),
    (retrieval_router, f"{API}/retrieval", "Retrieval"),
    (answer_router, f"{API}/answer", "Answer"),
    (validation_router, f"{API}/validation", "Validation"),
    (referral_router, f"{API}/referral", "Referral"),
    (feedback_router, f"{API}/feedback", "Feedback"),
    (audit_router, f"{API}/audit", "Audit"),
    (evaluation_router, f"{API}/evaluation", "Evaluation"),
    (selection_router, f"{API}/selection", "Selection"),
    (admin_router, f"{API}/admin", "Admin"),
)
for _router, _prefix, _tag in _MOUNTED_ROUTERS:
    app.include_router(_router, prefix=_prefix, tags=[_tag])


@app.get("/health", tags=["Health"])
async def health() -> dict[str, object]:
    """Liveness and governance-flag telemetry endpoint."""
    return {
        "status": "ok",
        "version": "0.1.0",
        "timezone": settings.APP_TIMEZONE,
        "streaming_enabled": settings.ENABLE_ANSWER_STREAMING,
        "mounted_modules": len(_MOUNTED_ROUTERS),
    }
