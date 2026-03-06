# Demographics + Wealth Overlay Summary

## What was produced
- Enriched station file: `station_demographics_wealth_overlay.csv`
- Overlay map (interactive): `station_goodrate_demographics_wealth_overlay.html`
- Overlay map (PNG): `station_goodrate_demographics_wealth_overlay.png`
- Geocode cache: `station_geocode_cache.csv`

## Demographic coverage from reverse geocoding
- suburb coverage: 0.6%
- city/town coverage: 96.9%
- municipality coverage: 97.5%
- province coverage: 100.0%

## Wealth variable note (important)
`wealth_proxy_score` is a proxy, not true household income/wealth.
It is based on:
- proximity to major metros (80%)
- locality-name presence in geocoded address (20%)

## Exploratory relationship
- Correlation (station_mean_good_rate vs wealth_proxy_score): -0.166

## Caveat
For policy-grade socioeconomic conclusions, replace `wealth_proxy_score` with official census/deprivation data at municipality/suburb level.

## PNG export
- status: saved
