from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime
from app.models.carbon import (
    EmissionEntry, EmissionSummary,
    EmissionIngestRequest, EmissionQueryRequest, EmissionScope, EmissionCategory
)
from app.services.carbon_service import CarbonService

router = APIRouter()
carbon_service = CarbonService()


@router.post("/ingest", response_model=dict)
async def ingest_emissions(payload: EmissionIngestRequest):
    """Bulk ingest emission entries for an organization."""
    try:
        result = await carbon_service.ingest(payload)
        return {"status": "ok", "inserted": result["count"], "org_id": payload.org_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary/{org_id}", response_model=EmissionSummary)
async def get_summary(
    org_id: str,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
):
    """Get aggregate emission summary for an org, optionally filtered by date range."""
    try:
        summary = await carbon_service.get_summary(org_id, start_date, end_date)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/entries/{org_id}", response_model=List[EmissionEntry])
async def list_entries(
    org_id: str,
    scope: Optional[EmissionScope] = Query(None),
    category: Optional[EmissionCategory] = Query(None),
    limit: int = Query(100, le=1000),
    offset: int = Query(0),
):
    """List individual emission entries with optional filters."""
    try:
        entries = await carbon_service.list_entries(
            org_id=org_id, scope=scope, category=category, limit=limit, offset=offset
        )
        return entries
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/entries/{entry_id}", response_model=dict)
async def delete_entry(entry_id: str):
    """Delete a single emission entry by ID."""
    try:
        await carbon_service.delete_entry(entry_id)
        return {"status": "deleted", "id": entry_id}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Entry {entry_id} not found")


@router.get("/trend/{org_id}", response_model=dict)
async def get_trend(
    org_id: str,
    months: int = Query(12, ge=1, le=60),
):
    """Get monthly emission trend data for charting."""
    try:
        trend = await carbon_service.get_trend(org_id, months)
        return {"org_id": org_id, "months": months, "data": trend}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
