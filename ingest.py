import re
import warnings
import pandas as pd
from sqlalchemy import create_engine, text

warnings.filterwarnings("ignore")

DB_PATH = "D:/Ashoka University/Academics/Spring - 2026/DSM/Project/Database.db"
engine = create_engine(f"sqlite:///{DB_PATH}")
BASE = "D:/Ashoka University/Academics/Spring - 2026/DSM/Project/"


def extract_year(s):
    m = re.search(r"(\d{4})", str(s))
    return int(m.group(1)) if m else None

def norm(s):
    return str(s).strip().lower()


print("Dropping old tables...")
with engine.begin() as conn:
    for tbl in ["jjm_water", "hmis", "agriculture", "nfhs5", "nfhs4", "districts"]:
        conn.execute(text(f"DROP TABLE IF EXISTS {tbl}"))
print("  Done.\n")


print("Building districts...")
frames = []
for p in [
    BASE + "NFHS-4.csv", BASE + "NFHS-5.csv",
    BASE + "AgricultureStatistics.csv",
    BASE + "HMIS (2017-18,2019-20).csv",
    BASE + "JalJeevanMission.csv",
]:
    tmp = pd.read_csv(p, usecols=["State", "District"])
    tmp.columns = ["state", "district"]
    tmp["state"]    = tmp["state"].str.strip().str.lower()
    tmp["district"] = tmp["district"].str.strip().str.lower()
    frames.append(tmp)

districts = pd.concat(frames).drop_duplicates().dropna().reset_index(drop=True)
districts.insert(0, "district_id", districts.index + 1)

with engine.begin() as conn:
    conn.execute(text("""
        CREATE TABLE districts (
            district_id INTEGER PRIMARY KEY,
            state       TEXT NOT NULL,
            district    TEXT NOT NULL,
            UNIQUE (state, district)
        )
    """))
districts.to_sql("districts", engine, if_exists="append", index=False)
print(f"  {len(districts)} districts.\n")

lookup = districts.set_index(["state", "district"])["district_id"].to_dict()
def did(state, district):
    return lookup.get((norm(state), norm(district)))


print("Loading NFHS-4...")
raw4 = pd.read_csv(BASE + "NFHS-4.csv")

