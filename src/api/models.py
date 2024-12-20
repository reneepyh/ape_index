from datetime import datetime
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

class TokenRequest(BaseModel):
    interval: Interval = Field(
        ..., 
        description="Interval for analysis: 0 = last 7 days, 1 = last 30 days, 2 = last year, 3 = all time."
    )
    token_id: str = Field(
        ..., 
        description="Token ID for token-specific analysis."
    )

class AddressRequest(BaseModel):
    address: str = Field(
        ..., 
        description="Wallet address for which to retrieve all held token IDs."
    )

# TimeBased
class TimeBasedData(BaseModel):
    total_volume: float = Field(None, description="Total sales volume.")
    average_price: float = Field(None, description="Average sale price.")
    transaction_count: int = Field(..., description="Number of transactions.")

class TimeBasedResponse(BaseModel):
    interval: Interval = Field(
        ..., 
        description="Interval for analysis: 0 = last 7 days, 1 = last 30 days, 2 = last year, 3 = all time."
    )
    data: list[TimeBasedData] = Field(..., description="List of time-based aggregated data.")

# BuyerSeller
class BuyerSellerData(BaseModel):
    address: str = Field(..., description="Wallet address of the buyer or seller.")
    total_volume: float = Field(..., description="Total transaction volume.")
    transaction_count: int = Field(..., description="Number of transactions.")

class BuyerSellerResponse(BaseModel):
    interval: Interval = Field(
        ..., 
        description="Interval for analysis: 0 = last 7 days, 1 = last 30 days, 2 = last year, 3 = all time."
    )
    top_buyers: list[BuyerSellerData] = Field(..., description="List of top buyers.")
    top_sellers: list[BuyerSellerData] = Field(..., description="List of top sellers.")

# MarketplaceComparison
class MarketplaceData(BaseModel):
    marketplace: str = Field(..., description="Name of the marketplace.")
    total_volume: float = Field(..., description="Total transaction volume on the marketplace.")
    average_price: float = Field(..., description="Average sale price on the marketplace.")
    transaction_count: int = Field(..., description="Number of transactions on the marketplace.")

class MarketplaceComparisonResponse(BaseModel):
    interval: Interval = Field(
        ..., 
        description="Interval for comparison: 0 = last 7 days, 1 = last 30 days, 2 = last year, 3 = all time."
    )
    data: list[MarketplaceData] = Field(..., description="List of marketplace comparison data.")

# TokenTransaction
class TokenTransactionData(BaseModel):
    sold_date: datetime = Field(..., description="Date and time of the transaction.")
    price: float = Field(..., description="Sale price of the token.")
    transaction_hash: str = Field(..., description="Unique transaction hash for this sale.")
    buyer_address: str = Field(..., description="Wallet address of the buyer.")

class TokenTransactionResponse(BaseModel):
    token_id: str = Field(..., description="Unique ID of the token.")
    interval: Interval = Field(
        ..., 
        description="Interval for analysis: 0 = last 7 days, 1 = last 30 days, 2 = last year, 3 = all time."
    )
    data: list[TokenTransactionData] = Field(..., description="List of transaction data for the token.")

# ResaleAnalysis
class ResaleData(BaseModel):
    token_id: str = Field(..., description="Unique ID of the token.")
    resale_count: int = Field(..., description="Number of resales.")
    total_profit: float = Field(..., description="Total profit from resales.")
    average_profit: float = Field(..., description="Average profit per resale.")

class ResaleAnalysisResponse(BaseModel):
    interval: Interval = Field(
        ..., 
        description="Interval for analysis: 0 = last 7 days, 1 = last 30 days, 2 = last year, 3 = all time."
    )
    data: list[ResaleData] = Field(..., description="List of resale and flipping behavior data.")

# TokenOwned
class TokenOwnedResponse(BaseModel):
    address: str = Field(
        ..., 
        description="Wallet address for which the token IDs are retrieved."
    )
    token_ids: list[str] = Field(
        ..., 
        description="List of token IDs held by the given address."
    )
