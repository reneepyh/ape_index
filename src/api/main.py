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

@app.get("/api/v1/time-based-data", response_model=api_models.TimeBasedResponse, summary="Get time-based data", description="Get time-based data in requested interval")
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

@app.get("/api/v1/top-buyers-sellers", response_model=api_models.BuyerSellerResponse, summary="Get top buyers and sellers for total volume", description="Get top 5 buyers and sellers for total volume in requested interval")
async def top_buyers_sellers_data(
    interval: int = Query(..., description="0 = last 7 days, 1 = last 30 days, 2 = last year, 3 = all time"),
    db: Session = Depends(get_db)
):

    if interval not in VALID_INTERVALS:
        raise HTTPException(status_code=400, detail=f"Invalid interval '{interval}'.")
    start_time = get_interval_date_range(interval)

    ## Buyers
    buyers_query = (
        db.query(
            db_models.Address.address.label('address'),
            func.sum(db_models.Transaction.price).label('total_volume'),
            func.count(db_models.Transaction.transaction_id).label('transaction_count'),
        )
        .join(
            db_models.Address,
            db_models.Transaction.buyer_id == db_models.Address.id
        )
    )
    
    if start_time:
        buyers_query = buyers_query.filter(db_models.Transaction.time >= start_time)

    buyers = (
        buyers_query
        .group_by(db_models.Address.address)
        .order_by(func.sum(db_models.Transaction.price).desc())
        .limit(5)
        .all()
    )

    ## Sellers
    # -- Step (1): Subquery with LAG
    sellers_subq = (
        db.query(
            db_models.Transaction.token_id.label('token_id'),
            db_models.Transaction.time.label('time'),
            db_models.Transaction.price.label('price'),
            func.lag(db_models.Transaction.buyer_id)
                .over(
                    partition_by=db_models.Transaction.token_id,
                    order_by=db_models.Transaction.time
                )
                .label('seller_id')
        )
    ).subquery('sellers_subq')

    # -- Step (2): Outer query
    sellers_query = (
        db.query(
            db_models.Address.address.label('address'),
            func.sum(sellers_subq.c.price).label('total_volume'),
            func.count(sellers_subq.c.price).label('transaction_count')
        )
        .join(
            db_models.Transaction,
            (db_models.Transaction.token_id == sellers_subq.c.token_id)
            & (db_models.Transaction.time == sellers_subq.c.time)
        )
        .join(
            db_models.Address,
            db_models.Address.id == sellers_subq.c.seller_id
        )
        .filter(sellers_subq.c.seller_id.isnot(None))
    )

    if start_time:
        sellers_query = sellers_query.filter(db_models.Transaction.time >= start_time)

    sellers = (
        sellers_query
        .group_by(db_models.Address.address)
        .order_by(func.sum(sellers_subq.c.price).desc())
        .limit(5)
        .all()
    )

    return api_models.BuyerSellerResponse(
        interval=interval,
        top_buyers=[
            api_models.BuyerSellerData(
                address=buyer.address,
                total_volume=float(buyer.total_volume or 0),
                transaction_count=buyer.transaction_count or 0
            )
            for buyer in buyers
        ],
        top_sellers=[
            api_models.BuyerSellerData(
                address=seller.address,
                total_volume=float(seller.total_volume or 0),
                transaction_count=seller.transaction_count or 0
            )
            for seller in sellers
        ]
    )

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