# Exact original column name → short name
cols4 = {
    "State":           "state",
    "District":        "district",
    "Year":            "year",
    "Residence Type":  "residence_type",
    # --- Malnutrition (core outcomes) ---
    "Children Under 5 Years Who Are Stunted (Height-For-Age) (%) (UOM:%(Percentage)), Scaling Factor:1":             "stunting_pct",
    "Children Under 5 Years Who Are Wasted (Weight-For-Height) (%) (UOM:%(Percentage)), Scaling Factor:1":           "wasting_pct",
    "Children Under 5 Years Who Are Severely Wasted (Weight-For-Height) (%) (UOM:%(Percentage)), Scaling Factor:1":  "severe_wasting_pct",
    "Children Under 5 Years Who Are Underweight (Weight-For-Age) (%) (UOM:%(Percentage)), Scaling Factor:1":         "underweight_pct",
    "Children Age Group 6 To 59 Months Who Are Anaemic (%) (UOM:%(Percentage)), Scaling Factor:1":                   "anaemia_children_u5_pct",
    # --- Anaemia (women) ---
    "Women Age Group 15 To 49 Years Who Are Anaemic (%) (UOM:%(Percentage)), Scaling Factor:1":                      "anaemia_women_pct",
    "Pregnant Women Age Group 15 To 49 Years Who Are Anaemic (%) (UOM:%(Percentage)), Scaling Factor:1":             "anaemia_pregnant_women_pct",
    "Non-Pregnant Women Age Group 15 To 49 Years Who Are Anaemic (%) (UOM:%(Percentage)), Scaling Factor:1":         "anaemia_non_pregnant_women_pct",
    # --- Child feeding & diet ---
    "Children Under Age 3 Years Breastfed Within One Hour Of Birth (%) (UOM:%(Percentage)), Scaling Factor:1":       "breastfed_within_1hr_pct",
    "Children Under Age 6 Months Exclusively Breastfed (%) (UOM:%(Percentage)), Scaling Factor:1":                   "exclusive_breastfed_pct",
    "Children Age Group 6 To 8 Months Receiving Solid Or Semisolid Food And Breastmilk (%) (UOM:%(Percentage)), Scaling Factor:1": "solid_food_6_8m_pct",
    "Children Age Group 6 To 23 Months Receiving An Adequate Diet (%) (UOM:%(Percentage)), Scaling Factor:1":        "adequate_diet_6_23m_pct",
    "Breastfeeding Children Age Group 6 To 23 Months Receiving An Adequate Diet (%) (UOM:%(Percentage)), Scaling Factor:1": "adequate_diet_breastfed_pct",
    "Children Age 9 To 35 Months Who Received Vitamin A Dose In The Last 6 Months (%) (UOM:%(Percentage)), Scaling Factor:1": "vitamin_a_pct",
    # --- Vaccination ---
    "Children In The Age Group Of 12 To 23 Months Who Are Fully Immunized (Bacille Calmette-Guerin (Bcg), Measles, And 3 Doses Each Of Polio And Dpt) (%) (UOM:%(Percentage)), Scaling Factor:1": "full_immunisation_pct",
    "Children Age Group 12 To 23 Months Who Have Received Bacillus Calmette Guerin (Bcg) (%) (UOM:%(Percentage)), Scaling Factor:1":  "bcg_vaccine_pct",
    "Children Age Group 12 To 23 Months Who Have Received 3 Doses Of Polio Vaccine (%) (UOM:%(Percentage)), Scaling Factor:1":        "polio3_vaccine_pct",
    "Children Age Group 12 To 23 Months Who Have Received 3 Doses Of Dpt Vaccine (%) (UOM:%(Percentage)), Scaling Factor:1":          "dpt3_vaccine_pct",
    "Children Age Group 12 To 23 Months Who Have Received 3 Doses Of Measles Vaccine (%) (UOM:%(Percentage)), Scaling Factor:1":      "measles_vaccine_pct",
    "Children Age Group 12 To 23 Months Who Have Received 3 Doses Of Hepatitis B Vaccine (%) (UOM:%(Percentage)), Scaling Factor:1":  "hepb3_vaccine_pct",
    # --- Disease burden ---
    "Prevalence Of Diarrhoea In The 2 Weeks Preceding The Survey (%) (UOM:%(Percentage)), Scaling Factor:1":         "diarrhoea_prevalence_pct",
    "Children With Diarrhoea In The 2 Weeks Preceding The Survey Who Received Oral Rehydration Salts (%) (UOM:%(Percentage)), Scaling Factor:1": "diarrhoea_ors_pct",
    "Children With Diarrhoea In The 2 Weeks Preceding The Survey Who Received Zinc (%) (UOM:%(Percentage)), Scaling Factor:1":                   "diarrhoea_zinc_pct",
    "Prevalence Of Symptoms Of Acute Respiratory Infection (Ari) In The 2 Weeks Preceding The Survey (%) (UOM:%(Percentage)), Scaling Factor:1": "ari_prevalence_pct",
    # --- Maternal & delivery care ---
    "Institutional Births (%) (UOM:%(Percentage)), Scaling Factor:1":                                                "institutional_births_pct",
    "Institutional Births In Public Facility (%) (UOM:%(Percentage)), Scaling Factor:1":                             "institutional_births_public_pct",
    "Mothers Who Had An Antenatal Check-Up In The First Trimester (%) (UOM:%(Percentage)), Scaling Factor:1":        "anc_first_trimester_pct",
    "Mothers Who Had At Least 4 Antenatal Care Visits (%) (UOM:%(Percentage)), Scaling Factor:1":                    "anc_4plus_pct",
    "Mothers Who Consumed Iron Folic Acid For 100 Days Or More When They Were Pregnant (%) (UOM:%(Percentage)), Scaling Factor:1": "ifa_100days_pct",
    "Mothers Who Received Postnatal Care From A Doctor Or Nurse Or Lady Health Visitor (Lhv) Or Auxiliary Nurse Midwifery (Anm) Or Midwife Or Other Health Personnel Within 2 Days Of Delivery (%) (UOM:%(Percentage)), Scaling Factor:1": "postnatal_care_pct",
    # --- WASH (water, sanitation, hygiene) ---
    "Population Living In Households With An Improved Drinking-Water Source (%) (UOM:%(Percentage)), Scaling Factor:1": "improved_water_pct",
    "Population Living In Households That Use An Improved Sanitation Facility (%) (UOM:%(Percentage)), Scaling Factor:1": "improved_sanitation_pct",
    "Households Using Clean Fuel For Cooking (%) (UOM:%(Percentage)), Scaling Factor:1":                              "clean_fuel_pct",
    "Population Living In Households With Electricity (%) (UOM:%(Percentage)), Scaling Factor:1":                     "electricity_pct",
    "Households Using Iodized Salt (%) (UOM:%(Percentage)), Scaling Factor:1":                                        "iodized_salt_pct",
    # --- Socioeconomic controls ---
    "Women Age Group 15 To 49 Years Who Are Literate (%) (UOM:%(Percentage)), Scaling Factor:1":                     "women_literate_pct",
    "Women With 10 Or More Years Of Schooling In The Age Group Of 15 To 49 Years (%) (UOM:%(Percentage)), Scaling Factor:1": "women_10yr_school_pct",
    "Women In The Age Group Of 20 To 24 Years Married Before Age 18 Years (%) (UOM:%(Percentage)), Scaling Factor:1": "child_marriage_pct",
    "Women With Body Mass Index (Bmi) Below Normal (%) (UOM:%(Percentage)), Scaling Factor:1":                        "women_bmi_low_pct",
    "Population And Household Profile-Households With Any Usual Member Covered Under A Health Insurance Or Financing Scheme (%) (UOM:%(Percentage)), Scaling Factor:1": "health_insurance_pct",
    "Population And Household Profile-Sex Ratio Of The Total Population (Females Per 1,000 Males) (UOM:Number), Scaling Factor:1": "sex_ratio",
    "Population And Household Profile-Sex Ratio At Birth For Children Born In The Last Five Years (Females Per 1,000 Males) (UOM:Number), Scaling Factor:1": "sex_ratio_at_birth",
    "Population Below Age 15 Years (%) (UOM:%(Percentage)), Scaling Factor:1":                                        "pop_below_15_pct",
    "Average Out Of Pocket Expenditure For Each Delivery In Public Health Facility (UOM:INR(IndianRupees)), Scaling Factor:1": "oop_delivery_cost_inr",
}

