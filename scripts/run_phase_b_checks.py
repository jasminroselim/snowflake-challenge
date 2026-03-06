from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(r"c:\Users\AV271PH\OneDrive - EY\Documents\Snowflake Challenge")
TRAIN_PATH = ROOT / "water_quality_training_dataset.csv"
SUB_PATH = ROOT / "submission_template.csv"

OUT_DATA_CONTRACT = ROOT / "phase_b_data_contract.md"
OUT_DECISIONS = ROOT / "PHASE_B_DECISIONS.md"
OUT_SUMMARY = ROOT / "phase_b_results_summary.md"
OUT_STATION_PROFILE = ROOT / "station_profile_phase_b.csv"
OUT_TEMP_YEAR = ROOT / "samples_per_year_phase_b.csv"
OUT_TEMP_MONTH = ROOT / "samples_per_month_phase_b.csv"
OUT_TEMP_STATION_YEAR = ROOT / "samples_per_station_year_phase_b.csv"
OUT_TARGET_PROFILE = ROOT / "target_profile_phase_b.csv"
OUT_TRANSFORM_DECISIONS = ROOT / "target_transform_decisions_phase_b.csv"
OUT_QUALITY_STATION = ROOT / "station_quality_profile_phase_b.csv"
OUT_TOP_BOTTOM = ROOT / "quality_top_bottom_stations_phase_b.csv"
OUT_MAP = ROOT / "station_spatial_sanity_phase_b.png"

train = pd.read_csv(TRAIN_PATH)
sub = pd.read_csv(SUB_PATH)

# Standardize datetime parsing
for df in (train, sub):
    df["Sample Date"] = pd.to_datetime(df["Sample Date"], format="%d-%m-%Y", errors="coerce")

# 2A Data contract metrics
row_count_train = len(train)
row_count_sub = len(sub)

train_dtypes = train.dtypes.astype(str)
sub_dtypes = sub.dtypes.astype(str)

train_null_pct = (train.isna().mean() * 100).round(4)
sub_null_pct = (sub.isna().mean() * 100).round(4)

train_min_date, train_max_date = train["Sample Date"].min(), train["Sample Date"].max()
sub_min_date, sub_max_date = sub["Sample Date"].min(), sub["Sample Date"].max()

hard_checks = {
    "train_lat_lon_date_non_null": bool(train[["Latitude", "Longitude", "Sample Date"]].notna().all().all()),
    "submission_lat_lon_date_non_null": bool(sub[["Latitude", "Longitude", "Sample Date"]].notna().all().all()),
    "train_targets_numeric": all(pd.api.types.is_numeric_dtype(train[c]) for c in ["Total Alkalinity", "Electrical Conductance", "Dissolved Reactive Phosphorus"]),
    "submission_targets_empty": bool(sub[["Total Alkalinity", "Electrical Conductance", "Dissolved Reactive Phosphorus"]].isna().all().all()),
}

# Repeated target row check by unique location-date in training
train_key = train[["Latitude", "Longitude", "Sample Date"]].copy()
repeated_location_date_rows = int(train_key.duplicated().sum())

# 2B Station key freeze metrics
train["station_id"] = train["Latitude"].round(4).astype(str) + "_" + train["Longitude"].round(4).astype(str)
sub["station_id"] = sub["Latitude"].round(4).astype(str) + "_" + sub["Longitude"].round(4).astype(str)

station_counts = train.groupby("station_id").size().rename("rows_per_station")
unique_stations = int(train["station_id"].nunique())
rows_per_station_min = int(station_counts.min())
rows_per_station_med = float(station_counts.median())
rows_per_station_max = int(station_counts.max())

station_date_dupes = int(train.duplicated(subset=["station_id", "Sample Date"]).sum())
stations_sampled_once = int((station_counts == 1).sum())

station_profile = station_counts.reset_index()
station_profile.to_csv(OUT_STATION_PROFILE, index=False)

