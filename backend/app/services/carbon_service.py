import uuid
from datetime import datetime, timedelta
from typing import Optional, List
from app.models.carbon import (
    EmissionEntry, EmissionSummary, EmissionIngestRequest,
    EmissionScope, EmissionCategory
)

# In-memory store — replace with boto3 DynamoDB calls in production
_store: List[dict] = []


class CarbonService:

    async def ingest(self, payload: EmissionIngestRequest) -> dict:
        count = 0
        for entry in payload.entries:
            record = entry.dict()
            record["id"] = str(uuid.uuid4())
            record["timestamp"] = record.get("timestamp") or datetime.utcnow()
            _store.append(record)
            count += 1
        return {"count": count}

    async def get_summary(
        self,
        org_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> EmissionSummary:
        entries = self._filter(org_id, start_date=start_date, end_date=end_date)

        total = sum(e["amount_kg_co2e"] for e in entries)
        by_scope = {}
        by_category = {}

        for e in entries:
            s = e.get("scope", "unknown")
            c = e.get("category", "unknown")
            by_scope[s] = by_scope.get(s, 0) + e["amount_kg_co2e"]
            by_category[c] = by_category.get(c, 0) + e["amount_kg_co2e"]

        now = datetime.utcnow()
        period_start = start_date or (now - timedelta(days=365))
        period_end = end_date or now

        # Trend vs prior period
        prior_start = period_start - (period_end - period_start)
        prior_entries = self._filter(org_id, start_date=prior_start, end_date=period_start)
        prior_total = sum(e["amount_kg_co2e"] for e in prior_entries)
        trend = None
        if prior_total > 0:
            trend = round(((total - prior_total) / prior_total) * 100, 2)

        return EmissionSummary(
            org_id=org_id,
            period_start=period_start,
            period_end=period_end,
            total_kg_co2e=total,
            by_scope=by_scope,
            by_category=by_category,
            trend_pct=trend,
        )

    async def list_entries(
        self,
        org_id: str,
        scope: Optional[EmissionScope] = None,
        category: Optional[EmissionCategory] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[EmissionEntry]:
        entries = self._filter(org_id, scope=scope, category=category)
        sliced = entries[offset: offset + limit]
        return [EmissionEntry(**e) for e in sliced]

    async def delete_entry(self, entry_id: str):
        global _store
        before = len(_store)
        _store = [e for e in _store if e.get("id") != entry_id]
        if len(_store) == before:
            raise ValueError(f"Entry {entry_id} not found")

    async def get_trend(self, org_id: str, months: int) -> List[dict]:
        """Return monthly totals for the last N months."""
        now = datetime.utcnow()
        result = []
        for i in range(months - 1, -1, -1):
            month_start = (now.replace(day=1) - timedelta(days=30 * i)).replace(day=1)
            month_end = (month_start + timedelta(days=32)).replace(day=1)
            entries = self._filter(org_id, start_date=month_start, end_date=month_end)
            total = sum(e["amount_kg_co2e"] for e in entries)
            result.append({
                "month": month_start.strftime("%Y-%m"),
                "total_kg_co2e": round(total, 2),
            })
        return result

    def _filter(
        self,
        org_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        scope: Optional[EmissionScope] = None,
        category: Optional[EmissionCategory] = None,
    ) -> List[dict]:
        results = [e for e in _store if e.get("org_id") == org_id]
        if start_date:
            results = [e for e in results if e.get("timestamp", datetime.min) >= start_date]
        if end_date:
            results = [e for e in results if e.get("timestamp", datetime.max) <= end_date]
        if scope:
            results = [e for e in results if e.get("scope") == scope]
        if category:
            results = [e for e in results if e.get("category") == category]
        return results
