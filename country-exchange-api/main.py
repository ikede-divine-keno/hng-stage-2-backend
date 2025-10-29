import asyncio
import os
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy import select, func, text
from datetime import datetime

from database import engine, get_db
from models.country import Base, Country
from schemas.country import CountryResponse
from services.fetch import fetch_countries, fetch_exchange_rates, ExternalAPIError
from services.image import generate_summary_image, IMAGE_PATH
from crud.country import upsert_countries
from utils.errors import not_found

app = FastAPI(title="Country Currency & Exchange API")

# CORS
origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
os.makedirs("cache", exist_ok=True)
app.mount("/cache", StaticFiles(directory="cache"), name="cache")

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.post("/countries/refresh")
async def refresh(background_tasks: BackgroundTasks, db=Depends(get_db)):
    try:
        countries_data, rates = await asyncio.gather(
            fetch_countries(),
            fetch_exchange_rates()
        )
    except ExternalAPIError as e:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "External data source unavailable",
                "details": f"Could not fetch data from {e.api_name}"
            }
        )

    global_timestamp = datetime.utcnow()
    await upsert_countries(db, countries_data, rates, global_timestamp)

    top5 = (await db.execute(
        select(Country).order_by(Country.estimated_gdp.desc()).limit(5)
    )).scalars().all()
    total = (await db.execute(select(func.count()).select_from(Country))).scalar_one()

    background_tasks.add_task(generate_summary_image, total, top5, global_timestamp)
    return {"status": "refresh completed", "total": len(countries_data)}

# FIXED: /image BEFORE /{name}
@app.get("/countries/image")
async def get_image():
    if not os.path.exists(IMAGE_PATH):
        raise HTTPException(status_code=404, detail={"error": "Summary image not found"})
    return FileResponse(IMAGE_PATH, media_type="image/png", filename="summary.png")

@app.get("/countries", response_model=list[CountryResponse])
async def get_countries(
    region: str | None = Query(None),
    currency: str | None = Query(None),
    sort: str | None = Query(None),
    db=Depends(get_db)
):
    query = select(Country)
    if region:
        query = query.where(Country.region == region)
    if currency:
        query = query.where(Country.currency_code == currency)
    if sort == "gdp_desc":
        query = query.order_by(Country.estimated_gdp.desc())  # This was correct

    result = await db.execute(query)
    return result.scalars().all()  # This returns list → correct

@app.get("/countries/{name}", response_model=CountryResponse)
async def get_country(name: str, db=Depends(get_db)):
    result = await db.execute(
        select(Country).where(text("LOWER(name) = LOWER(:name)")).params(name=name)
    )
    country = result.scalar_one_or_none()
    if not country:
        return not_found()
    return country

@app.delete("/countries/{name}")
async def delete_country(name: str, db=Depends(get_db)):
    result = await db.execute(
        select(Country).where(text("LOWER(name) = LOWER(:name)")).params(name=name)
    )
    country = result.scalar_one_or_none()
    if not country:
        return not_found()
    await db.delete(country)
    await db.commit()
    return {"status": "deleted"}

@app.get("/status")
async def status(db=Depends(get_db)):
    total = (await db.execute(select(func.count()).select_from(Country))).scalar_one()
    last = (await db.execute(select(func.max(Country.last_refreshed_at)))).scalar_one()
    return {
        "total_countries": total,
        "last_refreshed_at": last.isoformat() + "Z" if last else None
    }