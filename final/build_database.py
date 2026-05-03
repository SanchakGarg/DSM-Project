import re
import sqlite3
from pathlib import Path

import pandas as pd


WORKSPACE_DIR = Path(__file__).resolve().parent
RAW_DIR  = WORKSPACE_DIR / "data" / "raw"
DB_PATH  = WORKSPACE_DIR / "data" / "malnutrition.db"

NFHS4_PATH = RAW_DIR / "NFHS-4.csv"
NFHS5_PATH = RAW_DIR / "NFHS-5.csv"
AGRI_PATH  = RAW_DIR / "AgricultureStatistics.csv"
HMIS_PATH  = RAW_DIR / "HMIS (2017-18,2019-20).csv"
JJM_PATH   = RAW_DIR / "JalJeevanMission.csv"


STATE_ALIASES = {
    "andaman and nicobar island": "andaman and nicobar islands",
    "dadra and nagar haveli and daman and diu": "dadra and nagar haveli and daman and diu",
    "nct of delhi": "delhi",
    "orissa": "odisha",
    "pondicherry": "puducherry",
    "uttaranchal": "uttarakhand",
}


DISTRICT_ALIASES = {
    ("maharashtra", "mumbai suburban"): "mumbai suburban",
    ("maharashtra", "mumbai city"): "mumbai",
}


