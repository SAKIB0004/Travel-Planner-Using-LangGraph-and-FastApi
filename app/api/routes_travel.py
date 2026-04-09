from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.schemas.request import TripPlanningRequest
from app.schemas.response import ApiResponse, TripPlanningResponse
from app.services.trip_service import get_trip_service

router = APIRouter(prefix="/api/v1/travel", tags=["travel"])


@router.post("/plan", response_model=ApiResponse)
async def plan_trip(payload: TripPlanningRequest) -> ApiResponse:
    service = get_trip_service()
    try:
        response = await service.plan_trip(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Trip planning failed: {exc}") from exc

    return ApiResponse(success=True, message="Travel plan created successfully.", data=response)
