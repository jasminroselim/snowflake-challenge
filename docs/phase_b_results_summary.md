# Phase B Run Summary

Generated artifacts:
- phase_b_data_contract.md
- PHASE_B_DECISIONS.md
- station_profile_phase_b.csv
- samples_per_year_phase_b.csv
- samples_per_month_phase_b.csv
- samples_per_station_year_phase_b.csv
- target_profile_phase_b.csv
- target_transform_decisions_phase_b.csv
- station_quality_profile_phase_b.csv
- quality_top_bottom_stations_phase_b.csv
- station_spatial_sanity_phase_b.png

Headline numbers:
- Train rows: 9319
- Submission rows: 200
- Unique stations (train): 162
- Overall good-quality exploratory rate: 0.590

Hard checks:
- {'train_lat_lon_date_non_null': True, 'submission_lat_lon_date_non_null': True, 'train_targets_numeric': True, 'submission_targets_empty': True}