# 2C Temporal tables
train["year"] = train["Sample Date"].dt.year
train["month"] = train["Sample Date"].dt.month

samples_per_year = train.groupby("year").size().rename("sample_count").reset_index()
samples_per_month = train.groupby("month").size().rename("sample_count").reset_index()
samples_per_station_year = train.groupby(["station_id", "year"]).size().rename("sample_count").reset_index()

samples_per_year.to_csv(OUT_TEMP_YEAR, index=False)
samples_per_month.to_csv(OUT_TEMP_MONTH, index=False)
samples_per_station_year.to_csv(OUT_TEMP_STATION_YEAR, index=False)

# 2D Target profiling + transform decisions
TARGETS = ["Total Alkalinity", "Electrical Conductance", "Dissolved Reactive Phosphorus"]
quantiles = [0.01, 0.05, 0.25, 0.50, 0.75, 0.95, 0.99]

rows = []
transform_rows = []

for target in TARGETS:
    s = train[target].astype(float)
    q = s.quantile(quantiles)

    skewed = bool(s.skew() > 1.0)
    log_s = np.log1p(np.clip(s, 0, None))
    log_skew_reduced = abs(log_s.skew()) < abs(s.skew())
    use_log = skewed and log_skew_reduced

    rows.append({
        "target": target,
        "min": float(s.min()),
        "max": float(s.max()),
        "mean": float(s.mean()),
        "median": float(s.median()),
        "std": float(s.std()),
        "q01": float(q.loc[0.01]),
        "q05": float(q.loc[0.05]),
        "q25": float(q.loc[0.25]),
        "q50": float(q.loc[0.50]),
        "q75": float(q.loc[0.75]),
        "q95": float(q.loc[0.95]),
        "q99": float(q.loc[0.99]),
        "raw_skew": float(s.skew()),
        "log1p_skew": float(log_s.skew()),
    })

    transform_rows.append({
        "Target": target,
        "Skewed": "Yes" if skewed else "No",
        "Transform": "log1p" if use_log else "none",
        "Rationale": "Right-skew reduced by log1p" if use_log else "Skew not high or log1p not beneficial"
    })

profile_df = pd.DataFrame(rows)
profile_df.to_csv(OUT_TARGET_PROFILE, index=False)

transform_df = pd.DataFrame(transform_rows)
transform_df.to_csv(OUT_TRANSFORM_DECISIONS, index=False)

# 2E Good quality exploratory labels
train["alk_good"] = ((train["Total Alkalinity"] >= 20) & (train["Total Alkalinity"] <= 200)).astype(int)
train["ec_good"] = (train["Electrical Conductance"] < 800).astype(int)
train["drp_good"] = (train["Dissolved Reactive Phosphorus"] < 100).astype(int)
train["overall_good"] = ((train["alk_good"] == 1) & (train["ec_good"] == 1) & (train["drp_good"] == 1)).astype(int)

overall_good_rate = float(train["overall_good"].mean())
station_quality = train.groupby(["station_id", "Latitude", "Longitude"], as_index=False)["overall_good"].mean()
station_quality = station_quality.rename(columns={"overall_good": "station_mean_good_rate"})
station_quality.to_csv(OUT_QUALITY_STATION, index=False)

station_quality_sorted = station_quality.sort_values("station_mean_good_rate")
top10 = station_quality_sorted.tail(10).assign(rank_group="top10")
bottom10 = station_quality_sorted.head(10).assign(rank_group="bottom10")
pd.concat([top10, bottom10], ignore_index=True).to_csv(OUT_TOP_BOTTOM, index=False)

# 2F Spatial sanity map
plot_df = train.groupby(["station_id", "Latitude", "Longitude"], as_index=False)["Electrical Conductance"].mean()
plot_df = plot_df.rename(columns={"Electrical Conductance": "mean_ec"})

