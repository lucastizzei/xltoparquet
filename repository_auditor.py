import pandas as pd
import numpy as np
from datetime import datetime

PARQUET_PATH = "data/documents.parquet"
OUTPUT_FILE = "Repository_Audit.xlsx"

VALID_DOC_TYPES = {
    "MSDS",
    "eSDS",
    "TDS",
    "TRAQ",
    "AddInfo",
    "CORIntermediate",
    "CORResin",
    "EcoLabel",
    "LegInfo",
    "Reach EC",
    "Reach UK",
    "RS",
    "FoodContact"
}

VALID_LANGUAGES = {
    "EN",
    "NL",
    "ZH",
    "DE",
    "ES",
    "IT",
    "ID",
    "KO",
    "PT",
    "SE",
    "FR",
    "PL",
    "MS",
    "JA",
    "TH",
    "VI"
}

VALID_LEGISLATIONS = {
    "US",
    "EC",
    "ZH",
    "JA",
    "UN",
    "AU",
    "BR",
    "KO",
    "GB",
    "CA",
    "ID",
    "MY",
    "NZ",
    "SG",
    "TW",
    "TH",
    "TR",
    "LOCAL"
}

VALID_CLP_GHS = {
    "CLP",
    "GHS",
    "LOCAL"
}

print("Loading parquet...")
df = pd.read_parquet(PARQUET_PATH)

print(f"Loaded {len(df):,} records")

# ======================================================
# NORMALIZATION
# ======================================================

for col in [
    "Acoat",
    "GRACO",
    "Regulatory Document Type",
    "Supplier",
    "Legislation",
    "CLP_GHS",
    "Lang"
]:
    if col in df.columns:
        df[col] = (
            df[col]
            .astype("string")
            .str.strip()
        )

# ======================================================
# VALIDATION FLAGS
# ======================================================

df["ERR_Acoat"] = False
df["ERR_DocType"] = False
df["ERR_Language"] = False
df["ERR_Legislation"] = False
df["ERR_CLP_GHS"] = False
df["ERR_GHS_EC_GB"] = False
df["ERR_MissingSupplier"] = False
df["ERR_MissingIssueDate"] = False
df["ERR_FutureIssueDate"] = False
df["ERR_ValidationBeforeIssue"] = False

# ======================================================
# ACOAT
# ======================================================

acoat = df["Acoat"].astype("string")

df["ERR_Acoat"] = (
    ~acoat.str.match(r"^[0-9A-Z]{5}$", na=False)
)

# ======================================================
# DOCUMENT TYPE
# ======================================================

df["ERR_DocType"] = (
    ~df["Regulatory Document Type"]
        .isin(VALID_DOC_TYPES)
)

# ======================================================
# LANGUAGE
# ======================================================

df["ERR_Language"] = (
    ~df["Lang"]
        .isin(VALID_LANGUAGES)
)

# ======================================================
# LEGISLATION
# ======================================================

leg = df["Legislation"].astype("string")

df["ERR_Legislation"] = (
    leg.notna()
    &
    ~leg.isin(VALID_LEGISLATIONS)
)

# ======================================================
# CLP GHS
# ======================================================

clp = df["CLP_GHS"].astype("string")

df["ERR_CLP_GHS"] = (
    clp.notna()
    &
    ~clp.isin(VALID_CLP_GHS)
)

# ======================================================
# REQUIRED FIELDS
# ======================================================

df["ERR_MissingSupplier"] = (
    df["Supplier"]
    .astype("string")
    .str.strip()
    .fillna("")
    .eq("")
)

df["ERR_MissingIssueDate"] = (
    df["IssueDate"].isna()
)

# ======================================================
# FUTURE DATES
# ======================================================

today = pd.Timestamp.today().normalize()

df["ERR_FutureIssueDate"] = (
    df["IssueDate"] > today
)

# ======================================================
# Validation < Issue Date
# ======================================================

mask = (
    df["IssueDate"].notna()
    &
    df["ValidationDate"].notna()
)

df.loc[
    mask,
    "ERR_ValidationBeforeIssue"
] = (
    df.loc[mask, "ValidationDate"]
    <
    df.loc[mask, "IssueDate"]
)

# ======================================================
# MSDS RULES
# ======================================================

msds = (
    df["Regulatory Document Type"]
    == "MSDS"
)

df.loc[
    msds,
    "ERR_CLP_GHS"
] = (
    df.loc[msds, "CLP_GHS"]
    .isna()
)

df.loc[
    msds,
    "ERR_Legislation"
] = (
    df.loc[msds, "Legislation"]
    .isna()
)

# ======================================================
# GHS + EC/GB
# ======================================================

df["ERR_GHS_EC_GB"] = (
    (df["CLP_GHS"] == "GHS")
    &
    (
        df["Legislation"]
        .isin(["EC", "GB"])
    )
)

# ======================================================
# eSDS RULE
# ======================================================

df["ERR_eSDS_Legislation"] = (
    (df["Regulatory Document Type"] == "eSDS")
    &
    (
        ~df["Legislation"]
            .isin(["EC", "GB"])
    )
)

# ======================================================
# Reach EC
# ======================================================

df["ERR_ReachEC"] = (
    (df["Regulatory Document Type"] == "Reach EC")
    &
    (
        (
            df["CLP_GHS"] != "CLP"
        )
        |
        (
            df["Legislation"] != "EC"
        )
    )
)

# ======================================================
# Reach UK
# ======================================================

df["ERR_ReachUK"] = (
    (df["Regulatory Document Type"] == "Reach UK")
    &
    (
        (
            df["CLP_GHS"] != "CLP"
        )
        |
        (
            df["Legislation"] != "GB"
        )
    )
)

# ======================================================
# OVERALL SCORE
# ======================================================

error_cols = [
    c
    for c in df.columns
    if c.startswith("ERR_")
]

df["Errors"] = (
    df[error_cols]
    .sum(axis=1)
)

df["Status"] = np.where(
    df["Errors"] == 0,
    "VALID",
    "ERROR"
)

# ======================================================
# SUMMARY
# ======================================================

total_docs = len(df)

valid_docs = (
    df["Status"]
    .eq("VALID")
    .sum()
)

error_docs = total_docs - valid_docs

score = (
    valid_docs
    / total_docs
    * 100
)

print()
print("=" * 60)
print("REPOSITORY HEALTH")
print("=" * 60)

print(f"Documents : {total_docs:,}")
print(f"Valid     : {valid_docs:,}")
print(f"Errors    : {error_docs:,}")
print(f"Score     : {score:.2f}%")

print()
print("Top Errors")

summary = (
    df[error_cols]
    .sum()
    .sort_values(ascending=False)
)

print(summary)

# ======================================================
# EXPORT
# ======================================================

audit = df[df["Errors"] > 0]

audit.to_excel(
    OUTPUT_FILE,
    index=False
)

print()
print(f"Audit exported: {OUTPUT_FILE}")
print(f"Rows exported: {len(audit):,}")