nfhs4 = raw4[list(cols4.keys())].rename(columns=cols4).copy()
nfhs4["year_int"]     = nfhs4["year"].apply(extract_year)
nfhs4["state"]        = nfhs4["state"].str.strip().str.lower()
nfhs4["district"]     = nfhs4["district"].str.strip().str.lower()
nfhs4["district_id"]  = nfhs4.apply(lambda r: did(r["state"], r["district"]), axis=1)
nfhs4.to_sql("nfhs4", engine, if_exists="replace", index=False, method="multi", chunksize=500)
print(f"  {len(nfhs4)} rows, {len(nfhs4.columns)} columns.\n")


print("Loading NFHS-5...")
raw5 = pd.read_csv(BASE + "NFHS-5.csv")

cols5 = {
    "State":    "state",
    "District": "district",
    "Year":     "year",
    # --- Malnutrition (core outcomes) ---
    "Children Under 5 Years Who Are Stunted (Height-For-Age) (%) (UOM:%(Percentage)), Scaling Factor:1":             "stunting_pct",
    "Children Under 5 Years Who Are Wasted (Weight-For-Height) (%) (UOM:%(Percentage)), Scaling Factor:1":           "wasting_pct",
    "Children Under 5 Years Who Are Severely Wasted (Weight-For-Height) (%) (UOM:%(Percentage)), Scaling Factor:1":  "severe_wasting_pct",
    "Children Under 5 Years Who Are Underweight (Weight-For-Age) (%) (UOM:%(Percentage)), Scaling Factor:1":         "underweight_pct",
    "Children Under 5 Years Who Are Overweight (Weight-For-Height) (%) (UOM:%(Percentage)), Scaling Factor:1":       "overweight_children_pct",
    "Children Age Group 6 To 59 Months Who Are Anaemic (%) (UOM:%(Percentage)), Scaling Factor:1":                   "anaemia_children_u5_pct",
    # --- Anaemia (women) ---
    "Women Age Group 15 To 49 Years Who Are Anaemic (%) (UOM:%(Percentage)), Scaling Factor:1":                      "anaemia_women_pct",
    "Women Age Group 15 To 19 Years Who Are Anaemic (%) (UOM:%(Percentage)), Scaling Factor:1":                      "anaemia_women_15_19_pct",
    "Pregnant Women Age Group 15 To 49 Years Who Are Anaemic (%) (UOM:%(Percentage)), Scaling Factor:1":             "anaemia_pregnant_women_pct",
    "Non-Pregnant Women Age Group 15 To 49 Years Who Are Anaemic (%) (UOM:%(Percentage)), Scaling Factor:1":         "anaemia_non_pregnant_women_pct",
    # --- Child feeding & diet ---
    "Children Under Age 3 Years Breastfed Within One Hour Of Birth (%) (UOM:%(Percentage)), Scaling Factor:1":       "breastfed_within_1hr_pct",
    "Children Under Age 6 Months Exclusively Breastfed (%) (UOM:%(Percentage)), Scaling Factor:1":                   "exclusive_breastfed_pct",
    "Children Age Group 6 To 8 Months Receiving Solid Or Semisolid Food And Breastmilk (%) (UOM:%(Percentage)), Scaling Factor:1": "solid_food_6_8m_pct",
    "Children Age Group 6 To 23 Months Receiving An Adequate Diet (%) (UOM:%(Percentage)), Scaling Factor:1":        "adequate_diet_6_23m_pct",
    "Breastfeeding Children Age Group 6 To 23 Months Receiving An Adequate Diet (%) (UOM:%(Percentage)), Scaling Factor:1": "adequate_diet_breastfed_pct",
    "Children Age Group 9 To 35 Months Who Received Vitamin A Dose In The Last 6 Months (%) (UOM:%(Percentage)), Scaling Factor:1": "vitamin_a_pct",
    # --- Vaccination ---
    "Children Age Group 12 To 23 Months Fully Vaccinated Based On Information From Either Vaccination Card Or Mothers Recall (%) (UOM:%(Percentage)), Scaling Factor:1": "full_vaccination_pct",
    "Children Age Group 12 To 23 Months Fully Vaccinated Based On Information From Vaccination Card Only (%) (UOM:%(Percentage)), Scaling Factor:1":                     "full_vaccination_card_only_pct",
    "Children Age Group 12 To 23 Months Who Have Received Bacillus Calmette Guerin (Bcg) (%) (UOM:%(Percentage)), Scaling Factor:1":  "bcg_vaccine_pct",
    "Children Age Group 12 To 23 Months Who Have Received 3 Doses Of Polio Vaccine (%) (UOM:%(Percentage)), Scaling Factor:1":        "polio3_vaccine_pct",
    "Children Age Group 12 To 23 Months Who Have Received 3 Doses Of Penta Or Diphtheria Tetanus Toxoids And Pertussis (Dtp) Vaccine (%) (UOM:%(Percentage)), Scaling Factor:1": "dtp3_vaccine_pct",
    "Children Age Group 12 To 23 Months Who Have Received 3 Doses Of Penta Or Hepatitis B Vaccine (%) (UOM:%(Percentage)), Scaling Factor:1":  "hepb3_vaccine_pct",
    "Children Age Group 12 To 23 Months Who Have Received The First Dose Of Measles Containing Vaccine (Mcv) (%) (UOM:%(Percentage)), Scaling Factor:1":  "measles_mcv1_pct",
    "Children Age Group 24 To 35 Months Who Have Received A Second Dose Of Measles Containing Vaccine (Mcv) (%) (UOM:%(Percentage)), Scaling Factor:1":   "measles_mcv2_pct",
    "Children Age Group 12 To 23 Months Who Have Received 3 Doses Of Rotavirus Vaccine (%) (UOM:%(Percentage)), Scaling Factor:1":    "rotavirus3_pct",
    # --- Disease burden ---
    "Prevalence Of Diarrhoea In The 2 Weeks Preceding The Survey (%) (UOM:%(Percentage)), Scaling Factor:1":         "diarrhoea_prevalence_pct",
    "Children With Diarrhoea In The 2 Weeks Preceding The Survey Who Received Oral Rehydration Salts (%) (UOM:%(Percentage)), Scaling Factor:1": "diarrhoea_ors_pct",
    "Children With Diarrhoea In The 2 Weeks Preceding The Survey Who Received Zinc (%) (UOM:%(Percentage)), Scaling Factor:1":                   "diarrhoea_zinc_pct",
    "Prevalence Of Symptoms Of Acute Respiratory Infection (Ari) In The 2 Weeks Preceding The Survey (%) (UOM:%(Percentage)), Scaling Factor:1": "ari_prevalence_pct",
    # --- Maternal & delivery care ---
    "Institutional Births (%) (UOM:%(Percentage)), Scaling Factor:1":                                                "institutional_births_pct",
    "Institutional Births In Public Facility (%) (UOM:%(Percentage)), Scaling Factor:1":                             "institutional_births_public_pct",
    "Births Attended By Skilled Health Personnel (%) (UOM:%(Percentage)), Scaling Factor:1":                         "skilled_birth_attendant_pct",
    "Mothers Who Had An Antenatal Check-Up In The First Trimester (%) (UOM:%(Percentage)), Scaling Factor:1":        "anc_first_trimester_pct",
    "Mothers Who Had At Least 4 Antenatal Care Visits (%) (UOM:%(Percentage)), Scaling Factor:1":                    "anc_4plus_pct",
    "Mothers Who Consumed Iron Folic Acid For 100 Days Or More When They Were Pregnant (%) (UOM:%(Percentage)), Scaling Factor:1": "ifa_100days_pct",
    "Mothers Who Consumed Iron Folic Acid For 180 Days Or More When They Were Pregnant (%) (UOM:%(Percentage)), Scaling Factor:1": "ifa_180days_pct",
    "Mothers Who Received Postnatal Care From A Doctor Or Nurse Or Lady Health Visitor (Lhv) Or Auxiliary Nurse Midwifery (Anm) Or Midwife Or Other Health Personnel Within 2 Days Of Delivery (%) (UOM:%(Percentage)), Scaling Factor:1": "postnatal_care_pct",
    "Average Out Of Pocket Expenditure For Each Delivery In Public Health Facility (UOM:INR(IndianRupees)), Scaling Factor:1": "oop_delivery_cost_inr",
    # --- WASH ---
    "Population Living In Households With An Improved Drinking Water Source (%) (UOM:%(Percentage)), Scaling Factor:1": "improved_water_pct",
    "Population Living In Households That Use An Improved Sanitation Facility (%) (UOM:%(Percentage)), Scaling Factor:1": "improved_sanitation_pct",
    "Households Using Clean Fuel For Cooking (%) (UOM:%(Percentage)), Scaling Factor:1":                              "clean_fuel_pct",
    "Population Living In Households With Electricity (%) (UOM:%(Percentage)), Scaling Factor:1":                     "electricity_pct",
    "Households Using Iodized Salt (%) (UOM:%(Percentage)), Scaling Factor:1":                                        "iodized_salt_pct",
    # --- Socioeconomic controls ---
    "Women Age Group 15 To 49 Years Who Are Literate (%) (UOM:%(Percentage)), Scaling Factor:1":                     "women_literate_pct",
    "Women With 10 Or More Years Of Schooling (%) (UOM:%(Percentage)), Scaling Factor:1":                            "women_10yr_school_pct",
    "Women Age Group 20 To 24 Years Married Before Age 18 Years (%) (UOM:%(Percentage)), Scaling Factor:1":          "child_marriage_pct",
    "Women With Body Mass Index (Bmi) Below Normal (%) (UOM:%(Percentage)), Scaling Factor:1":                        "women_bmi_low_pct",
    "Population And Household Profile-Households With Any Usual Member Covered Under A Health Insurance Or Financing Scheme (%) (UOM:%(Percentage)), Scaling Factor:1": "health_insurance_pct",
    "Population And Household Profile-Sex Ratio Of The Total Population (Females Per 1,000 Males) (UOM:Number), Scaling Factor:1": "sex_ratio",
    "Population And Household Profile-Sex Ratio At Birth For Children Born In The Last Five Years (Females Per 1,000 Males) (UOM:Number), Scaling Factor:1": "sex_ratio_at_birth",
    "Population Below Age 15 Years (%) (UOM:%(Percentage)), Scaling Factor:1":                                        "pop_below_15_pct",
    "Women Age Group 15 To 24 Years Who Use Hygienic Methods Of Protection During Their Menstrual Period (%) (UOM:%(Percentage)), Scaling Factor:1": "menstrual_hygiene_pct",
    "Children Under Age 5 Years Whose Birth Was Registered With The Civil Authority (%) (UOM:%(Percentage)), Scaling Factor:1": "birth_registration_pct",
}

