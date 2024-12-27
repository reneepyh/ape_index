from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional

class Interval(int, Enum):
    LAST_7_DAYS = 0
    LAST_30_DAYS = 1
    LAST_YEAR = 2
    ALL_TIME = 3

# Time Based
class TimeBasedData(BaseModel):
    total_volume: float = Field(None, description="Total sales volume.")
    average_price: float = Field(None, description="Average sale price.")
    transaction_count: int = Field(..., description="Number of transactions.")
    highest_price_token_id: str = Field(None, description="Token ID of the highest sale.")
    highest_price: float = Field(None, description="Highest sale price.")

class TimeBasedResponse(BaseModel):
    interval: Interval = Field(
        ..., 
        description="Interval for analysis: 0 = last 7 days, 1 = last 30 days, 2 = last year, 3 = all time."
    )
    data: list[TimeBasedData] = Field(..., description="List of time-based aggregated data.")

# Buyer Seller
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

# Marketplace Comparison
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

# Top Flip Token
class TopFlipTokenData(BaseModel):
    token_id: str = Field(..., description="Unique ID of the token.")
    total_profit: float = Field(..., description="Profit from the largest single flip transaction.")
    seller: str = Field(..., description="Wallet address of the seller.")

class TopFlipTokenResponse(BaseModel):
    interval: int = Field(..., description="Interval for analysis: 0 = last 7 days, 1 = last 30 days, 2 = last year, 3 = all time.")
    data: list[TopFlipTokenData] = Field(..., description="List of top 5 flip transactions with seller details.")

# Token Transaction
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

# NFT Metadata
class NFTMetadata(BaseModel):
    token_id: str = Field(..., description="The unique ID of the NFT token.")
    image_url: Optional[str] = Field(None, description="URL of the NFT image.")
    rarity_rank: Optional[int] = Field(None, description="The rarity rank of the NFT in the collection.")