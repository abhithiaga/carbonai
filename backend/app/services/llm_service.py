import openai
import json
from datetime import datetime
from typing import Optional
from app.config import settings


class LLMService:
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.model = settings.LLM_MODEL
        self._history_store: dict = {}  # swap for DynamoDB in prod

    def build_recommendation_prompt(
        self,
        summary,
        focus_area: Optional[str],
        target_reduction_pct: float,
        extra_context: Optional[str],
    ) -> str:
        breakdown = json.dumps(summary.by_category if summary else {}, indent=2)
        focus_str = f"Focus specifically on {focus_area}." if focus_area else ""
        context_str = f"Additional context: {extra_context}" if extra_context else ""

        return f"""You are a sustainability expert AI. An organization wants to reduce their carbon footprint by {target_reduction_pct}%.

Their current emission breakdown by category (kg CO2e):
{breakdown}

Total emissions: {summary.total_kg_co2e if summary else "unknown"} kg CO2e

{focus_str} {context_str}

Respond ONLY with valid JSON in this exact structure:
{{
  "recommendations": [
    {{
      "title": "...",
      "description": "...",
      "category": "...",
      "estimated_reduction_kg_co2e": 0,
      "implementation_cost": "low|medium|high",
      "timeframe": "immediate|short_term|long_term",
      "priority": 1
    }}
  ],
  "estimated_reduction_kg_co2e": 0,
  "priority_actions": ["...", "...", "..."],
  "generated_at": "{datetime.utcnow().isoformat()}"
}}

Provide 5–8 specific, actionable recommendations ranked by impact.
"""

    async def complete(self, prompt: str) -> str:
        """Call OpenAI chat completion."""
        response = await openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY).chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are CarbonAI, an expert sustainability advisor. Always respond with valid JSON only."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=settings.LLM_MAX_TOKENS,
            temperature=0.3,
        )
        return response.choices[0].message.content

    def parse_recommendations(self, raw: str) -> dict:
        """Parse LLM JSON output, with fallback."""
        try:
            # Strip markdown code fences if present
            clean = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
            return json.loads(clean)
        except json.JSONDecodeError:
            return {
                "recommendations": [],
                "estimated_reduction_kg_co2e": 0.0,
                "priority_actions": ["Unable to parse AI response. Please retry."],
                "generated_at": datetime.utcnow().isoformat(),
            }

    async def get_recommendation_history(self, org_id: str, limit: int = 10) -> list:
        """Return stored recommendation history for an org."""
        return self._history_store.get(org_id, [])[-limit:]
