# Phase B Data Contract (Step 2A)

## Scope
This contract is derived using only:
- water_quality_training_dataset.csv
- submission_template.csv

## Core statement
Each row represents one location-date observation; no repeated target rows at identical location-date; submission has identical schema minus targets.

## Numeric checks
- Training row count: 9319
- Submission row count: 200
- Training date range: 2011-01-02 to 2015-12-31
- Submission date range: 2011-01-14 to 2015-12-28
- Repeated training rows at same (lat, lon, date): 0

## Hard checks
- train_lat_lon_date_non_null: True
- submission_lat_lon_date_non_null: True
- train_targets_numeric: True
- submission_targets_empty: True

## Column schema
### Training dtypes
Latitude                                float64
Longitude                               float64
Sample Date                      datetime64[us]
Total Alkalinity                        float64
Electrical Conductance                  float64
Dissolved Reactive Phosphorus           float64

### Submission dtypes
Latitude                                float64
Longitude                               float64
Sample Date                      datetime64[us]
Total Alkalinity                        float64
Electrical Conductance                  float64
Dissolved Reactive Phosphorus           float64

## Null % (Training)
Latitude                         0.0
Longitude                        0.0
Sample Date                      0.0
Total Alkalinity                 0.0
Electrical Conductance           0.0
Dissolved Reactive Phosphorus    0.0

## Null % (Submission)
Latitude                           0.0
Longitude                          0.0
Sample Date                        0.0
Total Alkalinity                 100.0
Electrical Conductance           100.0
Dissolved Reactive Phosphorus    100.0
