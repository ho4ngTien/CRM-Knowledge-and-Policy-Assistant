"""Evaluation service enforcing Section 8 thresholds & Chinese Wall partition isolation."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.evaluation.models import EvaluationRun
from src.modules.evaluation.schemas import EvaluationRunCreateRequest, EvaluationRunResponse
from src.shared.auth import AuthenticatedUser, ensure_partition_access
from src.shared.enums import EvalPartition, ReleaseGate


class EvaluationService:
    """Evaluates RFP Section 8 quantitative thresholds while isolating sealed_100."""

    def check_section8_thresholds(self, payload: EvaluationRunCreateRequest) -> list[str]:
        """Verify mandatory RFP Section 8 acceptance gates (DEL 02, DEL 03, VN 02)."""
        failures: list[str] = []
        if payload.critical_control_errors > 0:
            failures.append(
                f"Critical control errors={payload.critical_control_errors} (must be 0)."
            )
        if payload.applicability_rate < 0.95:
            failures.append(f"Applicability={payload.applicability_rate:.2%} (< 95%).")
        if payload.grounding_rate < 0.95:
            failures.append(f"Grounding={payload.grounding_rate:.2%} (< 95%).")
        if payload.completeness_rate < 0.90:
            failures.append(f"Completeness={payload.completeness_rate:.2%} (< 90%).")
        if payload.recall_at_5 < 0.90:
            failures.append(f"Recall@5={payload.recall_at_5:.2%} (< 90%).")
        if payload.usefulness_rate < 0.80:
            failures.append(f"Usefulness={payload.usefulness_rate:.2%} (< 80%).")
        if payload.fabrication_on_unanswerable_rate > 0.05:
            rate = f"{payload.fabrication_on_unanswerable_rate:.2%}"
            failures.append(f"Fabrication on unanswerable={rate} (> 5%).")
        return failures

    async def record_run(
        self,
        db: AsyncSession,
        user: AuthenticatedUser,
        payload: EvaluationRunCreateRequest,
    ) -> EvaluationRunResponse:
        """Persist an evaluation run after verifying Chinese Wall access on sealed_100."""
        ensure_partition_access(user, payload.partition)
        failures = self.check_section8_thresholds(payload)
        passed = len(failures) == 0

        run = EvaluationRun(
            id=f"EVAL-{uuid.uuid4().hex[:10].upper()}",
            release_gate=payload.release_gate.value,
            partition=payload.partition.value,
            evaluator_id=user.user_id,
            total_cases=payload.total_cases,
            critical_control_errors=payload.critical_control_errors,
            applicability_rate=payload.applicability_rate,
            grounding_rate=payload.grounding_rate,
            completeness_rate=payload.completeness_rate,
            recall_at_5=payload.recall_at_5,
            usefulness_rate=payload.usefulness_rate,
            fabrication_on_unanswerable_rate=payload.fabrication_on_unanswerable_rate,
            passed_thresholds=passed,
            notes=payload.notes,
        )
        db.add(run)
        await db.commit()
        await db.refresh(run)
        return EvaluationRunResponse(
            id=run.id,
            release_gate=ReleaseGate(run.release_gate),
            partition=EvalPartition(run.partition),
            total_cases=run.total_cases,
            critical_control_errors=run.critical_control_errors,
            applicability_rate=run.applicability_rate,
            grounding_rate=run.grounding_rate,
            completeness_rate=run.completeness_rate,
            recall_at_5=run.recall_at_5,
            usefulness_rate=run.usefulness_rate,
            fabrication_on_unanswerable_rate=run.fabrication_on_unanswerable_rate,
            passed_thresholds=run.passed_thresholds,
            failed_criteria=failures,
        )

    async def list_runs(
        self,
        db: AsyncSession,
        user: AuthenticatedUser,
        partition: EvalPartition,
    ) -> list[EvaluationRunResponse]:
        """List runs for a single partition without mixing real_200 and challenges_80."""
        ensure_partition_access(user, partition)
        rows = (
            await db.execute(
                select(EvaluationRun)
                .where(EvaluationRun.partition == partition.value)
                .order_by(EvaluationRun.created_at.desc())
            )
        ).scalars().all()
        return [
            EvaluationRunResponse(
                id=r.id,
                release_gate=ReleaseGate(r.release_gate),
                partition=EvalPartition(r.partition),
                total_cases=r.total_cases,
                critical_control_errors=r.critical_control_errors,
                applicability_rate=r.applicability_rate,
                grounding_rate=r.grounding_rate,
                completeness_rate=r.completeness_rate,
                recall_at_5=r.recall_at_5,
                usefulness_rate=r.usefulness_rate,
                fabrication_on_unanswerable_rate=r.fabrication_on_unanswerable_rate,
                passed_thresholds=r.passed_thresholds,
                failed_criteria=[],
            )
            for r in rows
        ]