def normalize_text(value):
    value = str(value).strip().lower()
    value = value.replace("&", "and")
    value = re.sub(r"[^a-z0-9]+", " ", value)
    value = re.sub(r"\b(dist|district)\b", "", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def normalize_state(value):
    value = normalize_text(value)
    return STATE_ALIASES.get(value, value)


def normalize_district(state_value, district_value):
    state_key = normalize_state(state_value)
    district_key = normalize_text(district_value)
    return DISTRICT_ALIASES.get((state_key, district_key), district_key)


def add_geo_keys(df, state_col="State", district_col="District"):
    out = df.copy()
    out["state_key"] = out[state_col].map(normalize_state)
    out["district_key"] = [
        normalize_district(state, district)
        for state, district in zip(out[state_col], out[district_col])
    ]
    return out


def build_district_reference():
    nfhs5 = pd.read_csv(
        NFHS5_PATH,
        usecols=["State", "District"],
    ).dropna()
    nfhs5 = add_geo_keys(nfhs5).drop_duplicates(subset=["state_key", "district_key"])
    nfhs5 = nfhs5.sort_values(["State", "District"]).reset_index(drop=True)
    nfhs5.insert(0, "district_id", range(1, len(nfhs5) + 1))
    nfhs5 = nfhs5.rename(
        columns={
            "State": "state_name",
            "District": "district_name",
        }
    )
    return nfhs5[["district_id", "state_name", "district_name", "state_key", "district_key"]]


def map_to_districts(df, districts, source_name, state_col="State", district_col="District"):
    geo = add_geo_keys(df, state_col=state_col, district_col=district_col)
    merged = geo.merge(
        districts[["district_id", "state_key", "district_key"]],
        on=["state_key", "district_key"],
        how="left",
    )

    unmatched = (
        merged.loc[merged["district_id"].isna(), [state_col, district_col, "state_key", "district_key"]]
        .drop_duplicates()
        .rename(columns={state_col: "state_name", district_col: "district_name"})
    )
    unmatched["source_name"] = source_name

    summary = pd.DataFrame(
        [
            {
                "source_name": source_name,
                "rows_total": int(len(merged)),
                "rows_matched": int(merged["district_id"].notna().sum()),
                "rows_unmatched": int(merged["district_id"].isna().sum()),
                "unique_district_keys": int(merged[["state_key", "district_key"]].drop_duplicates().shape[0]),
                "matched_unique_districts": int(
                    merged.loc[merged["district_id"].notna(), ["state_key", "district_key"]]
                    .drop_duplicates()
                    .shape[0]
                ),
            }
        ]
    )

    return merged, summary, unmatched


def load_nfhs4_total(districts):
    columns = {
        "State": "state_name",
        "District": "district_name",
        "Year": "year_label",
        "Residence Type": "residence_type",
        "Children Under 5 Years Who Are Stunted (Height-For-Age) (%) (UOM:%(Percentage)), Scaling Factor:1": "stunting_pct",
        "Children Under 5 Years Who Are Wasted (Weight-For-Height) (%) (UOM:%(Percentage)), Scaling Factor:1": "wasting_pct",
        "Children Under 5 Years Who Are Underweight (Weight-For-Age) (%) (UOM:%(Percentage)), Scaling Factor:1": "underweight_pct",
        "Children Age Group 6 To 59 Months Who Are Anaemic (%) (UOM:%(Percentage)), Scaling Factor:1": "anaemia_children_u5_pct",
        "Population Living In Households With An Improved Drinking-Water Source (%) (UOM:%(Percentage)), Scaling Factor:1": "improved_water_pct",
        "Population Living In Households That Use An Improved Sanitation Facility (%) (UOM:%(Percentage)), Scaling Factor:1": "improved_sanitation_pct",
        "Households Using Clean Fuel For Cooking (%) (UOM:%(Percentage)), Scaling Factor:1": "clean_fuel_pct",
        "Women With 10 Or More Years Of Schooling In The Age Group Of 15 To 49 Years (%) (UOM:%(Percentage)), Scaling Factor:1": "women_10plus_schooling_pct",
        "Women Age Group 15 To 49 Years Who Are Literate (%) (UOM:%(Percentage)), Scaling Factor:1": "women_literacy_pct",
    }
    nfhs4 = pd.read_csv(NFHS4_PATH, usecols=list(columns.keys())).rename(columns=columns)
    nfhs4 = nfhs4[nfhs4["residence_type"].eq("Total")].copy()
    mapped, summary, unmatched = map_to_districts(
        nfhs4.rename(columns={"state_name": "State", "district_name": "District"}),
        districts,
        source_name="nfhs4_total",
    )
    keep_cols = [
        "district_id",
        "State",
        "District",
        "year_label",
        "stunting_pct",
        "wasting_pct",
        "underweight_pct",
        "anaemia_children_u5_pct",
        "improved_water_pct",
        "improved_sanitation_pct",
        "clean_fuel_pct",
        "women_10plus_schooling_pct",
        "women_literacy_pct",
        "state_key",
        "district_key",
    ]
    cleaned = mapped[keep_cols].rename(columns={"State": "state_name", "District": "district_name"})
    return cleaned, summary, unmatched


def load_nfhs5(districts):
    columns = {
        "State": "state_name",
        "District": "district_name",
        "Year": "year_label",
        "Children Under 5 Years Who Are Stunted (Height-For-Age) (%) (UOM:%(Percentage)), Scaling Factor:1": "stunting_pct",
        "Children Under 5 Years Who Are Wasted (Weight-For-Height) (%) (UOM:%(Percentage)), Scaling Factor:1": "wasting_pct",
        "Children Under 5 Years Who Are Underweight (Weight-For-Age) (%) (UOM:%(Percentage)), Scaling Factor:1": "underweight_pct",
        "Children Age Group 6 To 59 Months Who Are Anaemic (%) (UOM:%(Percentage)), Scaling Factor:1": "anaemia_children_u5_pct",
        "Population Living In Households With An Improved Drinking Water Source (%) (UOM:%(Percentage)), Scaling Factor:1": "improved_water_pct",
        "Population Living In Households That Use An Improved Sanitation Facility (%) (UOM:%(Percentage)), Scaling Factor:1": "improved_sanitation_pct",
        "Households Using Clean Fuel For Cooking (%) (UOM:%(Percentage)), Scaling Factor:1": "clean_fuel_pct",
        "Women With 10 Or More Years Of Schooling (%) (UOM:%(Percentage)), Scaling Factor:1": "women_10plus_schooling_pct",
        "Women Age Group 15 To 49 Years Who Are Literate (%) (UOM:%(Percentage)), Scaling Factor:1": "women_literacy_pct",
        "Institutional Births (%) (UOM:%(Percentage)), Scaling Factor:1": "institutional_births_pct",
    }
    nfhs5 = pd.read_csv(NFHS5_PATH, usecols=list(columns.keys())).rename(columns=columns)
    mapped, summary, unmatched = map_to_districts(
        nfhs5.rename(columns={"state_name": "State", "district_name": "District"}),
        districts,
        source_name="nfhs5",
    )
    keep_cols = [
        "district_id",
        "State",
        "District",
        "year_label",
        "stunting_pct",
        "wasting_pct",
        "underweight_pct",
        "anaemia_children_u5_pct",
        "improved_water_pct",
        "improved_sanitation_pct",
        "clean_fuel_pct",
        "women_10plus_schooling_pct",
        "women_literacy_pct",
        "institutional_births_pct",
        "state_key",
        "district_key",
    ]
    cleaned = mapped[keep_cols].rename(columns={"State": "state_name", "District": "district_name"})
    return cleaned, summary, unmatched


def load_agriculture_2019(districts):
    columns = {
        "State": "State",
        "District": "District",
        "Year": "year_label",
        "Crop Name": "crop_name",
        "Crop Season": "crop_season",
        "Land Area Utilized For Production (UOM:Ha(Hectare)), Scaling Factor:1": "area_ha",
        "Crop Production (UOM:t(Tonne)), Scaling Factor:1": "production_t",
        "Crop Yield (UOM:t/Ha(TonnesperHectare)), Scaling Factor:1": "yield_t_per_ha",
    }
    agri = pd.read_csv(AGRI_PATH, usecols=list(columns.keys())).rename(columns=columns)
    agri = agri[agri["year_label"].astype(str).str.contains("2019", na=False)].copy()
    mapped, summary, unmatched = map_to_districts(agri, districts, source_name="agriculture_2019")
    mapped["area_ha"] = pd.to_numeric(mapped["area_ha"], errors="coerce")
    mapped["production_t"] = pd.to_numeric(mapped["production_t"], errors="coerce")

    grouped = (
        mapped.groupby(["district_id", "state_key", "district_key"], dropna=False)
        .agg(
            crop_count=("crop_name", "nunique"),
            total_area_ha=("area_ha", "sum"),
            total_production_t=("production_t", "sum"),
        )
        .reset_index()
    )
    grouped["weighted_yield_t_per_ha"] = grouped["total_production_t"] / grouped["total_area_ha"]
    grouped.loc[grouped["total_area_ha"] <= 0, "weighted_yield_t_per_ha"] = pd.NA
    return grouped, summary, unmatched


def load_hmis_2019(districts):
    columns = {
        "State": "State",
        "District": "District",
        "Year": "year_label",
        "Institutional Deliveries (To Total Reported Deliveries) (%) (UOM:%(Percentage)), Scaling Factor:1": "institutional_deliveries_pct",
        "Pregnant Women Received 4 Ante Natal Care (Anc) Check Ups (To Total Anc Registrations) (%) (UOM:%(Percentage)), Scaling Factor:1": "anc_4plus_pct",
        "Immunisation Sessions Held (To Immunisation Sessions Planned) (%) (UOM:%(Percentage)), Scaling Factor:1": "immunisation_sessions_pct",
    }
    hmis = pd.read_csv(HMIS_PATH, usecols=list(columns.keys())).rename(columns=columns)
    hmis = hmis[hmis["year_label"].astype(str).str.contains("2019", na=False)].copy()
    mapped, summary, unmatched = map_to_districts(hmis, districts, source_name="hmis_2019")
    keep_cols = [
        "district_id",
        "State",
        "District",
        "year_label",
        "institutional_deliveries_pct",
        "anc_4plus_pct",
        "immunisation_sessions_pct",
        "state_key",
        "district_key",
    ]
    cleaned = mapped[keep_cols].rename(columns={"State": "state_name", "District": "district_name"})
    return cleaned, summary, unmatched


def load_jjm_2025(districts):
    columns = {
        "State": "State",
        "District": "District",
        "Year": "year_label",
        "As On Date": "as_on_date",
        "Number Of Villages (UOM:Number), Scaling Factor:1": "total_villages",
        "Number Of Har Ghar Jal Village Reported (UOM:Number), Scaling Factor:1": "hjg_villages_reported",
        "Number Of Har Ghar Jal Village Certifiied (UOM:Number), Scaling Factor:1": "hjg_villages_certified",
    }
    jjm = pd.read_csv(JJM_PATH, usecols=list(columns.keys())).rename(columns=columns)
    mapped, summary, unmatched = map_to_districts(jjm, districts, source_name="jjm_2025")
    for col in ["total_villages", "hjg_villages_reported", "hjg_villages_certified"]:
        mapped[col] = pd.to_numeric(mapped[col], errors="coerce")
    mapped["hjg_villages_reported_ratio"] = mapped["hjg_villages_reported"] / mapped["total_villages"]
    mapped["hjg_villages_certified_ratio"] = mapped["hjg_villages_certified"] / mapped["total_villages"]
    keep_cols = [
        "district_id",
        "State",
        "District",
        "year_label",
        "as_on_date",
        "total_villages",
        "hjg_villages_reported",
        "hjg_villages_certified",
        "hjg_villages_reported_ratio",
        "hjg_villages_certified_ratio",
        "state_key",
        "district_key",
    ]
    cleaned = mapped[keep_cols].rename(columns={"State": "state_name", "District": "district_name"})
    return cleaned, summary, unmatched


def build_analysis_tables(districts, nfhs4_total, nfhs5, agriculture_2019, hmis_2019, jjm_2025):
    analysis = districts.merge(
        nfhs5[
            [
                "district_id",
                "stunting_pct",
                "wasting_pct",
                "underweight_pct",
                "anaemia_children_u5_pct",
                "improved_water_pct",
                "improved_sanitation_pct",
                "clean_fuel_pct",
                "women_10plus_schooling_pct",
                "women_literacy_pct",
                "institutional_births_pct",
            ]
        ],
        on="district_id",
        how="left",
    )
    analysis = analysis.merge(
        agriculture_2019[
            [
                "district_id",
                "crop_count",
                "total_area_ha",
                "total_production_t",
                "weighted_yield_t_per_ha",
            ]
        ],
        on="district_id",
        how="left",
    )
    analysis = analysis.merge(
        hmis_2019[
            [
                "district_id",
                "institutional_deliveries_pct",
                "anc_4plus_pct",
                "immunisation_sessions_pct",
            ]
        ],
        on="district_id",
        how="left",
    )
    analysis = analysis.merge(
        jjm_2025[
            [
                "district_id",
                "hjg_villages_reported_ratio",
                "hjg_villages_certified_ratio",
            ]
        ],
        on="district_id",
        how="left",
    )
    analysis = analysis.merge(
        nfhs4_total[
            [
                "district_id",
                "stunting_pct",
                "wasting_pct",
                "underweight_pct",
                "anaemia_children_u5_pct",
            ]
        ].rename(
            columns={
                "stunting_pct": "stunting_pct_nfhs4",
                "wasting_pct": "wasting_pct_nfhs4",
                "underweight_pct": "underweight_pct_nfhs4",
                "anaemia_children_u5_pct": "anaemia_children_u5_pct_nfhs4",
            }
        ),
        on="district_id",
        how="left",
    )

    core_columns = [
        "stunting_pct",
        "wasting_pct",
        "underweight_pct",
        "anaemia_children_u5_pct",
        "improved_water_pct",
        "institutional_deliveries_pct",
        "weighted_yield_t_per_ha",
    ]
    analysis["usable_for_eda"] = analysis[core_columns].notna().all(axis=1).astype(int)

    nutrition_change = analysis[
        [
            "district_id",
            "state_name",
            "district_name",
            "stunting_pct_nfhs4",
            "wasting_pct_nfhs4",
            "underweight_pct_nfhs4",
            "anaemia_children_u5_pct_nfhs4",
            "stunting_pct",
            "wasting_pct",
            "underweight_pct",
            "anaemia_children_u5_pct",
        ]
    ].copy()
    nutrition_change = nutrition_change.dropna(
        subset=[
            "stunting_pct_nfhs4",
            "wasting_pct_nfhs4",
            "underweight_pct_nfhs4",
            "anaemia_children_u5_pct_nfhs4",
            "stunting_pct",
            "wasting_pct",
            "underweight_pct",
            "anaemia_children_u5_pct",
        ]
    )
    nutrition_change["stunting_change_4_to_5"] = nutrition_change["stunting_pct"] - nutrition_change["stunting_pct_nfhs4"]
    nutrition_change["wasting_change_4_to_5"] = nutrition_change["wasting_pct"] - nutrition_change["wasting_pct_nfhs4"]
    nutrition_change["underweight_change_4_to_5"] = nutrition_change["underweight_pct"] - nutrition_change["underweight_pct_nfhs4"]
    nutrition_change["anaemia_change_4_to_5"] = (
        nutrition_change["anaemia_children_u5_pct"] - nutrition_change["anaemia_children_u5_pct_nfhs4"]
    )

    return analysis, nutrition_change


def normalize_analysis_table(analysis):
    normalized = analysis.copy()
    normalize_columns = [
        "stunting_pct",
        "wasting_pct",
        "underweight_pct",
        "anaemia_children_u5_pct",
        "improved_water_pct",
        "improved_sanitation_pct",
        "clean_fuel_pct",
        "women_10plus_schooling_pct",
        "women_literacy_pct",
        "institutional_births_pct",
        "crop_count",
        "total_area_ha",
        "total_production_t",
        "weighted_yield_t_per_ha",
        "institutional_deliveries_pct",
        "anc_4plus_pct",
        "immunisation_sessions_pct",
        "hjg_villages_reported_ratio",
        "hjg_villages_certified_ratio",
        "stunting_pct_nfhs4",
        "wasting_pct_nfhs4",
        "underweight_pct_nfhs4",
        "anaemia_children_u5_pct_nfhs4",
    ]

    summary_rows = []
    for col in normalize_columns:
        series = pd.to_numeric(normalized[col], errors="coerce")
        mean_value = series.mean(skipna=True)
        std_value = series.std(skipna=True, ddof=0)

        if pd.isna(std_value) or std_value == 0:
            normalized[f"z_{col}"] = pd.NA
        else:
            normalized[f"z_{col}"] = (series - mean_value) / std_value

        summary_rows.append(
            {
                "column_name": col,
                "mean_value": mean_value,
                "std_value": std_value,
                "non_null_count": int(series.notna().sum()),
            }
        )

    normalization_summary = pd.DataFrame(summary_rows)
    return normalized, normalization_summary


def write_database():
    districts = build_district_reference()
    nfhs4_total, nfhs4_summary, nfhs4_unmatched = load_nfhs4_total(districts)
    nfhs5, nfhs5_summary, nfhs5_unmatched = load_nfhs5(districts)
    agriculture_2019, agri_summary, agri_unmatched = load_agriculture_2019(districts)
    hmis_2019, hmis_summary, hmis_unmatched = load_hmis_2019(districts)
    jjm_2025, jjm_summary, jjm_unmatched = load_jjm_2025(districts)

    analysis_district, nutrition_change = build_analysis_tables(
        districts,
        nfhs4_total,
        nfhs5,
        agriculture_2019,
        hmis_2019,
        jjm_2025,
    )
    analysis_district_normalized, normalization_summary = normalize_analysis_table(analysis_district)

    merge_summary = pd.concat(
        [nfhs4_summary, nfhs5_summary, agri_summary, hmis_summary, jjm_summary],
        ignore_index=True,
    )
    merge_unmatched = pd.concat(
        [nfhs4_unmatched, nfhs5_unmatched, agri_unmatched, hmis_unmatched, jjm_unmatched],
        ignore_index=True,
    )

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DB_PATH) as conn:
        districts.to_sql("districts", conn, index=False, if_exists="replace")
        nfhs4_total.to_sql("nfhs4_total", conn, index=False, if_exists="replace")
        nfhs5.to_sql("nfhs5", conn, index=False, if_exists="replace")
        agriculture_2019.to_sql("agriculture_2019", conn, index=False, if_exists="replace")
        hmis_2019.to_sql("hmis_2019", conn, index=False, if_exists="replace")
        jjm_2025.to_sql("jjm_2025", conn, index=False, if_exists="replace")
        analysis_district.to_sql("analysis_district", conn, index=False, if_exists="replace")
        analysis_district_normalized.to_sql("analysis_district_normalized", conn, index=False, if_exists="replace")
        nutrition_change.to_sql("nutrition_change_4_to_5", conn, index=False, if_exists="replace")
        normalization_summary.to_sql("normalization_summary", conn, index=False, if_exists="replace")
        merge_summary.to_sql("merge_summary", conn, index=False, if_exists="replace")
        merge_unmatched.to_sql("merge_unmatched", conn, index=False, if_exists="replace")

    print(f"Created SQLite database: {DB_PATH}")
    print(f"Districts in analysis frame: {len(analysis_district)}")
    print(f"Districts usable for EDA core variables: {int(analysis_district['usable_for_eda'].sum())}")
    print(f"Normalized variables created: {len(normalization_summary)}")
    print("Merge coverage summary:")
    print(merge_summary.to_string(index=False))


if __name__ == "__main__":
    write_database()
