from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

ROOT = Path(r"c:\Users\AV271PH\OneDrive - EY\Documents\Snowflake Challenge")
TRAIN_PATH = ROOT / "water_quality_training_dataset.csv"
OUT_HTML = ROOT / "station_spatial_sanity_phase_b_map.html"
OUT_PNG = ROOT / "station_spatial_sanity_phase_b_map.png"
OUT_MULTI_HTML = ROOT / "station_spatial_sanity_phase_b_map_multi_metric.html"

# Load and prepare
train = pd.read_csv(TRAIN_PATH)
train["Sample Date"] = pd.to_datetime(train["Sample Date"], format="%d-%m-%Y", errors="coerce")
train["station_id"] = train["Latitude"].round(4).astype(str) + "_" + train["Longitude"].round(4).astype(str)
train["alk_good"] = ((train["Total Alkalinity"] >= 20) & (train["Total Alkalinity"] <= 200)).astype(int)
train["ec_good"] = (train["Electrical Conductance"] < 800).astype(int)
train["drp_good"] = (train["Dissolved Reactive Phosphorus"] < 100).astype(int)
train["overall_good"] = ((train["alk_good"] == 1) & (train["ec_good"] == 1) & (train["drp_good"] == 1)).astype(int)

station_map_df = (
    train.groupby(["station_id", "Latitude", "Longitude"], as_index=False)
    .agg(
        mean_ec=("Electrical Conductance", "mean"),
        mean_alk=("Total Alkalinity", "mean"),
        mean_drp=("Dissolved Reactive Phosphorus", "mean"),
        mean_overall_good=("overall_good", "mean"),
        sample_count=("station_id", "size"),
    )
)

metric_specs = [
    ("mean_ec", "Mean Electrical Conductance", "Viridis", "Mean EC", "station_spatial_sanity_mean_ec"),
    ("mean_alk", "Mean Total Alkalinity", "Cividis", "Mean Alkalinity", "station_spatial_sanity_mean_alk"),
    ("mean_drp", "Mean Dissolved Reactive Phosphorus", "Plasma", "Mean DRP", "station_spatial_sanity_mean_drp"),
    ("mean_overall_good", "Mean Overall Good-Rate", "Blues", "Mean Good Rate", "station_spatial_sanity_mean_overall_good"),
]


def style_geo(figure):
    figure.update_geos(
        scope="africa",
        showcountries=True,
        countrycolor="gray",
        showcoastlines=True,
        coastlinecolor="gray",
        showland=True,
        landcolor="rgb(240,240,240)",
        lataxis_range=[-36, -21],
        lonaxis_range=[14, 33],
        fitbounds=False,
    )
    figure.update_layout(margin=dict(l=20, r=20, t=60, b=20))


png_results = []
html_results = []

for metric_col, metric_title, color_scale, colorbar_title, base_name in metric_specs:
    metric_fig = px.scatter_geo(
        station_map_df,
        lat="Latitude",
        lon="Longitude",
        color=metric_col,
        size="sample_count",
        hover_name="station_id",
        hover_data={
            "mean_ec": ":.2f",
            "mean_alk": ":.2f",
            "mean_drp": ":.2f",
            "mean_overall_good": ":.3f",
            "sample_count": True,
            "Latitude": ":.4f",
            "Longitude": ":.4f",
        },
        color_continuous_scale=color_scale,
        projection="mercator",
        title=f"Station Spatial Sanity Check (South Africa): {metric_title}",
    )
    style_geo(metric_fig)
    metric_fig.update_layout(coloraxis_colorbar_title=colorbar_title)

    html_path = ROOT / f"{base_name}.html"
    png_path = ROOT / f"{base_name}.png"

    metric_fig.write_html(str(html_path), include_plotlyjs="cdn")
    html_results.append(html_path.name)

    try:
        metric_fig.write_image(str(png_path), width=1200, height=800, scale=2)
        png_results.append(f"{png_path.name}: saved")
    except Exception as exc:
        png_results.append(f"{png_path.name}: not saved ({exc})")


# Backward-compatible names (default = Mean EC)
default_html = ROOT / "station_spatial_sanity_mean_ec.html"
default_png = ROOT / "station_spatial_sanity_mean_ec.png"
if default_html.exists():
    OUT_HTML.write_text(default_html.read_text(encoding="utf-8"), encoding="utf-8")
if default_png.exists():
    OUT_PNG.write_bytes(default_png.read_bytes())


# Combined multi-metric interactive map with dropdown
multi_fig = go.Figure()
for index, (metric_col, metric_title, color_scale, colorbar_title, _base_name) in enumerate(metric_specs):
    multi_fig.add_trace(
        go.Scattergeo(
            lon=station_map_df["Longitude"],
            lat=station_map_df["Latitude"],
            text=station_map_df["station_id"],
            customdata=station_map_df[["mean_ec", "mean_alk", "mean_drp", "mean_overall_good", "sample_count"]].values,
            mode="markers",
            marker=dict(
                size=(station_map_df["sample_count"] ** 0.5) * 1.8,
                color=station_map_df[metric_col],
                colorscale=color_scale,
                colorbar=dict(title=colorbar_title),
                showscale=True,
                opacity=0.8,
                sizemin=4,
            ),
            name=metric_title,
            visible=(index == 0),
            hovertemplate=(
                "Station: %{text}<br>"
                "Lat/Lon: %{lat:.4f}, %{lon:.4f}<br>"
                "Mean EC: %{customdata[0]:.2f}<br>"
                "Mean Alkalinity: %{customdata[1]:.2f}<br>"
                "Mean DRP: %{customdata[2]:.2f}<br>"
                "Mean Good Rate: %{customdata[3]:.3f}<br>"
                "Sample Count: %{customdata[4]}<extra></extra>"
            ),
        )
    )

buttons = []
for index, (metric_col, metric_title, _color_scale, _colorbar_title, _base_name) in enumerate(metric_specs):
    visible_state = [False] * len(metric_specs)
    visible_state[index] = True
    buttons.append(
        dict(
            label=metric_title,
            method="update",
            args=[{"visible": visible_state}, {"title": f"Station Spatial Sanity Check (South Africa): {metric_title}"}],
        )
    )

multi_fig.update_layout(
    title="Station Spatial Sanity Check (South Africa): Mean Electrical Conductance",
    geo=dict(
        scope="africa",
        showcountries=True,
        countrycolor="gray",
        showcoastlines=True,
        coastlinecolor="gray",
        showland=True,
        landcolor="rgb(240,240,240)",
        lataxis_range=[-36, -21],
        lonaxis_range=[14, 33],
        projection_type="mercator",
    ),
    margin=dict(l=20, r=20, t=70, b=20),
    updatemenus=[
        dict(
            type="dropdown",
            direction="down",
            x=0.01,
            y=0.99,
            xanchor="left",
            yanchor="top",
            buttons=buttons,
            bgcolor="white",
        )
    ],
)

multi_fig.write_html(str(OUT_MULTI_HTML), include_plotlyjs="cdn")

print("Generated metric-specific HTML maps:")
for item in html_results:
    print(f"- {item}")

print("PNG export status:")
for item in png_results:
    print(f"- {item}")

print(f"Combined multi-metric map saved: {OUT_MULTI_HTML.name}")
print(f"Backward-compatible default HTML saved: {OUT_HTML.name}")
print(f"Backward-compatible default PNG saved: {OUT_PNG.name}")