# Only keep columns that exist in this file
cols5_present = {k: v for k, v in cols5.items() if k in raw5.columns}
nfhs5 = raw5[list(cols5_present.keys())].rename(columns=cols5_present).copy()
nfhs5["year_int"]    = nfhs5["year"].apply(extract_year)
nfhs5["state"]       = nfhs5["state"].str.strip().str.lower()
nfhs5["district"]    = nfhs5["district"].str.strip().str.lower()
nfhs5["district_id"] = nfhs5.apply(lambda r: did(r["state"], r["district"]), axis=1)
nfhs5.to_sql("nfhs5", engine, if_exists="replace", index=False, method="multi", chunksize=500)
print(f"  {len(nfhs5)} rows, {len(nfhs5.columns)} columns.\n")


print("Loading Agriculture...")
raw_ag = pd.read_csv(BASE + "AgricultureStatistics.csv")

cols_ag = {
    "State":    "state",
    "District": "district",
    "Year":     "year",
    "Crop Name":    "crop_name",
    "Crop Season":  "crop_season",
    "Land Area Utilized For Production (UOM:Ha(Hectare)), Scaling Factor:1": "area_ha",
    "Crop Production (UOM:t(Tonne)), Scaling Factor:1":                       "production_t",
    "Crop Yield (UOM:t/Ha(TonnesperHectare)), Scaling Factor:1":              "yield_t_per_ha",
}
agri = raw_ag[list(cols_ag.keys())].rename(columns=cols_ag).copy()
agri["year_int"]    = agri["year"].apply(extract_year)
agri["state"]       = agri["state"].str.strip().str.lower()
agri["district"]    = agri["district"].str.strip().str.lower()
agri["district_id"] = agri.apply(lambda r: did(r["state"], r["district"]), axis=1)
agri.to_sql("agriculture", engine, if_exists="replace", index=False, method="multi", chunksize=1000)
print(f"  {len(agri)} rows, {len(agri.columns)} columns.\n")


