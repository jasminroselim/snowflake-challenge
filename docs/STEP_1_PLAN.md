# Step 1 Plan — Context, Notebook Orientation, and Data Discovery (Snowflake)

This guide is intentionally limited to Step 1 only.

Goal of Step 1: understand the challenge context, understand what each notebook does, and perform structured data discovery before building models.

---

## Step 1 Outcomes (What success looks like)

By the end of Step 1, you should have:

1. A clear one-paragraph summary of the challenge objective in your own words.
2. A notebook map showing which notebook does what.
3. A basic quality profile of the training and submission data (shape, nulls, date coverage, station coverage, target distributions).
4. A short list of data issues/risks to handle in Step 2.

---

## Step 1A — Understand the context first (30–45 min)

Read and write down these points in plain language:

- Prediction task: regress 3 targets (Total Alkalinity, Electrical Conductance, DRP).
- Generalization requirement: validation points are from different regions/stations.
- Metric: mean R² across the 3 targets.
- Interpretation requirement: explain key drivers of variation.

Create a short note with these 4 headings:

1. What is being predicted
2. Why this is hard
3. How score is calculated
4. What non-technical stakeholders need to hear

---

## Step 1B — Notebook reading order (Snowflake-first)

Read in this order and take notes after each notebook.

### 1) Environment setup

1. `snowflake_setup.sql`
   - Purpose: provisioning and permissions.
   - What to capture: database/schema/stage names created, external access steps, any credentials/secrets assumptions.

2. `GETTING_STARTED_NOTEBOOK.ipynb` (if available in your challenge bundle)
   - Purpose: platform setup sanity check.
   - What to capture: expected runtime, libraries, data access patterns.

### 2) Main modeling baseline

3. `BENCHMARK_MODEL_NOTEBOOK_SNOWFLAKE.ipynb`
   - Purpose: end-to-end baseline training and submission flow.
   - What to capture:
     - Input tables/files
     - Feature columns used
     - Model type(s)
     - Train/test logic
     - Output submission path

### 3) Feature extraction notebooks

4. `TERRACLIMATE_DATA_EXTRACTION_NOTEBOOK_SNOWFLAKE.ipynb`
   - Purpose: derive climate and water-balance features.
   - What to capture: variables extracted, temporal granularity, join keys, output dataset name.

5. `LANDSAT_DATA_EXTRACTION_NOTEBOOK_SNOWFLAKE.ipynb`
   - Purpose: derive satellite surface/vegetation features.
   - What to capture: cloud filtering logic, indices used (for example NDVI), spatial sampling method, output dataset name.

### 4) Optional understanding notebooks

6. `TERRACLIMATE_DEMONSTRATION_NOTEBOOK_SNOWFLAKE.ipynb`
7. `LANDSAT_DEMONSTRATION_NOTEBOOK_SNOWFLAKE.ipynb`

These are for intuition and validation, not the primary production flow.

---

## Step 1C — Data discovery checklist (Snowflake)

Run discovery in this order.

### Part 1: Load and schema sanity

- Confirm row counts for:
  - training target dataset
  - submission template
- Confirm column names and types.
- Parse and validate dates.

Questions to answer:

- Are there nulls in Latitude/Longitude/Sample Date?
- Are target columns numeric and non-empty in training?
- Is submission template target section empty as expected?

### Part 2: Uniqueness and key structure

- Count unique station coordinates (lat, lon).
- Count unique (lat, lon, sample_date) combinations.
- Check duplicates at sample level.

Questions to answer:

- Do repeated station-date rows exist?
- Is there a reliable station key design (rounded lat-lon)?

### Part 3: Temporal coverage

- Min and max sample date.
- Monthly sample counts by year.
- Gaps by month/station.

Questions to answer:

- Is sampling balanced over 2011–2015?
- Are there seasonal or year-specific sparsity issues?

### Part 4: Target profiling

For each target (Alkalinity, EC, DRP):

- min, max, mean, median, std
- quantiles (1%, 5%, 25%, 50%, 75%, 95%, 99%)
- outlier review (extreme tails)

Questions to answer:

- Which target is most skewed?
- Which target likely needs transform (for example log1p)?

### Part 5: Quality label exploration (from challenge thresholds)

Create:

- Alk good if 20–200
- EC good if <800
- DRP good if <100
- Overall good = 1 only when all three are good

Then compute:

- overall good rate
- station-level mean good rate
- top/bottom stations by mean good rate

Questions to answer:

- Does your computed good-rate align with challenge narrative (~59%)?
- Which areas appear persistently low/high quality?

### Part 6: Spatial diagnostics (lightweight)

- Plot station locations.
- Join station-level mean-good to map.
- Compare broad regional patterns (west/interior/east).

Questions to answer:

- Is there visible regional clustering?
- Do results support the “spatial bias” statement from guidance?

---

## Step 1D — Deliverables to produce before Step 2

Create these files/artifacts:

1. `notes_step1_context.md`
   - your challenge summary and notebook map.

2. `data_discovery_summary_step1.md`
   - schema checks, quality checks, profiling highlights, risks.

3. `station_quality_profile.csv`
   - station-level mean quality indicator (0 to 1).

4. 2–4 plots/screenshots
   - monthly sample counts
   - target distributions
   - station map colored by mean quality

Only move to Step 2 when these are complete.

---

## Step 1E — Team split for your 3-person team

### Person 1 (non-technical)

- Own `notes_step1_context.md`
- Build plain-language glossary for targets and thresholds
- Draft 5-slide storyline: problem, data, regional variability, why model matters

### Person 2 (technical)

- Own Snowflake setup and notebook map
- Validate data loading, schema, keys, and temporal coverage

### Person 3 (technical)

- Own target profiling, quality-label analysis, and station-level summaries
- Produce charts and data discovery summary

Daily sync format (15 min):

- What was completed
- What is blocked
- What is needed from another teammate

---

## Step 1 Exit Criteria Checklist

- [ ] All required notebooks were read in order and summarized
- [ ] Data schema and key checks completed
- [ ] Temporal and target profiling completed
- [ ] Quality label and station-level bias analysis completed
- [ ] Step 1 deliverables saved
- [ ] Team aligned on risks and Step 2 priorities

If all boxes are checked, proceed to Step 2 (feature integration and baseline model improvements).
