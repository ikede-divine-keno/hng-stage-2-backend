from pydantic import BaseModel, Field, validator
from fastapi import HTTPException
from typing import Optional
from datetime import datetime

class CountryBase(BaseModel):
    name: str = Field(..., min_length=1)
    capital: Optional[str] = None
    region: Optional[str] = None
    population: int = Field(..., gt=0)
    currency_code: str | None = Field(..., description="Required, can be null")
    exchange_rate: float | None = Field(..., description="Required, can be null")
    flag_url: Optional[str] = None

    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise HTTPException(400, detail={
                "error": "Validation failed",
                "details": {"name": "is required"}
            })
        return v.strip().title()

    @validator('population')
    def validate_population(cls, v):
        if v is None or v <= 0:
            raise HTTPException(400, detail={
                "error": "Validation failed",
                "details": {"population": "is required and must be > 0"}
            })
        return v

    """@validator('currency_code')
    def validate_currency_code(cls, v):
        if v is None:
            raise HTTPException(400, detail={
                "error": "Validation failed",
                "details": {"currency_code": "is required"}
            })
        return v"""

class CountryCreate(CountryBase):
    estimated_gdp: float | None = Field(None, exclude=True)

class CountryResponse(BaseModel):
    id: int
    name: str
    capital: Optional[str] = None
    region: Optional[str] = None
    population: int = 0  # ← Allow 0
    currency_code: Optional[str] = None
    exchange_rate: Optional[float] = None
    estimated_gdp: Optional[float] = None
    flag_url: Optional[str] = None
    last_refreshed_at: datetime

    class Config:
        from_attributes = True