print("Loading HMIS...")
raw_hmis = pd.read_csv(BASE + "HMIS (2017-18,2019-20).csv")

cols_hmis = {
    "State":    "state",
    "District": "district",
    "Year":     "year",
    # --- ANC ---
    "Women Registered For Ante Natal Care(Anc) (UOM:Number), Scaling Factor:1":                                      "anc_registrations",
    "Women Registered For Ante Natal Care (Anc) Within First Trimester (UOM:Number), Scaling Factor:1":              "anc_first_trimester_n",
    "Registrations For Ante Natal Care (Anc) In The First Trimester (To Total Anc Registrations) (%) (UOM:%(Percentage)), Scaling Factor:1": "anc_first_trimester_pct",
    "Women Received 4 Or More (Anc) Check-Ups (UOM:Number), Scaling Factor:1":                                       "anc_4plus_n",
    "Pregnant Women Received 4 Ante Natal Care (Anc) Check Ups (To Total Anc Registrations) (%) (UOM:%(Percentage)), Scaling Factor:1":     "anc_4plus_pct",
    "Pregnant Women Received 180 Iron And Folic Acid Tablets (UOM:Number), Scaling Factor:1":                        "ifa_180_tablets_n",
    "Women Received 180 Ifa Tablets (To Total Anc Registrations) (%) (UOM:%(Percentage)), Scaling Factor:1":         "ifa_180_tablets_pct",
    "Women Having Tested Moderately Anemic With Hemoglobin (Hb)<11 (UOM:Number), Scaling Factor:1":                  "moderate_anaemia_n",
    "Women Having Tested With Severe Anemia With Hemoglobin (Hb) And Are Being Treated At An Institution (UOM:Number), Scaling Factor:1":   "severe_anaemia_n",
    "Pregnant Women With Hemoglobin (Hb) Levels<7 (Severe Anemia) (To Women With Hemoglobin (Hb) Levels<11 (Moderate Anemia)) (%) (UOM:%(Percentage)), Scaling Factor:1": "severe_anaemia_pct",
    # --- Delivery ---
    "Institutional Deliveries Includes Both Public And Private Institutions (UOM:Number), Scaling Factor:1":          "institutional_deliveries_n",
    "Institutional Deliveries (To Total Reported Deliveries) (%) (UOM:%(Percentage)), Scaling Factor:1":             "institutional_deliveries_pct",
    "Safe Deliveries (To Total Reported Deliveries) (%) (UOM:%(Percentage)), Scaling Factor:1":                      "safe_deliveries_pct",
    "Home Deliveries (To Total Reported Deliveries) (%) (UOM:%(Percentage)), Scaling Factor:1":                      "home_deliveries_pct",
    "Total Reported Deliveries (UOM:Number), Scaling Factor:1":                                                       "total_deliveries_n",
    "Maternal Deaths (UOM:Number), Scaling Factor:1":                                                                  "maternal_deaths_n",
    # --- Newborn care ---
    "Reported Live Births (UOM:Number), Scaling Factor:1":                                                            "live_births_n",
    "Newborns Weighed At Birth (To Reported Live Births) (%) (UOM:%(Percentage)), Scaling Factor:1":                 "newborns_weighed_pct",
    "Newborns Having Weight Less Than 25 Kg (To Newborns Weighed At Birth) (%) (UOM:%(Percentage)), Scaling Factor:1": "low_birth_weight_pct",
    "New Borns Breastfed Within 1 Hour (To Total Live Births) (%) (UOM:%(Percentage)), Scaling Factor:1":            "newborn_breastfed_1hr_pct",
    # --- Immunisation ---
    "Number Of Fully Immunized Children In The Age Group Of 9 To 11 Months (UOM:Number), Scaling Factor:1":          "fully_immunised_9_11m_n",
    "Newborns Given Bacillus Calmette Guerin  (Bcg) At Birth (To Reported Live Births) (%) (UOM:%(Percentage)), Scaling Factor:1": "bcg_at_birth_pct",
    "Newborns Given Oral Poliovirus Vaccines (Opv) At Birth (To Reported Live Births) (%) (UOM:%(Percentage)), Scaling Factor:1":  "opv_at_birth_pct",
    "Newborns Given Hep-B0 (Birth Dose) At Birth (To Total Reports Live Births) (%) (UOM:%(Percentage)), Scaling Factor:1":       "hepb_birth_dose_pct",
    "Infants Aged Up To 11 Months Who Received Measles And Measles Rubella Vaccine (To Reported Live Births) (%) (UOM:%(Percentage)), Scaling Factor:1": "measles_vaccine_pct",
    "Immunization Dropout Between Bacillus Calmette Guerin (Bcg) And Measles Vaccine (%) (UOM:%(Percentage)), Scaling Factor:1":  "immunisation_dropout_pct",
    "Immunisation Sessions Held (To Immunisation Sessions Planned) (%) (UOM:%(Percentage)), Scaling Factor:1":       "immunisation_sessions_pct",
    "Children Given Vitamin-A Dose 1 (To Reported Live Births) (%) (UOM:%(Percentage)), Scaling Factor:1":           "vitamin_a_dose1_pct",
    # --- Child morbidity ---
    "Children Under 5 Years Of Age Suffered From Diarrhea (UOM:Number), Scaling Factor:1":                           "u5_diarrhoea_n",
    "Children Under 5 Years Of Age Suffered From Malaria (UOM:Number), Scaling Factor:1":                            "u5_malaria_n",
    "Children Under 5 Years Of Age Suffered From Pneumonia (UOM:Number), Scaling Factor:1":                          "u5_pneumonia_n",
    "Children Under 5 Years Of Age Suffered From Tuberculosis (Tb) (UOM:Number), Scaling Factor:1":                  "u5_tb_n",
    "Infant Deaths Reported (UOM:Number), Scaling Factor:1":                                                          "infant_deaths_n",
    "Blood Smears Tested Positive For Plasmodium Falciparum (To Total Blood Smears Examined For Malaria) (%) (UOM:%(Percentage)), Scaling Factor:1": "malaria_pf_pct",
}

