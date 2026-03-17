"""GET /api/v1/evaluate — compute accuracy and F1 from labeled documents."""
from collections import defaultdict

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.db_models import Document
from app.models.schemas import EvaluateResponse, DOC_TYPES

router = APIRouter()


def _compute_metrics(
    y_true: list[str], y_pred: list[str]
) -> tuple[float, dict[str, float], float, dict[str, dict[str, int]]]:
    """Compute accuracy, per-class F1, macro F1, and confusion counts."""
    if not y_true:
        return 0.0, {}, 0.0, {}

    # Accuracy
    correct = sum(t == p for t, p in zip(y_true, y_pred))
    accuracy = correct / len(y_true)

    # Per-class TP, FP, FN
    tp: dict[str, int] = defaultdict(int)
    fp: dict[str, int] = defaultdict(int)
    fn: dict[str, int] = defaultdict(int)
    class_totals: dict[str, int] = defaultdict(int)

    for t, p in zip(y_true, y_pred):
        class_totals[t] += 1
        if t == p:
            tp[t] += 1
        else:
            fp[p] += 1
            fn[t] += 1

    # Per-class F1
    classes = sorted(set(y_true))
    per_class_f1: dict[str, float] = {}
    for cls in classes:
        precision = tp[cls] / (tp[cls] + fp[cls]) if (tp[cls] + fp[cls]) > 0 else 0.0
        recall = tp[cls] / (tp[cls] + fn[cls]) if (tp[cls] + fn[cls]) > 0 else 0.0
        f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
        per_class_f1[cls] = round(f1, 4)

    macro_f1 = round(sum(per_class_f1.values()) / len(per_class_f1), 4) if per_class_f1 else 0.0

    # Confusion counts (correct vs total per true class)
    confusion_counts = {
        cls: {"correct": tp[cls], "total": class_totals[cls]}
        for cls in classes
    }

    return round(accuracy, 4), per_class_f1, macro_f1, confusion_counts


@router.get("", response_model=EvaluateResponse)
async def evaluate(
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    """
    Evaluate classification accuracy using documents that have ground_truth set.
    Only documents with status='done' and ground_truth != null are considered.
    """
    result = await db.execute(
        select(Document)
        .where(
            Document.ground_truth.isnot(None),
            Document.doc_type.isnot(None),
            Document.status == "done",
        )
        .order_by(Document.created_at.desc())
        .limit(limit)
    )
    docs = result.scalars().all()

    y_true = [d.ground_truth for d in docs]
    y_pred = [d.doc_type for d in docs]

    accuracy, per_class_f1, macro_f1, confusion_counts = _compute_metrics(y_true, y_pred)

    return EvaluateResponse(
        total_evaluated=len(docs),
        accuracy=accuracy,
        per_class_f1=per_class_f1,
        macro_f1=macro_f1,
        confusion_counts=confusion_counts,
    )
