# Graph Report - .  (2026-05-03)

## Corpus Check
- Corpus is ~26,873 words - fits in a single context window. You may not need a graph.

## Summary
- 92 nodes · 77 edges · 15 communities detected
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 8 edges (avg confidence: 0.86)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Database Ingestion & Normalization|Database Ingestion & Normalization]]
- [[_COMMUNITY_Malnutrition Analysis Framework|Malnutrition Analysis Framework]]
- [[_COMMUNITY_Explorer Page Logic|Explorer Page Logic]]
- [[_COMMUNITY_Styling Utilities & Badge|Styling Utilities & Badge]]
- [[_COMMUNITY_Clustering Visualization Outputs|Clustering Visualization Outputs]]
- [[_COMMUNITY_Base UI Components|Base UI Components]]
- [[_COMMUNITY_Regional Structural Analysis|Regional Structural Analysis]]
- [[_COMMUNITY_Theme & Providers integration|Theme & Providers integration]]
- [[_COMMUNITY_Coefficients Chart Logic|Coefficients Chart Logic]]
- [[_COMMUNITY_Base Card Component|Base Card Component]]
- [[_COMMUNITY_Base Separator Component|Base Separator Component]]
- [[_COMMUNITY_Base Slider Component|Base Slider Component]]
- [[_COMMUNITY_Base Tabs Component|Base Tabs Component]]
- [[_COMMUNITY_PCA Scatter Plot|PCA Scatter Plot]]
- [[_COMMUNITY_Application Branding (Icon)|Application Branding (Icon)]]

## God Nodes (most connected - your core abstractions)
1. `write_database()` - 9 edges
2. `map_to_districts()` - 7 edges
3. `normalize_district()` - 4 edges
4. `add_geo_keys()` - 4 edges
5. `District-Level Analysis of Child Malnutrition in India` - 4 edges
6. `normalize_text()` - 3 edges
7. `normalize_state()` - 3 edges
8. `build_district_reference()` - 3 edges
9. `load_nfhs4_total()` - 3 edges
10. `load_nfhs5()` - 3 edges

## Surprising Connections (you probably didn't know these)
- `OLS Regression Model` --conceptually_related_to--> `Pathway 3: Healthcare Reach`  [INFERRED]
  website/app/explorer/page.tsx → report.pdf
- `ClusterViz Component` --conceptually_related_to--> `Cluster Profiles Bar Chart`  [INFERRED]
  website/components/ClusterViz.tsx → outputs/clustering/cluster_profiles_bar.png
- `ClusterViz Component` --conceptually_related_to--> `Cluster Composition by State`  [INFERRED]
  website/components/ClusterViz.tsx → outputs/clustering/cluster_state_composition.png
- `ClusterViz Component` --rationale_for--> `Elbow and Silhouette Metrics`  [INFERRED]
  website/components/ClusterViz.tsx → outputs/clustering/elbow_silhouette.png
- `Badge()` --calls--> `cn()`  [INFERRED]
  website\components\ui\badge.tsx → website\lib\utils.ts

## Hyperedges (group relationships)
- **Data Processing & Analysis Pipeline** — build_database_write_database, build_database_build_analysis_tables, build_database_normalize_analysis_table, website_pca_malnutrition_index, website_ols_regression_model [EXTRACTED 0.95]
- **Clustering Visualization Suite** — cluster_profiles_bar_image, cluster_scatter_image, cluster_state_composition_image, elbow_silhouette_image [INFERRED 0.95]
- **Base UI Component Library** — badge_badge, button_button, card_card, select_select, separator_separator, slider_slider, tabs_tabs [EXTRACTED 1.00]

## Communities

### Community 0 - "Database Ingestion & Normalization"
Cohesion: 0.31
Nodes (14): add_geo_keys(), build_analysis_tables(), build_district_reference(), load_agriculture_2019(), load_hmis_2019(), load_jjm_2025(), load_nfhs4_total(), load_nfhs5() (+6 more)

### Community 2 - "Malnutrition Analysis Framework"
Cohesion: 0.2
Nodes (10): Build Analysis Tables, Normalize Analysis Table, Write Database Entry Point, District-Level Analysis of Child Malnutrition in India, Pathway 1: Food Availability, Pathway 3: Healthcare Reach, Pathway 2: Water and Sanitation, South Asian Enigma (+2 more)

### Community 3 - "Explorer Page Logic"
Cohesion: 0.33
Nodes (2): clampSlider(), loadDistrict()

### Community 4 - "Styling Utilities & Badge"
Cohesion: 0.5
Nodes (2): cn(), Badge()

### Community 5 - "Clustering Visualization Outputs"
Cohesion: 0.5
Nodes (4): Cluster Profiles Bar Chart, Cluster Composition by State, ClusterViz Component, Elbow and Silhouette Metrics

### Community 7 - "Base UI Components"
Cohesion: 0.67
Nodes (3): Badge Component, Button Component, Select Component

### Community 15 - "Regional Structural Analysis"
Cohesion: 1.0
Nodes (2): K-Means District Clustering, Northeast India Structural Outlier

### Community 16 - "Theme & Providers integration"
Cohesion: 1.0
Nodes (2): Providers Component, ThemeToggle Component

### Community 28 - "Coefficients Chart Logic"
Cohesion: 1.0
Nodes (1): CoefficientsChart Component

### Community 29 - "Base Card Component"
Cohesion: 1.0
Nodes (1): Card Component

### Community 30 - "Base Separator Component"
Cohesion: 1.0
Nodes (1): Separator Component

### Community 31 - "Base Slider Component"
Cohesion: 1.0
Nodes (1): Slider Component

### Community 32 - "Base Tabs Component"
Cohesion: 1.0
Nodes (1): Tabs Component

### Community 33 - "PCA Scatter Plot"
Cohesion: 1.0
Nodes (1): Cluster PCA Scatter Plot

### Community 34 - "Application Branding (Icon)"
Cohesion: 1.0
Nodes (1): App Icon (Malnutrition India)

## Knowledge Gaps
- **21 isolated node(s):** `Build Analysis Tables`, `South Asian Enigma`, `Pathway 1: Food Availability`, `Pathway 2: Water and Sanitation`, `K-Means District Clustering` (+16 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Explorer Page Logic`** (7 nodes): `clampSlider()`, `clearPreset()`, `loadDistrict()`, `percentileRank()`, `tierInfo()`, `zToRaw()`, `page.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Styling Utilities & Badge`** (4 nodes): `cn()`, `Badge()`, `badge.tsx`, `utils.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Regional Structural Analysis`** (2 nodes): `K-Means District Clustering`, `Northeast India Structural Outlier`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Theme & Providers integration`** (2 nodes): `Providers Component`, `ThemeToggle Component`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Coefficients Chart Logic`** (1 nodes): `CoefficientsChart Component`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Base Card Component`** (1 nodes): `Card Component`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Base Separator Component`** (1 nodes): `Separator Component`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Base Slider Component`** (1 nodes): `Slider Component`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Base Tabs Component`** (1 nodes): `Tabs Component`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `PCA Scatter Plot`** (1 nodes): `Cluster PCA Scatter Plot`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Application Branding (Icon)`** (1 nodes): `App Icon (Malnutrition India)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What connects `Build Analysis Tables`, `South Asian Enigma`, `Pathway 1: Food Availability` to the rest of the system?**
  _21 weakly-connected nodes found - possible documentation gaps or missing edges._