cols_hmis_present = {k: v for k, v in cols_hmis.items() if k in raw_hmis.columns}
hmis = raw_hmis[list(cols_hmis_present.keys())].rename(columns=cols_hmis_present).copy()
hmis["year_int"]    = hmis["year"].apply(extract_year)
hmis["state"]       = hmis["state"].str.strip().str.lower()
hmis["district"]    = hmis["district"].str.strip().str.lower()
hmis["district_id"] = hmis.apply(lambda r: did(r["state"], r["district"]), axis=1)
hmis.to_sql("hmis", engine, if_exists="replace", index=False, method="multi", chunksize=200)
print(f"  {len(hmis)} rows, {len(hmis.columns)} columns.\n")


print("Loading JJM...")
raw_jjm = pd.read_csv(BASE + "JalJeevanMission.csv")

cols_jjm = {
    "State":    "state",
    "District": "district",
    "Year":     "year",
    "As On Date": "as_on_date",
    "Number Of Block (UOM:Number), Scaling Factor:1":                         "total_blocks",
    "Number Of Har Ghar Jal Block Reported (UOM:Number), Scaling Factor:1":   "hjg_blocks_reported",
    "Number Of Har Ghar Jal Block Certified (UOM:Number), Scaling Factor:1":  "hjg_blocks_certified",
    "Number Of Panchayats (UOM:Number), Scaling Factor:1":                    "total_panchayats",
    "Number Of Har Ghar Jal Panchayat Reported (UOM:Number), Scaling Factor:1":  "hjg_panchayats_reported",
    "Number Of Har Ghar Jal Panchayat Certified (UOM:Number), Scaling Factor:1": "hjg_panchayats_certified",
    "Number Of Villages (UOM:Number), Scaling Factor:1":                      "total_villages",
    "Number Of Har Ghar Jal Village Reported (UOM:Number), Scaling Factor:1": "hjg_villages_reported",
    "Number Of Har Ghar Jal Village Certifiied (UOM:Number), Scaling Factor:1": "hjg_villages_certified",
}

