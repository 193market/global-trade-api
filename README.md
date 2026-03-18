# Global Trade Statistics API

Global trade data including exports, imports, trade balance, merchandise trade, FDI, and top exporting/importing nations for 190+ countries. Powered by World Bank Open Data.

## Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | API info and available endpoints |
| `GET /summary` | All trade indicators for a country |
| `GET /exports` | Exports of goods & services (USD) |
| `GET /imports` | Imports of goods & services (USD) |
| `GET /trade-balance` | Current account balance |
| `GET /trade-gdp` | Trade as % of GDP (openness) |
| `GET /merchandise` | Merchandise exports & imports |
| `GET /fdi` | Foreign direct investment inflows |
| `GET /top-exporters` | Countries ranked by exports |
| `GET /top-importers` | Countries ranked by imports |

## Query Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `country` | ISO3 country code (e.g., USA, CHN, DEU) | `WLD` |
| `limit` | Number of years or countries to return | `10` |

## Data Source

World Bank Open Data
https://data.worldbank.org/indicator/NE.EXP.GNFS.CD

## Authentication

Requires `X-RapidAPI-Key` header via RapidAPI.
