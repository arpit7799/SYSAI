from fastapi import APIRouter
from app.services.optimization_service import (
    run_optimization,
    get_optimization_summary,
)
from app.schemas.optimization import (
    OptimizationSummary,
    OptimizationRequest,
)
from pydantic import BaseModel
from typing import List, Dict, Any


router = APIRouter()


class OptimizationResult(BaseModel):
    status: str
    actions: List[Dict[str, Any]]
    recommendations: List[str]


@router.post(
    "/optimize",
    response_model=OptimizationResult,
    tags=["Optimization"],
    summary="Run autonomous optimization",
)
async def trigger_optimization(request: OptimizationRequest):
    """
    Trigger the autonomous optimization engine.
    mode: safe (priority adjustments only) | aggressive (can terminate processes)
    """
    result = await run_optimization(mode=request.mode)
    return OptimizationResult(
        status=result.get("status", "unknown"),
        actions=result.get("actions", []),
        recommendations=result.get("recommendations", []),
    )


@router.get(
    "/optimize/summary",
    response_model=OptimizationSummary,
    tags=["Optimization"],
    summary="Get optimization history and recommendations",
)
async def get_summary():
    """
    Returns recent optimization actions and current recommendations.
    """
    return await get_optimization_summary()