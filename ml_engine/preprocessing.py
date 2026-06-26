import pandas as pd
import numpy as np


def load_data(beneficiary_path, inpatient_path, outpatient_path, labels_path):
    benf_df = pd.read_csv(beneficiary_path)
    inpatient_df = pd.read_csv(inpatient_path)
    outpatient_df = pd.read_csv(outpatient_path)
    labels_df = pd.read_csv(labels_path)
    return benf_df, inpatient_df, outpatient_df, labels_df


def inspect_data(df, name):
    print(f"\n{'='*60}")
    print(f"DATASET: {name}")
    print(f"{'='*60}")

    print("\nShape:")
    print(df.shape)

    print("\nColumns:")
    print(df.columns.tolist())

    print("\nData Types:")
    print(df.dtypes)

    print("\nMissing Values:")
    print(df.isnull().sum())

    print("\nDuplicate Rows:")
    print(df.duplicated().sum())

    print("\nSample Data:")
    display(df.head())


def clean_beneficiary_data(benf_df, inpatient_df, outpatient_df):
    REF_DATE = max(inpatient_df["ClaimEndDt"].max(), outpatient_df["ClaimEndDt"].max())
    REF_DATE = pd.to_datetime(REF_DATE)

    benf_df["DOB"] = pd.to_datetime(benf_df["DOB"])
    benf_df["DOD"] = pd.to_datetime(benf_df["DOD"], errors="coerce")

    benf_df["Age"] = ((REF_DATE - benf_df["DOB"]).dt.days / 365.25).astype(int)
    benf_df["IsDead"] = benf_df["DOD"].notna().astype(int)

    CHRONIC_COLS = [c for c in benf_df.columns if c.startswith("ChronicCond_")]
    for col in CHRONIC_COLS:
        benf_df[col] = (benf_df[col] == 1).astype(int)

    benf_df["ChronicCondCount"] = benf_df[CHRONIC_COLS].sum(axis=1)
    benf_df["RenalDiseaseIndicator"] = benf_df["RenalDiseaseIndicator"].map({'Y': 1, '0': 0})
    benf_df["Gender"] = (benf_df["Gender"] == 1).astype(int)

    return benf_df


def clean_inpatient_data(inpatient_df):
    DATE_COLS_INP = ["ClaimStartDt", "ClaimEndDt", "AdmissionDt", "DischargeDt"]
    for col in DATE_COLS_INP:
        inpatient_df[col] = pd.to_datetime(inpatient_df[col])

    inpatient_df["ClaimDuration"] = (inpatient_df["ClaimEndDt"] - inpatient_df["ClaimStartDt"]).dt.days
    inpatient_df["DaysInHospital"] = (inpatient_df["DischargeDt"] - inpatient_df["AdmissionDt"]).dt.days
    inpatient_df["ClaimDuration"] = inpatient_df["ClaimDuration"].clip(lower=0)
    inpatient_df["DaysInHospital"] = inpatient_df["DaysInHospital"].clip(lower=0)

    inpatient_df["DeductibleAmtPaid"] = inpatient_df["DeductibleAmtPaid"].fillna(0)

    DIAG_COLS = [f"ClmDiagnosisCode_{i}" for i in range(1, 11)]
    for col in DIAG_COLS:
        inpatient_df[col] = inpatient_df[col].fillna("NONE")

    PROC_COLS = [f"ClmProcedureCode_{i}" for i in range(1, 7)]
    for col in PROC_COLS:
        inpatient_df[col] = inpatient_df[col].fillna(0).astype(int).astype(str)
        inpatient_df[col] = inpatient_df[col].replace("0", "NONE")

    inpatient_df["SameAttendOper"] = (
        inpatient_df["AttendingPhysician"].notna() &
        inpatient_df["OperatingPhysician"].notna() &
        (inpatient_df["AttendingPhysician"] == inpatient_df["OperatingPhysician"])
    ).astype(int)

    return inpatient_df


def clean_outpatient_data(outpatient_df):
    DATE_COLS_OUT = ["ClaimStartDt", "ClaimEndDt"]
    for col in DATE_COLS_OUT:
        outpatient_df[col] = pd.to_datetime(outpatient_df[col])

    outpatient_df["ClaimDuration"] = (outpatient_df["ClaimEndDt"] - outpatient_df["ClaimStartDt"]).dt.days
    outpatient_df["ClaimDuration"] = outpatient_df["ClaimDuration"].clip(lower=0)

    DIAG_COLS = [f"ClmDiagnosisCode_{i}" for i in range(1, 11)]
    for col in DIAG_COLS:
        outpatient_df[col] = outpatient_df[col].fillna("NONE")

    PROC_COLS = [f"ClmProcedureCode_{i}" for i in range(1, 7)]
    for col in PROC_COLS:
        outpatient_df[col] = outpatient_df[col].fillna(0).astype(int).astype(str)
        outpatient_df[col] = outpatient_df[col].replace("0", "NONE")

    outpatient_df["ClmAdmitDiagnosisCode"] = outpatient_df["ClmAdmitDiagnosisCode"].fillna("NONE")
    outpatient_df["SameAttendOper"] = (
        outpatient_df["AttendingPhysician"].notna() &
        outpatient_df["OperatingPhysician"].notna() &
        (outpatient_df["AttendingPhysician"] == outpatient_df["OperatingPhysician"])
    ).astype(int)

    outpatient_df["DaysInHospital"] = 0

    return outpatient_df


def merge_claims(inpatient_df, outpatient_df):
    inpatient_df["ClaimType"] = "Inpatient"
    outpatient_df["ClaimType"] = "Outpatient"

    for col in ["AdmissionDt", "DischargeDt", "DiagnosisGroupCode"]:
        if col not in outpatient_df.columns:
            outpatient_df[col] = np.nan

    claims = pd.concat([inpatient_df, outpatient_df], ignore_index=True, sort=False)
    return claims


def merge_beneficiary(claims, benf_df):
    return claims.merge(benf_df, on="BeneID", how="left")
