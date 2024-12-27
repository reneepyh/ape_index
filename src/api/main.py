import os, requests, json
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from src.api.db.database import SessionLocal
import src.api.db.models as db_models
import src.api.models as api_models

load_dotenv()
app = FastAPI(
    title="Bored Ape Yacht Club NFT Analytics API"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.get("/api/v1/time-based-data", response_model=api_models.TimeBasedResponse, 
         summary="Get time-based data", description="Get time-based data in requested interval, including highest sale token ID.")
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

    #highest price
    highest_price_query = db.query(
        db_models.Transaction.token_id.label('token_id'),
        db_models.Transaction.price.label('highest_price')
    ).order_by(db_models.Transaction.price.desc())

    if start_time:
        highest_price_query = highest_price_query.filter(db_models.Transaction.time >= start_time)

    highest_price_result = highest_price_query.first()

    total_volume = float(result.total_volume or 0)
    average_price = float(result.average_price or 0)
    transaction_count = result.transaction_count or 0
    highest_price_token_id = str(highest_price_result.token_id) if highest_price_result else "N/A"
    highest_price = float(highest_price_result.highest_price) if highest_price_result else 0.0

    data = [
        api_models.TimeBasedData(
            total_volume=total_volume,
            average_price=average_price,
            transaction_count=transaction_count,
            highest_price_token_id=highest_price_token_id,
            highest_price=highest_price
        )
    ]

    return api_models.TimeBasedResponse(interval=interval, data=data)

@app.get("/api/v1/top-buyers-sellers", response_model=api_models.BuyerSellerResponse, 
         summary="Get top buyers and sellers for total volume", description="Get top 5 buyers and sellers for total volume in requested interval")
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

@app.get(
    "/api/v1/marketplace-comparison",
    response_model=api_models.MarketplaceComparisonResponse,
    summary="Compare marketplaces based on total volume and transaction count",
    description="Get comparison data across marketplaces for total volume, average price, and transaction count"
)
async def marketplace_comparison_data(
    interval: int = Query(..., description="0 = last 7 days, 1 = last 30 days, 2 = last year, 3 = all time"),
    db: Session = Depends(get_db)
):
    if interval not in VALID_INTERVALS:
        raise HTTPException(status_code=400, detail=f"Invalid interval '{interval}'.")

    start_time = get_interval_date_range(interval)

    query = (
        db.query(
            db_models.Market.name.label('marketplace'),
            func.sum(db_models.Transaction.price).label('total_volume'),
            func.avg(db_models.Transaction.price).label('average_price'),
            func.count(db_models.Transaction.transaction_id).label('transaction_count')
        )
        .join(
            db_models.Market,
            db_models.Transaction.market_id == db_models.Market.id
        )
    )

    if start_time:
        query = query.filter(db_models.Transaction.time >= start_time)

    data = (
        query
        .group_by(db_models.Market.name)
        .order_by(func.sum(db_models.Transaction.price).desc())
        .all()
    )

    return api_models.MarketplaceComparisonResponse(
        interval=interval,
        data=[
            api_models.MarketplaceData(
                marketplace=market.marketplace,
                total_volume=float(market.total_volume or 0),
                average_price=float(market.average_price or 0),
                transaction_count=market.transaction_count or 0
            )
            for market in data
        ]
    )

@app.get(
    "/api/v1/top-flip-token",
    response_model=api_models.TopFlipTokenResponse,
    summary="Top 5 tokens by largest single flip profit",
    description="Get the Top 5 tokens with the largest single resale price difference, including the seller"
)
async def top_flip_token(
    interval: int = Query(..., description="0 = last 7 days, 1 = last 30 days, 2 = last year, 3 = all time"),
    db: Session = Depends(get_db)
):
    if interval not in VALID_INTERVALS:
        raise HTTPException(status_code=400, detail=f"Invalid interval '{interval}'.")

    start_time = get_interval_date_range(interval)

    resale_subq = (
        db.query(
            db_models.Transaction.token_id.label('token_id'),
            db_models.Transaction.time.label('time'),
            db_models.Transaction.price.label('price'),
            func.lag(db_models.Transaction.price)
                .over(
                    partition_by=db_models.Transaction.token_id,
                    order_by=[
                        db_models.Transaction.time,
                        db_models.Transaction.transaction_id
                    ]
                )
                .label('previous_price'),
            func.lag(db_models.Transaction.buyer_id)
                .over(
                    partition_by=db_models.Transaction.token_id,
                    order_by=[
                        db_models.Transaction.time,
                        db_models.Transaction.transaction_id
                    ]
                )
                .label('seller_id')
        )
        .subquery('resale_subq')
    )

    price_diff = (resale_subq.c.price - resale_subq.c.previous_price).label('price_difference')

    query = (
        db.query(
            resale_subq.c.token_id.label('token_id'),
            price_diff,
            db_models.Address.address.label('seller')
        )
        .join(
            db_models.Address,
            db_models.Address.id == resale_subq.c.seller_id
        )
        .filter(resale_subq.c.previous_price.isnot(None))
        .filter(resale_subq.c.seller_id.isnot(None))
    )

    if start_time is not None:
        query = query.filter(resale_subq.c.time >= start_time)

    data = (
        query
        .order_by((price_diff).desc())
        .limit(5)
        .all()
    )

    return api_models.TopFlipTokenResponse(
        interval=interval,
        data=[
            api_models.TopFlipTokenData(
                token_id=str(record.token_id),
                total_profit=float(record.price_difference or 0),
                seller=record.seller
            )
            for record in data
        ]
    )

@app.get(
    "/api/v1/token-transaction",
    response_model=api_models.TokenTransactionResponse,
    summary="Get transactions for a specific token",
    description="Retrieve transaction history for a specific token within the requested interval"
)
async def token_transaction(
    token_id: str = Query(..., description="Token ID (0-9999) for transaction history"),
    interval: int = Query(..., description="Interval for analysis: 0 = last 7 days, 1 = last 30 days, 2 = last year, 3 = all time"),
    db: Session = Depends(get_db)
):
    if interval not in VALID_INTERVALS:
        raise HTTPException(status_code=400, detail=f"Invalid interval '{interval}'.")

    try:
        token_id_int = int(token_id)
        if token_id_int < 0 or token_id_int > 9999:
            raise ValueError("Token ID must be between 0 and 9999.")
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Token ID must be an integer between 0 and 9999."
        )

    start_time = get_interval_date_range(interval)

    query = (
        db.query(
            db_models.Transaction.time.label('sold_date'),
            db_models.Transaction.price.label('price'),
            db_models.Transaction.transaction_hash.label('transaction_hash'),
            db_models.Address.address.label('buyer_address')
        )
        .join(
            db_models.Address,
            db_models.Transaction.buyer_id == db_models.Address.id
        )
        .filter(db_models.Transaction.token_id == token_id)
    )

    if start_time:
        query = query.filter(db_models.Transaction.time >= start_time)

    data = query.order_by(db_models.Transaction.time.desc()).all()

    return api_models.TokenTransactionResponse(
        token_id=token_id,
        interval=interval,
        data=[
            api_models.TokenTransactionData(
                sold_date=record.sold_date,
                price=float(record.price or 0),
                transaction_hash=record.transaction_hash,
                buyer_address=record.buyer_address
            )
            for record in data
        ]
    )

@app.get("/api/v1/nft-details", response_model=api_models.NFTMetadata)
async def get_nft_details(token_id: str = Query(..., description="Token ID (0-9999) for NFT details")):
    try:
        url = f"https://deep-index.moralis.io/api/v2.2/nft/0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D/{token_id}"
        headers = {
            "accept": "application/json",
            "X-API-Key": os.getenv('MORALIS_APIKEY')
        }
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to fetch NFT details")

        data = response.json()

        if not data.get("token_id"):
            raise HTTPException(status_code=404, detail="NFT not found")

        metadata_raw = data.get("metadata", "{}")
        metadata = {}
        try:
            metadata = json.loads(metadata_raw)
        except json.JSONDecodeError:
            metadata = {}

        image_url = metadata.get("image") or data.get("normalized_metadata", {}).get("image")
        if image_url and image_url.startswith("ipfs://"):
            image_url = image_url.replace("ipfs://", "https://ipfs.io/ipfs/")
       
        rarity_rank = data.get("rarity_rank")

        return api_models.NFTMetadata(
            token_id=data.get("token_id"),
            image_url=image_url,
            rarity_rank=rarity_rank
        )

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))