# District Malnutrition EDA Workspace

This workspace is isolated from the original prototype. It contains:

- `build_database.py`: builds a clean SQLite database for EDA
- `data/district_malnutrition_eda.db`: generated SQLite database
- `District_Malnutrition_EDA.ipynb`: Colab/Jupyter notebook for exploratory analysis
- `outputs/`: optional export location for figures and tables

## How to use

From the project root:

```powershell
python .\district_malnutrition_eda\build_database.py
```

Then open:

```text
district_malnutrition_eda/District_Malnutrition_EDA.ipynb
```

## What the database contains

- `districts`: NFHS-5 district reference table
- `nfhs4_total`: NFHS-4 district totals only
- `nfhs5`: NFHS-5 district table
- `agriculture_2019`: district-level agriculture aggregates for 2019
- `hmis_2019`: district-level HMIS indicators for 2019
- `jjm_2025`: Jal Jeevan Mission snapshot with derived village coverage ratios
- `analysis_district`: merged analysis-ready district table
- `analysis_district_normalized`: same district table with `z_...` standardized columns for modeling
- `nutrition_change_4_to_5`: NFHS-4 to NFHS-5 change table for overlapping districts
- `normalization_summary`: mean, standard deviation, and non-null count for each normalized variable
- `merge_summary`: source-level merge coverage summary
- `merge_unmatched`: unmatched district keys by source
