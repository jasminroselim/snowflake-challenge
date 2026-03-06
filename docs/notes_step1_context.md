# Step 1 Context Notes

Use this document to capture your understanding of the challenge before modeling.

---

## 1) What is being predicted

- Targets:
  - Total Alkalinity
  - Electrical Conductance (EC)
  - Dissolved Reactive Phosphorus (DRP)
- Prediction unit: each sample point is a unique location-date observation (latitude, longitude, sample date).
- Input identifiers available: latitude, longitude, sample date, and engineered station key from coordinates.

In plain terms: we must predict 3 continuous water quality values for each row in the validation template, not classify good/poor directly.

---

## 2) Why this is hard

- Generalization challenge (new regions/stations): validation locations come from different regions/stations, so models that memorize known stations will fail.
- Potential data sparsity issues: sampling is not perfectly uniform across all stations and months, so some place-time patterns are underrepresented.
- Sensor/feature limitations: target dataset alone has limited explanatory variables, so satellite/climate features are needed to capture environmental drivers.
- Risks for model overfitting: random splits can leak station-specific patterns and inflate performance; grouped validation is required.

---

## 3) How score is calculated

- Leaderboard metric: mean R² across the three predicted targets.
- How mean R² is computed across 3 targets: compute R² independently for Alkalinity, EC, and DRP, then take the simple average.
- Why grouped validation matters: if folds are split by station, local geographic signatures cannot leak between train and validation, which better simulates leaderboard behavior.

Formula used in practice:

Mean R² = (R²_alkalinity + R²_EC + R²_DRP) / 3

---

## 4) Notebook map (Snowflake-first)

| Notebook/File                                         | Purpose                                                                                   | Inputs                                                                                                                           | Outputs                                                                                                   | Notes                                                                                  |
| ----------------------------------------------------- | ----------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| snowflake_setup.sql                                   | Configure Snowflake account/network access and GitHub integration for challenge notebooks | ACCOUNTADMIN role access, SNOWFLAKE_LEARNING_DB                                                                                  | External access integration (`DATA_CHALLENGE_EXTERNAL_ACCESS`), API integration (`GITHUB`), network rules | Run once at environment setup; enables access to PyPI and Planetary Computer endpoints |
| GETTING_STARTED_NOTEBOOK.ipynb                        | Baseline workspace onboarding notebook (expected from challenge pack)                     | Snowflake workspace + setup prerequisites                                                                                        | Verified runnable environment and starter checks                                                          | Not present in current folder; check source ZIP/challenge portal                       |
| BENCHMARK_MODEL_NOTEBOOK_SNOWFLAKE.ipynb              | End-to-end baseline model workflow and submission generation                              | `water_quality_training_dataset.csv`, `landsat_features_training.csv`, `terraclimate_features_training.csv`, submission template | Baseline model scores (R² / RMSE) and challenge-format predictions CSV                                    | Uses Landsat bands/indices + TerraClimate PET; intended as starter baseline            |
| TERRACLIMATE_DATA_EXTRACTION_NOTEBOOK_SNOWFLAKE.ipynb | Extract TerraClimate climate feature file for training/submission rows via API            | Water quality train/submission rows (lat/lon/date), TerraClimate STAC/Zarr source                                                | `terraclimate_features_training.csv` and submission TerraClimate feature file                             | Demonstrates nearest-grid/time mapping (KD-tree) and 2011–2015 filtering               |
| LANDSAT_DATA_EXTRACTION_NOTEBOOK_SNOWFLAKE.ipynb      | Extract Landsat spectral features and indices for training/submission rows                | Water quality train/submission rows (lat/lon/date), Landsat STAC source                                                          | `landsat_features_training.csv` and submission Landsat feature file                                       | Long-running extraction; uses cloud filter and ~100m buffer; supports batching         |
| TERRACLIMATE_DEMONSTRATION_NOTEBOOK_SNOWFLAKE.ipynb   | Demonstrate TerraClimate access/visualization for understanding                           | TerraClimate source and sample spatial/temporal subset                                                                           | Visual/demo outputs (not primary production artifact)                                                     | Use for intuition and QA, not main training pipeline                                   |
| LANDSAT_DEMONSTRATION_NOTEBOOK_SNOWFLAKE.ipynb        | Demonstrate Landsat access and cloud-filter workflow                                      | Landsat source and sample region/time                                                                                            | Visual/demo outputs (not primary production artifact)                                                     | File in workspace is named `LANDSAT_DEMONSTRATION_NOTEBOOK_SNOWFLAKE (1).ipynb`        |

