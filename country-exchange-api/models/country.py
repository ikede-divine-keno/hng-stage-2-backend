from sqlalchemy import Column, Integer, String, Float, DateTime, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Country(Base):
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    capital = Column(String(100), nullable=True)
    region = Column(String(50), nullable=True)
    population = Column(Integer, nullable=False)
    currency_code = Column(String(10), nullable=True)  # Can be null
    exchange_rate = Column(Float, nullable=True)      # Can be null
    estimated_gdp = Column(Float, nullable=True)
    flag_url = Column(String(255), nullable=True)
    last_refreshed_at = Column(DateTime, default=func.now(), onupdate=func.now())