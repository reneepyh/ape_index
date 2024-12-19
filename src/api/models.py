from pydantic import BaseModel, Field
from enum import Enum

class Interval(int, Enum):
    LAST_7_DAYS = 0
    LAST_30_DAYS = 1
    LAST_YEAR = 2
    ALL_TIME = 3

class GeneralRequest(BaseModel):
    interval: Interval = Field(
        ..., 
        description="Interval for analysis: 0 = last 7 days, 1 = last 30 days, 2 = last year, 3 = all time."
    )

class TokenSpecificRequest(BaseModel):
    interval: Interval = Field(
        ..., 
        description="Interval for analysis: 0 = last 7 days, 1 = last 30 days, 2 = last year, 3 = all time."
    )
    token_id: str = Field(
        ..., 
        description="Token ID for token-specific analysis."
    )

class PriceVolumeData(BaseModel):
    date: str = Field(..., description="Date in YYYY-MM-DD format.")
    total_volume: float = Field(..., description="Total sales volume.")
    average_price: float = Field(..., description="Average sale price.")
    transaction_count: int = Field(..., description="Number of transactions.")

class PriceVolumeResponse(BaseModel):
    interval: Interval = Field(
        ..., 
        description="Interval for aggregation: 0 = last 7 days, 1 = last 30 days, 2 = last year, 3 = all time."
    )
    data: list[PriceVolumeData] = Field(..., description="List of aggregated data.")
