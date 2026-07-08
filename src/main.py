import pandas as pd

PARQUET_PATH = "data/documents.parquet"

EXCEL_PATH = r"C:\Users\TizzeiVL\OneDrive - AkzoNobel\GPCTools\Macros\0_4 Document Management Tool\Supporting Files\ZyLAB Report Full.xlsx"

CATEGORY_COLUMNS = [
    "Acoat",
    "GRACO",
    "Regulatory Document Type",
    "Authorization",
    "Supplier",
    "Legislation",
    "CLP_GHS",
    "Lang",
    "Region",
    "Archive",
    "Raw material Category",
    "Raw Material Class",
    "Processed in SAP"
]


STRING_COLUMNS = [
    "ID",
    "Name",
    "Remarks"
]



def load_excel():
    df = pd.read_excel(
        EXCEL_PATH,
        dtype={
            "ID": str,
            "Acoat": str,
            "GRACO": str,
            "Name": str,
            "Remarks": str
        }
    )

    df.columns = df.columns.str.strip()

    #STRINGS - Captured early (the "str" above in pandas is only to avoid corruption)
    for col in STRING_COLUMNS:
        if col in df.columns:
            df[col] = df[col].astype("string")


    print("\nStart schema:")
    print(df.dtypes)
    print()

    # Drop unnecessary column
    if "Created By" in df.columns:
        df = df.drop(columns=["Created By"])

    # Dates
    for col in ["Created", "IssueDate", "ValidationDate"]:
        if col in df.columns:

            original_not_null = df[col].notna().sum()

            df[col] = pd.to_datetime(
                df[col],
                format="%m/%d/%Y %I:%M %p",
                errors="coerce"
            ).dt.normalize()

            failures = original_not_null - df[col].notna().sum()

            print(f"{col}: {failures} invalid dates")

    # Categories
    for col in CATEGORY_COLUMNS:
        if col in df.columns:
            df[col] = df[col].astype("category")

    print("\nFinal schema:")
    print(df.dtypes)
    print()

    return df


def save_to_parquet(df):
    df.to_parquet(
        PARQUET_PATH,
        engine="pyarrow",
        compression="zstd",
        index=False
    )


if __name__ == "__main__":
    df = load_excel()
    save_to_parquet(df)

    test = pd.read_parquet(PARQUET_PATH)

    print(test.dtypes)
    print(test.shape)


    print(f"✅ Saved {len(df):,} rows to Parquet")
