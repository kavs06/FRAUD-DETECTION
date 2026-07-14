from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.investigation_service import InvestigationService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/investigate", tags=["investigation"])

_service: InvestigationService | None = None


def get_service() -> InvestigationService:
    global _service
    if _service is None:
        _service = InvestigationService()
    return _service


class InvestigationRequest(BaseModel):
    provider_id: str


@router.post("")
def investigate_provider(request: InvestigationRequest) -> dict[str, Any]:
    try:
        report = get_service().investigate_provider(request.provider_id)
    except ValueError as exc:
        logger.warning("Investigation request failed: %s", exc)
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - defensive boundary
        logger.exception("Unexpected investigation failure for provider %s", request.provider_id)
        raise HTTPException(status_code=500, detail="Investigation failed") from exc

    return report
