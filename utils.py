import pandas as pd
import numpy as np

def clean_dataframe(df: pd.DataFrame):
    """
    Returns: cleaned_df, report_dict
    """
    report = {}

    report["rows_before"] = int(df.shape[0])
    report["cols_before"] = int(df.shape[1])
    report["missing_before"] = int(df.isna().sum().sum())
    report["duplicates_before"] = int(df.duplicated().sum())

    cleaned = df.copy()

    # Drop duplicates
    cleaned = cleaned.drop_duplicates()

    # Trim column names
    cleaned.columns = [c.strip() for c in cleaned.columns]

    # Trim text + convert common null strings
    obj_cols = cleaned.select_dtypes(include=["object"]).columns
    for col in obj_cols:
        cleaned[col] = cleaned[col].astype(str).str.strip()
        cleaned[col] = cleaned[col].replace(
            {"": pd.NA, "nan": pd.NA, "NaN": pd.NA, "NULL": pd.NA, "null": pd.NA, "None": pd.NA}
        )

    # Try parsing date-like columns
    for col in cleaned.columns:
        if "date" in col.lower():
            try_dt = pd.to_datetime(cleaned[col], errors="coerce")
            if try_dt.notna().mean() > 0.6:
                cleaned[col] = try_dt

    # Fill missing values
    num_cols = cleaned.select_dtypes(include=["number"]).columns
    for col in num_cols:
        if cleaned[col].isna().any():
            cleaned[col] = cleaned[col].fillna(cleaned[col].median())

    other_cols = [c for c in cleaned.columns if c not in num_cols]
    for col in other_cols:
        if cleaned[col].isna().any():
            mode_series = cleaned[col].mode(dropna=True)
            fill_val = mode_series.iloc[0] if len(mode_series) > 0 else "Unknown"
            cleaned[col] = cleaned[col].fillna(fill_val)

    report["rows_after"] = int(cleaned.shape[0])
    report["cols_after"] = int(cleaned.shape[1])
    report["missing_after"] = int(cleaned.isna().sum().sum())
    report["duplicates_after"] = int(cleaned.duplicated().sum())

    return cleaned, report


# ------------------ STEP 2 HELPERS ------------------

def detect_column_types(df: pd.DataFrame):
    """Returns (numeric_cols, categorical_cols, date_cols)"""
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    date_cols = df.select_dtypes(include=["datetime64[ns]", "datetime64[ns, UTC]"]).columns.tolist()

    # detect date-like object columns
    for col in df.columns:
        if col in date_cols:
            continue
        if "date" in col.lower() and df[col].dtype == "object":
            parsed = pd.to_datetime(df[col], errors="coerce")
            if parsed.notna().mean() > 0.6:
                df[col] = parsed

    # recalc date cols after conversion
    date_cols = df.select_dtypes(include=["datetime64[ns]", "datetime64[ns, UTC]"]).columns.tolist()
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()

    categorical_cols = []
    for col in df.columns:
        if col in numeric_cols or col in date_cols:
            continue
        # treat object columns with reasonable cardinality as categorical
        if df[col].dtype == "object":
            nunique = df[col].nunique(dropna=True)
            if nunique <= max(25, int(0.05 * len(df))):
                categorical_cols.append(col)

    return numeric_cols, categorical_cols, date_cols


def basic_summary(df: pd.DataFrame):
    num_cols, cat_cols, date_cols = detect_column_types(df)

    return {
        "rows": int(df.shape[0]),
        "cols": int(df.shape[1]),
        "missing_cells": int(df.isna().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
        "num_cols": num_cols,
        "cat_cols": cat_cols,
        "date_cols": date_cols,
    }


def find_metric_column(df: pd.DataFrame, preferred=("sales", "revenue", "profit", "amount")):
    """Pick a main numeric metric column automatically."""
    lower_map = {c.lower(): c for c in df.columns}

    for key in preferred:
        for col_lower, original in lower_map.items():
            if key in col_lower and pd.api.types.is_numeric_dtype(df[original]):
                return original

    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    if not numeric_cols:
        return None

    variances = df[numeric_cols].var(numeric_only=True).sort_values(ascending=False)
    return variances.index[0] if len(variances) else numeric_cols[0]

def top_categories(df: pd.DataFrame, cat_col: str, n=10):
    vc = df[cat_col].value_counts(dropna=True).head(n)
    out = vc.reset_index()
    out.columns = [cat_col, "category_count"]  # avoids 'count' clashes
    return out

def time_series_aggregate(df: pd.DataFrame, date_col: str, metric_col: str, freq="M", agg="sum"):
    temp = df.copy()
    temp[date_col] = pd.to_datetime(temp[date_col], errors="coerce")
    temp = temp.dropna(subset=[date_col])

    if metric_col is None or metric_col not in temp.columns:
        return None

    temp = temp.set_index(date_col)

    if agg == "sum":
        out = temp[metric_col].resample(freq).sum().reset_index()
    else:
        out = temp[metric_col].resample(freq).mean().reset_index()

    return out