---

## 5) Plain-language story for stakeholders

### Problem statement (2–4 sentences)

Many communities still do not have reliably safe water, and water quality conditions vary significantly by location and time. This challenge asks us to forecast three key water quality parameters using environmental and geospatial data. Better forecasts help local teams identify risk sooner and allocate monitoring and treatment resources more effectively.

### Why this matters for communities (2–4 sentences)

Poor water quality increases health risks, treatment costs, and environmental damage, especially for vulnerable populations. If we can predict where and when water quality may deteriorate, local authorities can intervene earlier. This supports safer drinking water access, better public health outcomes, and more resilient water management.

### How AI helps decision-making (2–4 sentences)

AI can combine historical measurements with climate and satellite signals to detect patterns humans cannot easily see at scale. It provides repeatable, data-driven estimates for locations and dates where direct testing may be limited. Interpretable model outputs also help explain likely drivers, so decision-makers can act on root causes rather than symptoms.

---

## 6) Questions and unknowns

- [ ] Exact Snowflake object names and output tables generated by each extraction notebook
- [ ] Final feature join strategy for aligning monthly climate/satellite data with sample dates
- [ ] Which target-specific modeling choices maximize mean R² without sacrificing interpretability

---

## 7) Step 1 sign-off

- Date: 2026-02-24
- Team members present:
- Summary decision to proceed to Step 2:

---

## 8) Execution Controls to Add Before Modeling

### A) Ownership and deadlines

Assign each Phase B deliverable an owner and due date:

| Deliverable                       | Owner | Due date | Status |
| --------------------------------- | ----- | -------- | ------ |
| Data Contract (2A)                |       |          |        |
| Station key freeze (2B)           |       |          |        |
| Temporal reality check (2C)       |       |          |        |
| Target transform table (2D)       |       |          |        |
| Exploratory quality insights (2E) |       |          |        |
| Spatial sanity note (2F)          |       |          |        |
| Validation freeze statement (2G)  |       |          |        |

### B) Pass/fail gates (must be explicit)

- [ ] Hard data checks passed (nulls, dtypes, schema expectations)
- [ ] Station definition frozen and documented
- [ ] Temporal assumptions documented
- [ ] Target transform decisions frozen with rationale
- [ ] Validation strategy frozen as grouped CV by station_id

No modeling starts until all five are checked.

### C) Data versioning rules

- [ ] Freeze source file names used in Phase B
- [ ] Record extraction date/time and environment
- [ ] Record schema snapshot (column list + dtypes)
- [ ] Note any manual edits to intermediate files

### D) Leakage prevention checklist

- [ ] No random-only split used for final offline evaluation
- [ ] Cross-validation grouped by station_id
- [ ] No target-derived columns included as predictors
- [ ] Feature joins do not use future information

### E) Reproducibility checklist

- [ ] Random seeds fixed and documented
- [ ] Notebook/package environment documented
- [ ] Run order documented (setup → extraction → benchmark/improved model)
- [ ] Outputs saved with consistent naming convention

### F) Submission QA gate

- [ ] Submission columns exactly match template names and order
- [ ] Row count matches submission template
- [ ] No null predictions
- [ ] Numeric types are valid for all three targets

### G) Decision log (single source of truth)

Create and maintain a single decisions note with:

1. Frozen station definition
2. Frozen validation strategy
3. Frozen target transform decisions
4. Known risks and mitigations

This prevents rework and repeated debates.
