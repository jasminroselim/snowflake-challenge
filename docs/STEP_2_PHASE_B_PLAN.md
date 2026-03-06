# Step 2 (Phase B) — Data Contract, Station Logic, and Validation Freeze

This phase is **no-ML** by design. The purpose is to eliminate ambiguity and prevent leakage before modeling starts.

---

## 2A) Lock the Data Contract (no ML yet)

### Goal

Be 100% certain what a row and station represent, and what cannot change later.

### Actions

- Load only:
  - `water_quality_training_dataset.csv`
  - `submission_template.csv`
- Record these metrics:
  - Row count (train vs submission)
  - Column names + dtypes
  - % nulls per column
  - Min/max sample dates

### Hard checks (must pass)

- Latitude, longitude, sample_date are never null
- Targets are numeric and present only in training
- Submission targets are empty

### Deliverable

A half-page **Data Contract** note:

> Each row represents one location-date observation; no repeated target rows; submission has identical schema minus targets.

This is your immutability line.

---

## 2B) Define and Freeze the Station Key

### Goal

Freeze the station definition once and never change it again.

### Actions

- Create `station_id` from rounded coordinates (example logic):
  - `round(lat, 4) + round(lon, 4)`
- Compute:
  - Number of unique stations
  - Rows per station (min / median / max)
- Explicitly answer:
  - Do multiple rows exist for the same station-date?
  - Are some stations sampled only once?

### Decision to write down

> We define a station as ****\_\_****, and all validation splits will group on this key.

### Deliverable (freeze statement)

> Station-level generalization is enforced using station_id derived from rounded lat/lon.

If this is not frozen now, CV later can become misleading.

---

## 2C) Temporal Coverage Sanity (still no modeling)

### Actions

Produce three number-first tables:

- Samples per year
- Samples per month (aggregated across years)
- Samples per station × year

### Answer these questions

- Are some years sparsely sampled?
- Are some stations active for only a short window?
- Are there seasonal gaps?

### Why this matters

This determines whether:

- Month/season features help
- Lag features are safe
- Rolling statistics are viable

### Deliverable

A short **Temporal Reality Check** note:

> Sampling is uneven across years and stations; features must not assume continuous monthly coverage.

---

## 2D) Target Profiling and Transformation Decisions

### Actions (for each target separately)

Compute:

- min / max
- mean / median
- std
- quantiles: 1%, 5%, 25%, 50%, 75%, 95%, 99%

Then answer (yes/no):

- Is it right-skewed?
- Are extreme values physically plausible?
- Does log1p reduce skew meaningfully?

### Freeze decisions

> Target X will / will not be log-transformed during training; predictions will be inverse-transformed before submission.

### Deliverable

A 3-row decision table:

| Target                        | Skewed | Transform | Rationale |
| ----------------------------- | ------ | --------- | --------- |
| Total Alkalinity              |        |           |           |
| Electrical Conductance        |        |           |           |
| Dissolved Reactive Phosphorus |        |           |           |

This prevents recurring debates later.

---

## 2E) “Good Quality” Labels (exploration only)

### Purpose

Exploration for intuition and stakeholder alignment, not model training labels.

### Actions

Compute binary flags using challenge thresholds:

- Alkalinity in [20, 200]
- EC < 800
- DRP < 100

Compute:

- Overall good rate
- Station-level mean good rate
- Top 10 and bottom 10 stations

Check:

- Does ~60% good align with challenge narrative?

### Deliverable

A short exploratory insight list (3–5 bullets), explicitly labeled exploratory.

---

## 2F) Spatial Sanity Check (lightweight)

### Actions

- Plot station points
- Color by one target (e.g., mean EC)

### Visual checks

- Is there regional clustering?
- Are there obvious outliers?

### Deliverable

One map + one sentence:

> Spatial clustering is visible; reinforces need for grouped CV.

---

## 2G) Freeze Validation Strategy (Phase B exit gate)

### Final decision statement

> All offline evaluation will use grouped cross-validation by station_id to prevent spatial leakage and approximate leaderboard behavior.

### Deliverable

A signed-off **Phase B Decisions** section containing:

- Station definition
- Temporal assumptions
- Target transforms
- Validation strategy

Once this is complete, you are cleared to model.

---

## End-of-Phase B Success Criteria

You should be able to say:

- We know exactly what a station is.
- We know where leakage happens and how we block it.
- We know which targets need transformation and why.
- Any model that scores well under our CV is meaningful.

At this point, Phase C (feature engineering) becomes structured instead of guesswork.

---

## Team Execution Tip (optional)

For your 3-person setup:

- Person A (lead): own freezes and decision statements
- Person B (technical): own 2A–2C metrics and integrity checks
- Person C (technical/support): own 2D–2F analyses and summaries
