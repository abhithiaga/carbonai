from typing import Optional, List
from datetime import datetime

# Industry average emissions per employee (kg CO2e/year) — simplified benchmarks
INDUSTRY_BENCHMARKS = {
    "manufacturing": {"scope1": 15000, "scope2": 8000, "scope3": 40000, "total": 63000},
    "technology": {"scope1": 500, "scope2": 5000, "scope3": 20000, "total": 25500},
    "retail": {"scope1": 2000, "scope2": 4000, "scope3": 30000, "total": 36000},
    "finance": {"scope1": 300, "scope2": 2000, "scope3": 10000, "total": 12300},
    "healthcare": {"scope1": 3000, "scope2": 5000, "scope3": 15000, "total": 23000},
    "agriculture": {"scope1": 50000, "scope2": 2000, "scope3": 20000, "total": 72000},
    "energy": {"scope1": 80000, "scope2": 5000, "scope3": 30000, "total": 115000},
    "default": {"scope1": 5000, "scope2": 5000, "scope3": 20000, "total": 30000},
}

SCORE_HISTORY_STORE: dict = {}  # swap for DynamoDB


class ScoringService:

    def get_benchmark(self, industry: str) -> dict:
        key = industry.lower()
        if key not in INDUSTRY_BENCHMARKS:
            raise KeyError(f"No benchmark for {industry}")
        return {"industry": industry, "benchmarks_kg_co2e_per_employee": INDUSTRY_BENCHMARKS[key]}

    async def score(self, summary, benchmark_industry: Optional[str] = None) -> dict:
        """Compute a 0–100 sustainability score."""
        if not summary:
            raise ValueError("No emission summary provided")

        industry = (benchmark_industry or "default").lower()
        bench = INDUSTRY_BENCHMARKS.get(industry, INDUSTRY_BENCHMARKS["default"])

        # Score per scope vs benchmark (lower is better)
        scope_scores = {}
        for scope_key in ["scope1", "scope2", "scope3"]:
            actual = summary.by_scope.get(scope_key, 0)
            bench_val = bench.get(scope_key, 1)
            ratio = actual / max(bench_val, 1)
            # ratio < 1 = below benchmark = good; cap at 100
            scope_scores[scope_key] = min(100, max(0, round((1 - ratio + 0.5) * 100)))

        overall = round(sum(scope_scores.values()) / len(scope_scores), 1)

        grade = self._grade(overall)
        improvement_areas = [k for k, v in scope_scores.items() if v < 50]

        # Industry percentile (simplified)
        percentile = round(min(99, overall * 0.95), 1)

        result = {
            "org_id": summary.org_id,
            "overall_score": overall,
            "grade": grade,
            "subscores": scope_scores,
            "industry_percentile": percentile,
            "improvement_areas": improvement_areas,
            "score_history": SCORE_HISTORY_STORE.get(summary.org_id, []),
        }

        # Store in history
        if summary.org_id not in SCORE_HISTORY_STORE:
            SCORE_HISTORY_STORE[summary.org_id] = []
        SCORE_HISTORY_STORE[summary.org_id].append({
            "score": overall,
            "grade": grade,
            "timestamp": datetime.utcnow().isoformat(),
        })

        return result

    def _grade(self, score: float) -> str:
        if score >= 90: return "A+"
        if score >= 80: return "A"
        if score >= 70: return "B"
        if score >= 60: return "C"
        if score >= 50: return "D"
        return "F"

    async def get_leaderboard(self, industry: Optional[str], limit: int) -> List[dict]:
        """Return a mock leaderboard. In prod, query DynamoDB GSI."""
        board = []
        for org_id, history in SCORE_HISTORY_STORE.items():
            if history:
                latest = history[-1]
                board.append({"org_id": org_id, **latest})
        board.sort(key=lambda x: x["score"], reverse=True)
        return board[:limit]