jjm = raw_jjm[list(cols_jjm.keys())].rename(columns=cols_jjm).copy()
jjm["year_int"]    = jjm["year"].apply(extract_year)
jjm["state"]       = jjm["state"].str.strip().str.lower()
jjm["district"]    = jjm["district"].str.strip().str.lower()
jjm["district_id"] = jjm.apply(lambda r: did(r["state"], r["district"]), axis=1)
jjm.to_sql("jjm_water", engine, if_exists="replace", index=False, method="multi", chunksize=500)
print(f"  {len(jjm)} rows, {len(jjm.columns)} columns.\n")


print("Adding indexes...")
with engine.begin() as conn:
    for tbl in ["nfhs4", "nfhs5", "agriculture", "hmis", "jjm_water"]:
        conn.execute(text(f"CREATE INDEX IF NOT EXISTS idx_{tbl}_did  ON {tbl}(district_id)"))
        conn.execute(text(f"CREATE INDEX IF NOT EXISTS idx_{tbl}_year ON {tbl}(year_int)"))
    conn.execute(text("CREATE INDEX IF NOT EXISTS idx_agri_crop ON agriculture(crop_name)"))


print("\n== Summary ==")
with engine.connect() as conn:
    for tbl in ["districts", "nfhs4", "nfhs5", "agriculture", "hmis", "jjm_water"]:
        rows = conn.execute(text(f"SELECT COUNT(*) FROM {tbl}")).scalar()
        ncols = len(conn.execute(text(f"PRAGMA table_info({tbl})")).fetchall())
        print(f"  {tbl:15s}  rows={rows:>7,}  cols={ncols}")

print(f"\nDatabase: {DB_PATH}")
print("Connection string for tools: sqlite:///dsm_project.db")
print("\nDone.")
