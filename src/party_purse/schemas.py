"""Pydantic schemas for data validation"""

from pydantic import BaseModel, Field
from typing import List, Optional


class Funder(BaseModel):
    """Individual funder record"""

    party: str = Field(description="Party name")
    funder: str = Field(description="Donor name with type")
    amount_gbp: int = Field(description="Amount in GBP", ge=0)
    percentage: float = Field(description="Percentage of party total", ge=0, le=100)


class FundingResponse(BaseModel):
    """Complete funding data response"""

    funders: List[Funder]
    data_quality_note: Optional[str] = None
    data_source: str = "Electoral Commission"
    reporting_period: Optional[str] = None
