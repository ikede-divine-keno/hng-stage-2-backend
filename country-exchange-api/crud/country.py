from sqlalchemy import select, update
from models.country import Country
import random

async def upsert_countries(session, countries_data, rates, global_timestamp):
    existing = {c.name.lower(): c for c in (await session.execute(select(Country))).scalars().all()}

    for data in countries_data:
        name = data["name"]
        key = name.lower()

        currencies = data.get("currencies") or []
        currency_code = currencies[0]["code"] if currencies else None

        exchange_rate = None
        if currency_code and currency_code in rates:
            exchange_rate = rates[currency_code]

        estimated_gdp = None
        if exchange_rate and exchange_rate > 0:
            multiplier = random.uniform(1000, 2000)
            estimated_gdp = data["population"] * multiplier / exchange_rate
        elif currency_code is None:
            estimated_gdp = 0

        country_data = {
            "name": name,
            "capital": data.get("capital"),
            "region": data.get("region"),
            "population": data["population"],
            "currency_code": currency_code,
            "exchange_rate": exchange_rate,
            "estimated_gdp": estimated_gdp,
            "flag_url": data.get("flag"),
            "last_refreshed_at": global_timestamp
        }

        if key in existing:
            stmt = update(Country).where(Country.name == name).values(**country_data)
            await session.execute(stmt)
        else:
            country = Country(**country_data)
            session.add(country)

    await session.commit()