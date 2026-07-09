from pathlib import Path
import pandas as pd

# =============================================================================
# PROJECT PATHS
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

OUTPUT_ROOT = PROJECT_ROOT / "data" / "output"

# =============================================================================
# DATA TYPE SETTINGS
# =============================================================================

CATEGORY_COLUMNS = [
    "Acoat",
    "GRACO",
    "Regulatory Document Type",
    "Authorization",
    "Legislation",
    "CLP_GHS",
    "Lang",
    "Region",
    "Archive",
    "Raw material Category",
    "Raw Material Class",
    "Processed in SAP",
    "Harmonized name"
    # Future mappings
]

STRING_COLUMNS = [
    "ID",
    "Name",
    "Remarks"
    # Future mappings
]

DATE_COLUMNS = [
    "Created",
    "IssueDate",
    "ValidationDate"
]

# =============================================================================
# FUNCTIONS
# =============================================================================

def clean_drag_drop_path(path: str) -> str:

    path = path.strip()

    # PowerShell drag/drop
    if path.startswith("& "):
        path = path[2:].strip()

    # Remove wrapping quotes
    path = path.strip("'").strip('"')

    return str(Path(path))

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:

    df.columns = df.columns.str.strip()

    # Strings
    for col in STRING_COLUMNS:
        if col in df.columns:
            df[col] = df[col].astype("string")

    # Dates
    for col in DATE_COLUMNS:

        if col in df.columns:

            original_not_null = df[col].notna().sum()

            df[col] = pd.to_datetime(
                df[col],
                errors="coerce"
            ).dt.normalize()

            failures = original_not_null - df[col].notna().sum()

            print(f"   {col}: {failures} invalid dates")

    # Categories
    for col in CATEGORY_COLUMNS:
        if col in df.columns:
            df[col] = df[col].astype("category")

    # Optional cleanup
    if "Created By" in df.columns:
        df = df.drop(columns=["Created By"])

    return df

def workbook_to_parquet(excel_file: str):

    excel_path = Path(excel_file)
    if not excel_path.exists():
        raise FileNotFoundError(
            f"File not found:\n{excel_path}"
        )

    # Output folder
    workbook_output = OUTPUT_ROOT / excel_path.stem

    workbook_output.mkdir(
        parents=True,
        exist_ok=True
    )

    print("\n" + "=" * 80)
    print(f"Workbook : {excel_path.name}")
    print(f"Output   : {workbook_output}")
    print("=" * 80)

    workbook = pd.ExcelFile(excel_path)

    conversion_log = []

    for sheet_name in workbook.sheet_names:

        print(f"\nProcessing sheet: {sheet_name}")

        try:

            df = pd.read_excel(
                excel_path,
                sheet_name=sheet_name,
                dtype={
                    "ID": str,
                    "Acoat": str,
                    "GRACO": str,
                    "Name": str,
                    "Remarks": str
                }
            )

            df = clean_dataframe(df)

            parquet_file = (
                workbook_output /
                f"{sheet_name}.parquet"
            )

            df.to_parquet(
                parquet_file,
                engine="pyarrow",
                compression="zstd",
                index=False
            )

            conversion_log.append({
                "Sheet": sheet_name,
                "Rows": len(df),
                "Columns": len(df.columns),
                "Parquet File": parquet_file.name
            })

            print(
                f"   ✅ Saved {len(df):,} rows "
                f"→ {parquet_file.name}"
            )

        except Exception as e:

            print(f"   ❌ ERROR: {e}")

            conversion_log.append({
                "Sheet": sheet_name,
                "Rows": None,
                "Columns": None,
                "Parquet File": "FAILED",
                "Error": str(e)
            })

    # Save conversion log
    log_df = pd.DataFrame(conversion_log)

    log_path = workbook_output / "_conversion_log.csv"

    log_df.to_csv(
        log_path,
        index=False
    )

    print("\n" + "=" * 80)
    print("CONVERSION COMPLETE")
    print("=" * 80)

    print(f"\nFiles saved to:\n{workbook_output}")
    print(f"\nLog saved to:\n{log_path}")


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":

    excel_file = clean_drag_drop_path(
        input(
            "\nDrag an Excel file here and press ENTER:\n\n"
        )
    )

    print(f"\nReceived path:\n{excel_file}\n")

    workbook_to_parquet(excel_file)
