# Phase B Decisions (Draft)

## Station definition (frozen)
Station ID = round(Latitude, 4) + '_' + round(Longitude, 4)

## Station metrics
- Unique stations (training): 162
- Rows per station (min / median / max): 6 / 50.0 / 210
- Duplicate station-date rows: 0
- Stations sampled only once: 0

## Temporal assumptions
Sampling is uneven across years and stations; features must not assume continuous monthly coverage.

## Target transform decisions (draft from skew test)
| Target                        | Skewed   | Transform   | Rationale                             |
|:------------------------------|:---------|:------------|:--------------------------------------|
| Total Alkalinity              | No       | none        | Skew not high or log1p not beneficial |
| Electrical Conductance        | No       | none        | Skew not high or log1p not beneficial |
| Dissolved Reactive Phosphorus | Yes      | log1p       | Right-skew reduced by log1p           |

## Validation strategy (frozen)
All offline evaluation will use grouped cross-validation by station_id to prevent spatial leakage and approximate leaderboard behavior.

## Exploratory quality note
- Overall good-quality rate (threshold-based): 0.590 (59.0%)
- This is exploratory and not used as supervised target for leaderboard submission models.
