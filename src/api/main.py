from fastapi import FastAPI, HTTPException
import src.api.models as models

app = FastAPI()

@app.get("api/v1/price-volumn", response_model=models.PriceVolumeResponse)
async def get_price_volume(request: models.GeneralRequest):
    return models.PriceVolumeResponse(
        interval=request.interval,
        data=[
            models.PriceVolumeData(
                date="2024-12-19",
                total_volume=100.25,
                average_price=35234,
                transaction_count=20
            )
        ]
    )

