from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import httpx
from datetime import datetime

app = FastAPI(
    title="Global Trade Statistics API",
    description="Global trade data including exports, imports, trade balance, and top trading nations for 190+ countries. Powered by World Bank Open Data.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

WB_BASE = "https://api.worldbank.org/v2"

INDICATORS = {
    "exports_usd":      {"id": "NE.EXP.GNFS.CD",  "name": "Exports of Goods & Services",    "unit": "Current USD"},
    "imports_usd":      {"id": "NE.IMP.GNFS.CD",  "name": "Imports of Goods & Services",    "unit": "Current USD"},
    "exports_pct":      {"id": "NE.EXP.GNFS.ZS",  "name": "Exports of Goods & Services",    "unit": "% of GDP"},
    "imports_pct":      {"id": "NE.IMP.GNFS.ZS",  "name": "Imports of Goods & Services",    "unit": "% of GDP"},
    "trade_pct_gdp":    {"id": "NE.TRD.GNFS.ZS",  "name": "Trade (Exports + Imports)",       "unit": "% of GDP"},
    "current_account":  {"id": "BN.CAB.XOKA.CD",  "name": "Current Account Balance",         "unit": "Current USD"},
    "merch_exports":    {"id": "TX.VAL.MRCH.CD.WT","name": "Merchandise Exports",             "unit": "Current USD"},
    "merch_imports":    {"id": "TM.VAL.MRCH.CD.WT","name": "Merchandise Imports",             "unit": "Current USD"},
    "fdi_inflows":      {"id": "BX.KLT.DINV.CD.WD","name": "FDI Net Inflows",                "unit": "Current USD"},
}

COUNTRIES = {
    "WLD": "World",
    "USA": "United States",
    "CHN": "China",
    "DEU": "Germany",
    "JPN": "Japan",
    "GBR": "United Kingdom",
    "FRA": "France",
    "KOR": "South Korea",
    "IND": "India",
    "NLD": "Netherlands",
    "BEL": "Belgium",
    "HKG": "Hong Kong",
    "SGP": "Singapore",
    "ITA": "Italy",
    "CAN": "Canada",
    "MEX": "Mexico",
    "RUS": "Russia",
    "TWN": "Taiwan",
    "ESP": "Spain",
    "SAU": "Saudi Arabia",
    "UAE": "United Arab Emirates",
    "AUS": "Australia",
    "BRA": "Brazil",
    "THA": "Thailand",
    "MYS": "Malaysia",
    "VNM": "Vietnam",
    "CHE": "Switzerland",
    "POL": "Poland",
    "IDN": "Indonesia",
    "ZAF": "South Africa",
}


async def fetch_wb_country(country_code: str, indicator_id: str, limit: int = 10):
    url = f"{WB_BASE}/country/{country_code}/indicator/{indicator_id}"
    params = {"format": "json", "mrv": limit, "per_page": limit}
    async with httpx.AsyncClient(timeout=15) as client:
        res = await client.get(url, params=params)
        data = res.json()
    if not data or len(data) < 2:
        return []
    records = data[1] or []
    return [
        {"year": str(r["date"]), "value": r["value"]}
        for r in records
        if r.get("value") is not None
    ]


async def fetch_wb_all_countries(indicator_id: str):
    url = f"{WB_BASE}/country/all/indicator/{indicator_id}"
    params = {"format": "json", "mrv": 1, "per_page": 300}
    async with httpx.AsyncClient(timeout=20) as client:
        res = await client.get(url, params=params)
        data = res.json()
    if not data or len(data) < 2:
        return []
    records = data[1] or []
    results = []
    for r in records:
        if r.get("value") is not None and r.get("countryiso3code"):
            results.append({
                "country_code": r["countryiso3code"],
                "country": r["country"]["value"],
                "year": str(r["date"]),
                "value": r["value"],
            })
    return results


@app.get("/")
def root():
    return {
        "api": "Global Trade Statistics API",
        "version": "1.0.0",
        "provider": "GlobalData Store",
        "source": "World Bank Open Data",
        "endpoints": [
            "/summary", "/exports", "/imports", "/trade-balance",
            "/trade-gdp", "/merchandise", "/fdi", "/top-exporters", "/top-importers"
        ],
        "countries": list(COUNTRIES.keys()),
        "updated_at": datetime.utcnow().isoformat() + "Z",
    }


@app.get("/summary")
async def summary(
    country: str = Query(default="WLD", description="ISO3 country code"),
    limit: int = Query(default=5, ge=1, le=30)
):
    """All trade indicators for a country"""
    country = country.upper()
    results = {}
    for key, meta in INDICATORS.items():
        results[key] = await fetch_wb_country(country, meta["id"], limit)
    formatted = {
        key: {
            "name": INDICATORS[key]["name"],
            "unit": INDICATORS[key]["unit"],
            "data": results[key],
        }
        for key in INDICATORS
    }
    return {
        "country_code": country,
        "country": COUNTRIES.get(country, country),
        "source": "World Bank Open Data",
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "indicators": formatted,
    }


@app.get("/exports")
async def exports(
    country: str = Query(default="WLD", description="ISO3 country code"),
    limit: int = Query(default=10, ge=1, le=60)
):
    """Exports of goods and services (current USD)"""
    country = country.upper()
    data = await fetch_wb_country(country, "NE.EXP.GNFS.CD", limit)
    return {
        "indicator": "Exports of Goods & Services",
        "series_id": "NE.EXP.GNFS.CD",
        "unit": "Current USD",
        "frequency": "Annual",
        "country_code": country,
        "country": COUNTRIES.get(country, country),
        "source": "World Bank",
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "data": data,
    }


@app.get("/imports")
async def imports(
    country: str = Query(default="WLD", description="ISO3 country code"),
    limit: int = Query(default=10, ge=1, le=60)
):
    """Imports of goods and services (current USD)"""
    country = country.upper()
    data = await fetch_wb_country(country, "NE.IMP.GNFS.CD", limit)
    return {
        "indicator": "Imports of Goods & Services",
        "series_id": "NE.IMP.GNFS.CD",
        "unit": "Current USD",
        "frequency": "Annual",
        "country_code": country,
        "country": COUNTRIES.get(country, country),
        "source": "World Bank",
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "data": data,
    }


@app.get("/trade-balance")
async def trade_balance(
    country: str = Query(default="WLD", description="ISO3 country code"),
    limit: int = Query(default=10, ge=1, le=60)
):
    """Current account balance (BoP, current USD)"""
    country = country.upper()
    data = await fetch_wb_country(country, "BN.CAB.XOKA.CD", limit)
    return {
        "indicator": "Current Account Balance",
        "series_id": "BN.CAB.XOKA.CD",
        "unit": "Current USD",
        "frequency": "Annual",
        "country_code": country,
        "country": COUNTRIES.get(country, country),
        "source": "World Bank",
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "data": data,
    }


@app.get("/trade-gdp")
async def trade_gdp(
    country: str = Query(default="WLD", description="ISO3 country code"),
    limit: int = Query(default=10, ge=1, le=60)
):
    """Trade (exports + imports) as % of GDP — trade openness"""
    country = country.upper()
    data = await fetch_wb_country(country, "NE.TRD.GNFS.ZS", limit)
    return {
        "indicator": "Trade (Exports + Imports) / GDP",
        "series_id": "NE.TRD.GNFS.ZS",
        "unit": "% of GDP",
        "frequency": "Annual",
        "country_code": country,
        "country": COUNTRIES.get(country, country),
        "source": "World Bank",
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "data": data,
    }


@app.get("/merchandise")
async def merchandise(
    country: str = Query(default="WLD", description="ISO3 country code"),
    limit: int = Query(default=10, ge=1, le=60)
):
    """Merchandise exports and imports (current USD)"""
    country = country.upper()
    exp = await fetch_wb_country(country, "TX.VAL.MRCH.CD.WT", limit)
    imp = await fetch_wb_country(country, "TM.VAL.MRCH.CD.WT", limit)
    return {
        "country_code": country,
        "country": COUNTRIES.get(country, country),
        "source": "World Bank",
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "merchandise_exports": {"series_id": "TX.VAL.MRCH.CD.WT", "unit": "Current USD", "data": exp},
        "merchandise_imports": {"series_id": "TM.VAL.MRCH.CD.WT", "unit": "Current USD", "data": imp},
    }


@app.get("/fdi")
async def fdi(
    country: str = Query(default="WLD", description="ISO3 country code"),
    limit: int = Query(default=10, ge=1, le=60)
):
    """Foreign direct investment net inflows (current USD)"""
    country = country.upper()
    data = await fetch_wb_country(country, "BX.KLT.DINV.CD.WD", limit)
    return {
        "indicator": "FDI Net Inflows",
        "series_id": "BX.KLT.DINV.CD.WD",
        "unit": "Current USD",
        "frequency": "Annual",
        "country_code": country,
        "country": COUNTRIES.get(country, country),
        "source": "World Bank",
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "data": data,
    }


@app.get("/top-exporters")
async def top_exporters(limit: int = Query(default=20, ge=1, le=50)):
    """Countries ranked by total merchandise exports"""
    data = await fetch_wb_all_countries("TX.VAL.MRCH.CD.WT")
    sorted_data = sorted(
        [d for d in data if len(d["country_code"]) == 3],
        key=lambda x: x["value"] if x["value"] is not None else 0,
        reverse=True
    )
    ranked = [{"rank": i + 1, **entry} for i, entry in enumerate(sorted_data[:limit])]
    return {
        "indicator": "Merchandise Exports",
        "series_id": "TX.VAL.MRCH.CD.WT",
        "unit": "Current USD",
        "source": "World Bank",
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "top_exporters": ranked,
    }


@app.get("/top-importers")
async def top_importers(limit: int = Query(default=20, ge=1, le=50)):
    """Countries ranked by total merchandise imports"""
    data = await fetch_wb_all_countries("TM.VAL.MRCH.CD.WT")
    sorted_data = sorted(
        [d for d in data if len(d["country_code"]) == 3],
        key=lambda x: x["value"] if x["value"] is not None else 0,
        reverse=True
    )
    ranked = [{"rank": i + 1, **entry} for i, entry in enumerate(sorted_data[:limit])]
    return {
        "indicator": "Merchandise Imports",
        "series_id": "TM.VAL.MRCH.CD.WT",
        "unit": "Current USD",
        "source": "World Bank",
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "top_importers": ranked,
    }
