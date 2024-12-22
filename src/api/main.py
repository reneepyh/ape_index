from fastapi import FastAPI, HTTPException, Query, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from typing import List
from src.api.db.database import SessionLocal
import src.api.db.models as db_models
import src.api.models as api_models

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

VALID_INTERVALS = [0, 1, 2, 3]

def get_interval_date_range(interval: int):
    interval_map = {
        0: datetime.now(timezone.utc) - timedelta(days=7),
        1: datetime.now(timezone.utc) - timedelta(days=30),
        2: datetime.now(timezone.utc) - timedelta(days=365),
        3: None,
    }
    return interval_map.get(interval)

@app.get("/api/v1/time-based-data", response_model=api_models.TimeBasedResponse)
async def time_based_data(
    interval: int = Query(..., description="0 = last 7 days, 1 = last 30 days, 2 = last year, 3 = all time"),
    db: Session = Depends(get_db)
):
    if interval not in VALID_INTERVALS:
        raise HTTPException(status_code=400, detail=f"Invalid interval '{interval}'. Valid values are: {VALID_INTERVALS}")
    
    start_time = get_interval_date_range(interval)

    query = db.query(
        func.sum(db_models.Transaction.price).label('total_volume'),
        func.avg(db_models.Transaction.price).label('average_price'),
        func.count(db_models.Transaction.transaction_id).label('transaction_count')
    )

    if start_time:
        query = query.filter(db_models.Transaction.time >= start_time)

    result = query.one()

    data = [
        api_models.TimeBasedData(
            total_volume=float(result.total_volume or 0),
            average_price=float(result.average_price or 0),
            transaction_count=result.transaction_count or 0
        )
    ]

    return api_models.TimeBasedResponse(interval=interval, data=data)

@app.get("/api/v1/top-buyers-sellers", response_model=api_models.BuyerSellerResponse)
async def top_buyers_sellers_data(request: api_models.GeneralRequest):
    pass

@app.get("/api/v1/marketplace-comparison", response_model=api_models.MarketplaceComparisonResponse)
async def marketplace_comparison_data(request: api_models.GeneralRequest):
    pass

@app.get("/api/v1/resale-data", response_model=api_models.ResaleAnalysisResponse)
async def resale_data(request: api_models.GeneralRequest):
    pass

@app.get("/api/v1/token-transaction", response_model=api_models.TokenTransactionResponse)
async def token_transaction(request: api_models.TokenRequest):
    pass

@app.get("/api/v1/token-owned", response_model=api_models.TokenOwnedResponse)
async def get_token_owned(request: api_models.AddressRequest):
    pass
