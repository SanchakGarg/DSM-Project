# EDA Explanation

## What EDA means here

EDA stands for **Exploratory Data Analysis**. In this project, EDA is the first serious analysis stage after data ingestion and cleaning. Its purpose is to help us understand:

- what the merged district-level dataset looks like
- whether the data is complete enough for analysis
- how child malnutrition varies across districts and states
- whether there are visible patterns between nutrition outcomes and explanatory variables
- what problems or limitations need to be handled before regression and clustering

EDA is not the final model. It is the stage where we inspect the data carefully so that later conclusions are based on actual patterns rather than assumptions.

## Why EDA is important for this project

This project combines multiple public datasets:

- NFHS-4
- NFHS-5
- HMIS
- Agriculture Statistics
- Jal Jeevan Mission

These datasets come from different systems, use different year structures, and do not always align perfectly at the district level. Because of that, EDA is necessary to answer basic but important questions before modeling:

- Which districts are available in all sources?
- How much missing data is there?
- Are the malnutrition indicators distributed normally or highly unevenly?
- Which states or districts have the highest burden?
- Are sanitation, education, healthcare, or agricultural variables visibly related to malnutrition?

Without EDA, regression results can be misleading because we may use badly merged data, weak variables, or incomplete district coverage.

## What data is being used for EDA

The EDA notebook uses the cleaned SQLite database created by:

- `district_malnutrition_eda/build_database.py`

The main table used for analysis is:

- `analysis_district`

This is a merged district-level table built from cleaned source tables. It includes:

- child nutrition indicators from NFHS-5
- selected historical NFHS-4 indicators for comparison
- district-level agriculture aggregates for 2019
- HMIS 2019 healthcare indicators
- JJM 2025 supporting coverage ratios

The notebook also uses:

- `merge_summary`
- `merge_unmatched`
- `nutrition_change_4_to_5`

For later modeling support, the database also contains:

- `analysis_district_normalized`
- `normalization_summary`

These help assess merge quality and compare NFHS-4 and NFHS-5 outcomes for overlapping districts.

## How the EDA is being done

The notebook follows a clear sequence.

### 1. Load the cleaned database

The notebook connects to the new SQLite database:

- `district_malnutrition_eda/data/district_malnutrition_eda.db`

This avoids using raw CSV files directly during EDA. It ensures that all analysis is based on a single cleaned and merged source of truth.

### 2. Inspect available tables and merged dataset shape

The first step is to confirm:

- which tables exist in the database
- how many rows and columns are in the merged analysis table
- whether the pipeline created all expected outputs

This is a basic integrity check.

### 3. Check merge coverage and unmatched districts

Because the project depends on combining multiple datasets, the notebook checks:

- how many rows matched successfully for each source
- how many districts failed to match
- which district names remain unmatched

This is important because some newly created districts or naming differences reduce full cross-source coverage.

### 4. Measure missingness

The notebook calculates missing values for the main analysis variables, such as:

- stunting
- wasting
- underweight
- child anaemia
- improved water
- improved sanitation
- maternal schooling
- institutional deliveries
- ANC coverage
- agricultural yield

This tells us which variables are reliable enough for later modeling and which variables reduce sample size.

### 5. Produce descriptive statistics

For the core variables, the notebook computes:

- mean
- standard deviation
- median
- minimum
- maximum

This gives a statistical summary of the burden of child malnutrition and the variation across districts.

### 6. Visualize distributions

The notebook creates histograms for the main child nutrition indicators:

- stunting
- wasting
- underweight
- child anaemia

These plots help identify:

- skewness
- clustering of districts
- unusually high-burden districts
- whether the burden is evenly spread or concentrated

### 7. Compare state-level burden

The notebook aggregates district outcomes to the state level and ranks states by average nutrition burden. This helps identify:

- high-burden states
- lower-burden states
- broad geographic inequality

This is useful for report writing because it gives a policy-level overview before district-level detail.

### 8. Compare NFHS-4 and NFHS-5 where overlap exists

For districts appearing in both NFHS waves, the notebook computes change between NFHS-4 and NFHS-5 for:

- stunting
- wasting
- underweight
- child anaemia

This helps us understand whether conditions improved or worsened over time, even though the project is not currently being treated as a full causal panel study.

### 9. Study correlations

The notebook builds a correlation matrix across nutrition outcomes and selected explanatory variables. This gives an early view of:

- which variables move together
- which variables are negatively associated with malnutrition
- whether some predictors may be strongly related to each other

This is not causal evidence, but it is useful for selecting variables for regression.

### 10. Plot simple relationships

The notebook creates scatter plots for selected relationships such as:

- stunting vs improved water
- child anaemia vs institutional delivery
- underweight vs agricultural yield

These visual checks help confirm whether the data shows visible patterns before formal modeling.

## What EDA is expected to give us

By the end of EDA, we should know:

- the usable district sample size
- which variables are strongest candidates for regression
- how severe and uneven child malnutrition is
- which states and districts appear most vulnerable
- whether some explanatory variables seem plausibly related to nutrition outcomes
- what limitations must be reported honestly in the final writeup

So EDA gives both:

- **substantive findings**, such as high-burden regions and broad patterns
- **technical findings**, such as missing data and merge weaknesses

## What EDA does not do

EDA does **not** prove causation.

At this stage, if we observe that sanitation or women’s education is negatively associated with malnutrition, that only means the variables move together in the data. It does not prove that one directly causes the other.

That is why EDA is followed by:

- regression, to estimate controlled associations more formally
- clustering, to identify district vulnerability profiles

## Current interpretation from the EDA stage

The early EDA results suggest:

- child malnutrition remains highly uneven across districts
- states such as Gujarat, Bihar, Jharkhand, and Madhya Pradesh show high average burden across multiple indicators
- some anthropometric outcomes improved from NFHS-4 to NFHS-5 on average
- child anaemia worsened on average across overlapping districts
- sanitation and women’s schooling appear more strongly associated with lower malnutrition than any single sector variable alone
- agriculture and healthcare still matter, but their simple cross-sectional relationships are weaker or more mixed

These findings justify the next stage of analysis, but they should still be treated as exploratory rather than final.

## How normalization is being handled

The cleaned database now stores both:

- `analysis_district`: raw values in original units
- `analysis_district_normalized`: z-score standardized versions of the main numeric analysis variables

The normalized table is mainly for:

- PCA
- clustering
- comparing variables measured on very different scales

The standardization rule is:

```text
z = (value - mean) / standard deviation
```

The parameters used for each normalized variable are stored in:

- `normalization_summary`

## Files involved

- `district_malnutrition_eda/build_database.py`
- `district_malnutrition_eda/data/district_malnutrition_eda.db`
- `district_malnutrition_eda/District_Malnutrition_EDA.ipynb`

## Next step after EDA

Once EDA is complete and reviewed, the next stage is to:

- build a composite malnutrition index
- run regression models with a small justified variable set
- cluster districts into vulnerability profiles
- convert those results into policy recommendations
