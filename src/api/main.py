from fastapi import FastAPI, HTTPException
import src.api.models as models

app = FastAPI()

@app.get("/api/v1/time-based-data", response_model=models.TimeBasedResponse)
async def time_based_data(request: models.GeneralRequest):
    pass

@app.get("/api/v1/top-buyers-sellers", response_model=models.BuyerSellerResponse)
async def top_buyers_sellers_data(request: models.GeneralRequest):
    pass

@app.get("/api/v1/marketplace-comparison", response_model=models.MarketplaceComparisonResponse)
async def marketplace_comparison_data(request: models.GeneralRequest):
    pass

@app.get("/api/v1/resale-data", response_model=models.ResaleAnalysisResponse)
async def resale_data(request: models.GeneralRequest):
    pass

@app.get("/api/v1/token-transaction", response_model=models.TokenTransactionResponse)
async def token_transaction(request: models.TokenRequest):
    pass

@app.get("/api/v1/token-owned", response_model=models.TokenOwnedResponse)
async def get_token_owned(request: models.AddressRequest):
    pass
