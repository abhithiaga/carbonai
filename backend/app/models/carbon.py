from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum


class EmissionScope(str, Enum):
    SCOPE1 = "scope1"  # Direct emissions
    SCOPE2 = "scope2"  # Indirect – purchased energy
    SCOPE3 = "scope3"  # Value chain


class EmissionCategory(str, Enum):
    ENERGY = "energy"
    TRANSPORT = "transport"
    WASTE = "waste"
    SUPPLY_CHAIN = "supply_chain"
    MANUFACTURING = "manufacturing"
    AGRICULTURE = "agriculture"
    OTHER = "other"


class EmissionEntry(BaseModel):
    id: Optional[str] = None
    org_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    scope: EmissionScope
    category: EmissionCategory
    source: str                        # e.g. "Natural Gas Boiler"
    amount_kg_co2e: float              # kg CO2 equivalent
    unit: str = "kg CO2e"
    metadata: Optional[Dict] = {}


class EmissionSummary(BaseModel):
    org_id: str
    period_start: datetime
    period_end: datetime
    total_kg_co2e: float
    by_scope: Dict[str, float]
    by_category: Dict[str, float]
    trend_pct: Optional[float] = None  # % change vs prior period


class EmissionIngestRequest(BaseModel):
    org_id: str
    entries: List[EmissionEntry]


class EmissionQueryRequest(BaseModel):
    org_id: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    scope: Optional[EmissionScope] = None
    category: Optional[EmissionCategory] = None
