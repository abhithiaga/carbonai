from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.services.llm_service import LLMService
from app.services.carbon_service import CarbonService

router = APIRouter()
llm_service = LLMService()
carbon_service = CarbonService()


class RecommendationRequest(BaseModel):
    org_id: str
    focus_area: Optional[str] = None   # e.g. "energy", "transport"
    target_reduction_pct: Optional[float] = 20.0
    context: Optional[str] = None      # free text org context


class RecommendationResponse(BaseModel):
    org_id: str
    recommendations: list
    estimated_reduction_kg_co2e: float
    priority_actions: list
    generated_at: str


@router.post("/generate", response_model=RecommendationResponse)
async def generate_recommendations(payload: RecommendationRequest):
    """
    Use LLM to generate tailored carbon reduction recommendations
    based on the org's actual emission data.
    """
    try:
        # 1. Pull org emission summary
        summary = await carbon_service.get_summary(payload.org_id)

        # 2. Build LLM prompt with real data
        prompt = llm_service.build_recommendation_prompt(
            summary=summary,
            focus_area=payload.focus_area,
            target_reduction_pct=payload.target_reduction_pct,
            extra_context=payload.context,
        )

        # 3. Call LLM
        raw = await llm_service.complete(prompt)

        # 4. Parse structured response
        result = llm_service.parse_recommendations(raw)
        return RecommendationResponse(
            org_id=payload.org_id,
            recommendations=result["recommendations"],
            estimated_reduction_kg_co2e=result["estimated_reduction_kg_co2e"],
            priority_actions=result["priority_actions"],
            generated_at=result["generated_at"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{org_id}", response_model=list)
async def get_recommendation_history(org_id: str, limit: int = 10):
    """Retrieve past AI-generated recommendations for an org."""
    try:
        history = await llm_service.get_recommendation_history(org_id, limit)
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
