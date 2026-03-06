from pathlib import Path
import math
import time
import numpy as np
import pandas as pd
import plotly.express as px
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

ROOT = Path(r"c:\Users\AV271PH\OneDrive - EY\Documents\Snowflake Challenge")
STATION_INPUT = ROOT / "station_quality_profile_phase_b.csv"
CACHE_FILE = ROOT / "station_geocode_cache.csv"
OUT_ENRICHED = ROOT / "station_demographics_wealth_overlay.csv"
OUT_HTML = ROOT / "station_goodrate_demographics_wealth_overlay.html"
OUT_PNG = ROOT / "station_goodrate_demographics_wealth_overlay.png"
OUT_SUMMARY = ROOT / "demographics_wealth_overlay_summary.md"

METROS = {
    "cape_town": (-33.9249, 18.4241),
    "johannesburg": (-26.2041, 28.0473),
    "pretoria": (-25.7479, 28.2293),
    "durban": (-29.8587, 31.0218),
}


def haversine_km(lat1, lon1, lat2, lon2):
    r = 6371.0
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    return r * (2 * np.arcsin(np.sqrt(a)))


def load_cache(path: Path):
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame(columns=[
        "cache_key", "suburb", "city_town", "municipality", "province", "country", "display_name"
    ])


def normalize_series(s):
    s = pd.Series(s, dtype=float)
    if s.max() == s.min():
        return pd.Series(np.zeros(len(s)), index=s.index)
    return (s - s.min()) / (s.max() - s.min())


station = pd.read_csv(STATION_INPUT)
station["cache_key"] = station["Latitude"].round(4).astype(str) + "_" + station["Longitude"].round(4).astype(str)

cache = load_cache(CACHE_FILE)
cache_keys = set(cache["cache_key"].astype(str).tolist())

missing = station.loc[~station["cache_key"].isin(cache_keys), ["cache_key", "Latitude", "Longitude"]].drop_duplicates()

geolocator = Nominatim(user_agent="ey-water-quality-demographics-overlay")
reverse = RateLimiter(geolocator.reverse, min_delay_seconds=1.0, swallow_exceptions=True)

new_rows = []
if not missing.empty:
    for _, row in missing.iterrows():
        key = row["cache_key"]
        lat = float(row["Latitude"])
        lon = float(row["Longitude"])

        location = reverse((lat, lon), language="en", zoom=12, addressdetails=True)
        address = {} if location is None else location.raw.get("address", {})

        suburb = address.get("suburb") or address.get("neighbourhood") or address.get("quarter")
        city_town = (
            address.get("city")
            or address.get("town")
            or address.get("village")
            or address.get("hamlet")
        )
        municipality = (
            address.get("municipality")
            or address.get("county")
            or address.get("city_district")
        )
        province = address.get("state")
        country = address.get("country")
        display_name = None if location is None else location.address

        new_rows.append({
            "cache_key": key,
            "suburb": suburb,
            "city_town": city_town,
            "municipality": municipality,
            "province": province,
            "country": country,
            "display_name": display_name,
        })

    cache = pd.concat([cache, pd.DataFrame(new_rows)], ignore_index=True).drop_duplicates(subset=["cache_key"], keep="last")
    cache.to_csv(CACHE_FILE, index=False)

# Merge cache demographics
merged = station.merge(cache, on="cache_key", how="left")

# Wealth proxy (explicitly proxy): urban proximity + settlement context
for metro_name, (m_lat, m_lon) in METROS.items():
    merged[f"dist_{metro_name}_km"] = haversine_km(merged["Latitude"], merged["Longitude"], m_lat, m_lon)

metro_dist_cols = [c for c in merged.columns if c.startswith("dist_") and c.endswith("_km")]
merged["nearest_metro_km"] = merged[metro_dist_cols].min(axis=1)

# Settlement indicator from reverse geocode availability
merged["has_locality_name"] = merged[["suburb", "city_town", "municipality"]].notna().any(axis=1).astype(int)

# Score components
proximity_score = 1.0 - normalize_series(merged["nearest_metro_km"])  # closer => higher proxy
locality_score = merged["has_locality_name"].astype(float)

# Transparent proxy definition (not true household wealth)
merged["wealth_proxy_score"] = (0.8 * proximity_score + 0.2 * locality_score).clip(0, 1)

# Rank bins for easier communication
merged["wealth_proxy_band"] = pd.cut(
    merged["wealth_proxy_score"],
    bins=[-0.001, 0.33, 0.66, 1.0],
    labels=["Low proxy", "Mid proxy", "High proxy"]
)

merged.to_csv(OUT_ENRICHED, index=False)

# Create overlay map
fig = px.scatter_geo(
    merged,
    lat="Latitude",
    lon="Longitude",
    color="station_mean_good_rate",
    size="wealth_proxy_score",
    hover_name="station_id",
    hover_data={
        "station_mean_good_rate": ":.3f",
        "wealth_proxy_score": ":.3f",
        "wealth_proxy_band": True,
        "suburb": True,
        "city_town": True,
        "municipality": True,
        "province": True,
        "nearest_metro_km": ":.1f",
    },
    color_continuous_scale="RdYlGn",
    projection="mercator",
    title="Station Mean Overall Good-Rate with Demographic Labels and Wealth Proxy (South Africa)",
)

fig.update_geos(
    scope="africa",
    showcountries=True,
    countrycolor="gray",
    showcoastlines=True,
    coastlinecolor="gray",
    showland=True,
    landcolor="rgb(240,240,240)",
    lataxis_range=[-36, -21],
    lonaxis_range=[14, 33],
)
fig.update_layout(margin=dict(l=20, r=20, t=70, b=20), coloraxis_colorbar_title="Mean Good Rate")

fig.write_html(str(OUT_HTML), include_plotlyjs="cdn")

png_status = "saved"
try:
    fig.write_image(str(OUT_PNG), width=1200, height=800, scale=2)
except Exception as exc:
    png_status = f"not saved ({exc})"

# Summary note
coverage = {
    "suburb": float(merged["suburb"].notna().mean()),
    "city_town": float(merged["city_town"].notna().mean()),
    "municipality": float(merged["municipality"].notna().mean()),
    "province": float(merged["province"].notna().mean()),
}

corr = merged[["station_mean_good_rate", "wealth_proxy_score"]].corr().iloc[0, 1]

summary = f"""# Demographics + Wealth Overlay Summary

## What was produced
- Enriched station file: `{OUT_ENRICHED.name}`
- Overlay map (interactive): `{OUT_HTML.name}`
- Overlay map (PNG): `{OUT_PNG.name}`
- Geocode cache: `{CACHE_FILE.name}`

## Demographic coverage from reverse geocoding
- suburb coverage: {coverage['suburb']*100:.1f}%
- city/town coverage: {coverage['city_town']*100:.1f}%
- municipality coverage: {coverage['municipality']*100:.1f}%
- province coverage: {coverage['province']*100:.1f}%

## Wealth variable note (important)
`wealth_proxy_score` is a proxy, not true household income/wealth.
It is based on:
- proximity to major metros (80%)
- locality-name presence in geocoded address (20%)

## Exploratory relationship
- Correlation (station_mean_good_rate vs wealth_proxy_score): {corr:.3f}

## Caveat
For policy-grade socioeconomic conclusions, replace `wealth_proxy_score` with official census/deprivation data at municipality/suburb level.

## PNG export
- status: {png_status}
"""

OUT_SUMMARY.write_text(summary, encoding="utf-8")

print("Demographic enrichment and wealth-proxy overlay completed.")
print(summary)
