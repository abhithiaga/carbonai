from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.services.scoring_service import ScoringService
from app.services.carbon_service import CarbonService

router = APIRouter()
scoring_service = ScoringService()
carbon_service = CarbonService()


class ScoringRequest(BaseModel):
    org_id: str
    benchmark_industry: Optional[str] = None


class ScoringResponse(BaseModel):
    org_id: str
    overall_score: float        # 0–100
    grade: str                  # A–F
    subscores: dict             # breakdown by category
    industry_percentile: Optional[float] = None
    improvement_areas: List[str]
    score_history: List[dict]


@router.post("/score", response_model=ScoringResponse)
async def score_org(payload: ScoringRequest):
    """
    Compute a composite sustainability score for an organization
    using emission data and industry benchmarks.
    """
    try:
        summary = await carbon_service.get_summary(payload.org_id)
        score_result = await scoring_service.score(
            summary=summary,
            benchmark_industry=payload.benchmark_industry,
        )
        return ScoringResponse(**score_result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/leaderboard", response_model=List[dict])
async def get_leaderboard(industry: Optional[str] = None, limit: int = 20):
    """Get top-scoring organizations, optionally filtered by industry."""
    try:
        board = await scoring_service.get_leaderboard(industry=industry, limit=limit)
        return board
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/benchmark/{industry}", response_model=dict)
async def get_industry_benchmark(industry: str):
    """Return average emission benchmarks for a given industry sector."""
    try:
        bench = scoring_service.get_benchmark(industry)
        return bench
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"No benchmark data for {industry}")
