
"""
Reusable helper functions for {PROJECT_NAME}.
"""

import logging
import pandas as pd

logger = logging.getLogger("project.helpers")


    """
    EXAMPLES BELOW - Delete
    """

def normalize_supplier(df: pd.DataFrame, col: str = "Supplier") -> pd.DataFrame:
    """
    Normalize supplier names: strip, uppercase, collapse spaces.
    """
    
    logger.info("normalize_supplier loaded (or used?).")
    print("normalize_supplier module loaded.")

    df = df.copy()
    if col not in df.columns:
        logger.warning(f"Column '{col}' not found.")
        return df

    df[col] = (
        df[col]
        .astype(str)
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
        .str.upper()
    )
    return df

def validate_columns(df: pd.DataFrame, required: list[str]) -> list[str]:
    missing = [c for c in required if c not in df.columns]
    if missing:
        logger.error(f"Missing columns: {missing}")
    return missing
