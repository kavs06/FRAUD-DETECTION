import pandas as pd


def extract_top_codes(claims_bene, top_n=100):
    top100_diag = (
        claims_bene["ClmDiagnosisCode_1"]
        .value_counts()
        .drop("NONE", errors="ignore")
        .head(top_n)
        .index.tolist()
    )

    top100_proc = (
        claims_bene["ClmProcedureCode_1"]
        .value_counts()
        .drop("NONE", errors="ignore")
        .head(top_n)
        .index.tolist()
    )

    return top100_diag, top100_proc


def create_code_indicators(claims_bene, top100_diag, top100_proc):
    for code in top100_diag:
        claims_bene[f"Diag_{code}"] = (claims_bene["ClmDiagnosisCode_1"] == code).astype(int)

    for code in top100_proc:
        claims_bene[f"Proc_{code}"] = (claims_bene["ClmProcedureCode_1"] == code).astype(int)

    return claims_bene


def aggregate_provider_features(claims_bene, top100_diag, top100_proc):
    diag_cols_feat = [f"Diag_{c}" for c in top100_diag]
    proc_cols_feat = [f"Proc_{c}" for c in top100_proc]

    agg_dict = {
        "ClaimID": "count",
        "InscClaimAmtReimbursed": ["sum", "mean", "max"],
        "DeductibleAmtPaid": ["sum", "mean"],
        "ReimbRatio": "mean",
        "ClaimDuration": ["mean", "max"],
        "DaysInHospital": ["mean", "sum"],
        "Age": "mean",
        "ChronicCondCount": "mean",
        "SameAttendOper": "sum",
        "IsDead": "sum",
        "ClaimType": lambda x: (x == "Inpatient").sum(),
    }

    provider_df = claims_bene.groupby("Provider").agg(agg_dict)
    provider_df.columns = [
        "_".join(filter(None, col)).strip("_")
        if isinstance(col, tuple) else col
        for col in provider_df.columns
    ]
    provider_df = provider_df.reset_index()

    provider_df = provider_df.rename(columns={
        "ClaimID_count": "TotalClaims",
        "InscClaimAmtReimbursed_sum": "TotalReimbursed",
        "InscClaimAmtReimbursed_mean": "AvgReimbursed",
        "InscClaimAmtReimbursed_max": "MaxReimbursed",
        "DeductibleAmtPaid_sum": "TotalDeductible",
        "DeductibleAmtPaid_mean": "AvgDeductible",
        "ReimbRatio_mean": "AvgReimbRatio",
        "ClaimDuration_mean": "AvgClaimDuration",
        "ClaimDuration_max": "MaxClaimDuration",
        "DaysInHospital_mean": "AvgDaysInHospital",
        "DaysInHospital_sum": "TotalDaysInHospital",
        "Age_mean": "AvgPatientAge",
        "ChronicCondCount_mean": "AvgChronicConds",
        "SameAttendOper_sum": "SameAttendOperCount",
        "IsDead_sum": "DeceasedPatientCount",
        "ClaimType_<lambda>": "InpatientClaimCount",
    })

    uniq = claims_bene.groupby("Provider").agg(
        UniquePatients=("BeneID", "nunique"),
        UniqueAttendPhys=("AttendingPhysician", "nunique"),
        UniqueOperPhys=("OperatingPhysician", "nunique"),
        UniqueDiagnoses=("ClmDiagnosisCode_1", "nunique"),
        UniqueProcedures=("ClmProcedureCode_1", "nunique"),
    ).reset_index()

    provider_df = provider_df.merge(uniq, on="Provider", how="left")

    provider_df["OutpatientClaimCount"] = (
        provider_df["TotalClaims"] - provider_df["InpatientClaimCount"]
    )
    provider_df["InpatientRatio"] = (
        provider_df["InpatientClaimCount"] / provider_df["TotalClaims"]
    )
    provider_df["PatientsPerClaim"] = (
        provider_df["UniquePatients"] / provider_df["TotalClaims"]
    )
    provider_df["PhysiciansPerClaim"] = (
        provider_df["UniqueAttendPhys"] / provider_df["TotalClaims"]
    )
    provider_df["SameAttendOperRate"] = (
        provider_df["SameAttendOperCount"] / provider_df["TotalClaims"]
    )
    provider_df["DeceasedPatientRate"] = (
        provider_df["DeceasedPatientCount"] / provider_df["UniquePatients"]
    )

    code_agg = claims_bene.groupby("Provider")[diag_cols_feat + proc_cols_feat].max()
    provider_df = provider_df.merge(code_agg.reset_index(), on="Provider", how="left")

    return provider_df


def add_labels(provider_df, labels_df):
    labels_df["FraudLabel"] = (labels_df["PotentialFraud"] == "Yes").astype(int)
    final_df = labels_df.merge(provider_df, on="Provider", how="left")
    return final_df


def create_claim_features(claims_bene):
    claims_bene["ReimbRatio"] = (
        claims_bene["InscClaimAmtReimbursed"] /
        (claims_bene["DeductibleAmtPaid"] + 1)
    )
    return claims_bene


def prepare_training_data(final_df, feature_columns, label_column="FraudLabel"):
    X = final_df[feature_columns]
    y = final_df[label_column]
    return X, y


def save_provider_master(provider_df, filepath):
    provider_df.to_csv(filepath, index=False)