fig, ax = plt.subplots(figsize=(8, 6))
sc = ax.scatter(plot_df["Longitude"], plot_df["Latitude"], c=plot_df["mean_ec"], cmap="viridis", s=28)
ax.set_title("Station Spatial Sanity: Mean Electrical Conductance")
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
cb = plt.colorbar(sc, ax=ax)
cb.set_label("Mean EC")
plt.tight_layout()
fig.savefig(OUT_MAP, dpi=150)
plt.close(fig)

# Write contract note
contract_text = f"""# Phase B Data Contract (Step 2A)\n\n## Scope\nThis contract is derived using only:\n- water_quality_training_dataset.csv\n- submission_template.csv\n\n## Core statement\nEach row represents one location-date observation; no repeated target rows at identical location-date; submission has identical schema minus targets.\n\n## Numeric checks\n- Training row count: {row_count_train}\n- Submission row count: {row_count_sub}\n- Training date range: {train_min_date.date()} to {train_max_date.date()}\n- Submission date range: {sub_min_date.date()} to {sub_max_date.date()}\n- Repeated training rows at same (lat, lon, date): {repeated_location_date_rows}\n\n## Hard checks\n- train_lat_lon_date_non_null: {hard_checks['train_lat_lon_date_non_null']}\n- submission_lat_lon_date_non_null: {hard_checks['submission_lat_lon_date_non_null']}\n- train_targets_numeric: {hard_checks['train_targets_numeric']}\n- submission_targets_empty: {hard_checks['submission_targets_empty']}\n\n## Column schema\n### Training dtypes\n{train_dtypes.to_string()}\n\n### Submission dtypes\n{sub_dtypes.to_string()}\n\n## Null % (Training)\n{train_null_pct.to_string()}\n\n## Null % (Submission)\n{sub_null_pct.to_string()}\n"""
OUT_DATA_CONTRACT.write_text(contract_text, encoding="utf-8")

# Write decisions draft
phase_b_decisions = f"""# Phase B Decisions (Draft)\n\n## Station definition (frozen)\nStation ID = round(Latitude, 4) + '_' + round(Longitude, 4)\n\n## Station metrics\n- Unique stations (training): {unique_stations}\n- Rows per station (min / median / max): {rows_per_station_min} / {rows_per_station_med:.1f} / {rows_per_station_max}\n- Duplicate station-date rows: {station_date_dupes}\n- Stations sampled only once: {stations_sampled_once}\n\n## Temporal assumptions\nSampling is uneven across years and stations; features must not assume continuous monthly coverage.\n\n## Target transform decisions (draft from skew test)\n{transform_df.to_markdown(index=False)}\n\n## Validation strategy (frozen)\nAll offline evaluation will use grouped cross-validation by station_id to prevent spatial leakage and approximate leaderboard behavior.\n\n## Exploratory quality note\n- Overall good-quality rate (threshold-based): {overall_good_rate:.3f} ({overall_good_rate*100:.1f}%)\n- This is exploratory and not used as supervised target for leaderboard submission models.\n"""
OUT_DECISIONS.write_text(phase_b_decisions, encoding="utf-8")

summary = f"""# Phase B Run Summary\n\nGenerated artifacts:\n- {OUT_DATA_CONTRACT.name}\n- {OUT_DECISIONS.name}\n- {OUT_STATION_PROFILE.name}\n- {OUT_TEMP_YEAR.name}\n- {OUT_TEMP_MONTH.name}\n- {OUT_TEMP_STATION_YEAR.name}\n- {OUT_TARGET_PROFILE.name}\n- {OUT_TRANSFORM_DECISIONS.name}\n- {OUT_QUALITY_STATION.name}\n- {OUT_TOP_BOTTOM.name}\n- {OUT_MAP.name}\n\nHeadline numbers:\n- Train rows: {row_count_train}\n- Submission rows: {row_count_sub}\n- Unique stations (train): {unique_stations}\n- Overall good-quality exploratory rate: {overall_good_rate:.3f}\n\nHard checks:\n- {hard_checks}\n"""
OUT_SUMMARY.write_text(summary, encoding="utf-8")

print("Phase B checks completed.")
print(summary)
