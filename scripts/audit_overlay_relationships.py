from pathlib import Path
import pandas as pd

root = Path(r"c:\Users\AV271PH\OneDrive - EY\Documents\Snowflake Challenge")
path = root / "outputs" / "tables" / "station_demographics_wealth_overlay.csv"
if not path.exists():
    path = root / "station_demographics_wealth_overlay.csv"

df = pd.read_csv(path)

print("Rows:", len(df))
print("Global mean_good_rate:", round(float(df["station_mean_good_rate"].mean()), 3))
print("Global corr(mean_good_rate, wealth_proxy_score):", round(float(df[["station_mean_good_rate", "wealth_proxy_score"]].corr().iloc[0, 1]), 3))

metros = {
    "cape_town": "dist_cape_town_km",
    "johannesburg": "dist_johannesburg_km",
    "pretoria": "dist_pretoria_km",
    "durban": "dist_durban_km",
}

for metro, col in metros.items():
    near = df[df[col] <= 120]["station_mean_good_rate"]
    mid = df[(df[col] > 120) & (df[col] <= 300)]["station_mean_good_rate"]
    far = df[df[col] > 300]["station_mean_good_rate"]

    print(f"\n{metro}:")
    print(" near<=120km:", "n=", len(near), "mean=", round(float(near.mean()), 3) if len(near) else None)
    print(" mid(120,300]:", "n=", len(mid), "mean=", round(float(mid.mean()), 3) if len(mid) else None)
    print(" far>300km:", "n=", len(far), "mean=", round(float(far.mean()), 3) if len(far) else None)

print("\nClosest 12 stations to Cape Town:")
ct = df.sort_values("dist_cape_town_km")[
    ["station_id", "dist_cape_town_km", "station_mean_good_rate", "wealth_proxy_score", "city_town", "municipality", "province"]
].head(12)
print(ct.to_string(index=False))
