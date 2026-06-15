from __future__ import annotations

from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


LABEL_CANDIDATES = {"label", "labels", "class", "target"}


def _as_paths(paths_or_dir: str | Path | Iterable[str | Path]) -> list[Path]:
    if isinstance(paths_or_dir, (str, Path)):
        path = Path(paths_or_dir)
        if path.is_dir():
            return sorted(p for p in path.rglob("*.csv") if p.is_file())
        return [path]

    paths: list[Path] = []
    for item in paths_or_dir:
        path = Path(item)
        if path.is_dir():
            paths.extend(sorted(p for p in path.rglob("*.csv") if p.is_file()))
        else:
            paths.append(path)
    return sorted(paths)


def load_cicids_csvs(paths_or_dir: str | Path | Iterable[str | Path]) -> pd.DataFrame:
    """Load one CICIDS-style CSV file or every CSV under a directory."""
    csv_paths = _as_paths(paths_or_dir)
    if not csv_paths:
        raise FileNotFoundError(f"No CSV files found for: {paths_or_dir}")

    missing = [str(path) for path in csv_paths if not path.exists()]
    if missing:
        raise FileNotFoundError(f"CSV path(s) do not exist: {missing}")

    frames = []
    for path in csv_paths:
        frame = pd.read_csv(path, low_memory=False)
        frame["source_file"] = path.name
        frames.append(frame)

    return pd.concat(frames, ignore_index=True)


def find_label_column(columns: Iterable[str]) -> str:
    normalized = {str(column).strip().lower(): column for column in columns}
    if "label" in normalized:
        return normalized["label"]

    for normalized_name, original_name in normalized.items():
        if normalized_name in LABEL_CANDIDATES or "label" in normalized_name:
            return original_name

    raise ValueError("Could not find a label column. Expected Label, label, or similar.")


def clean_cicids_dataframe(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series, pd.DataFrame]:
    """Clean CICIDS2017 CSV data and return numeric features, binary labels, and summary."""
    if df.empty:
        raise ValueError("Input dataframe is empty.")

    cleaned = df.copy()
    cleaned.columns = [str(column).strip() for column in cleaned.columns]

    label_column = find_label_column(cleaned.columns)
    labels = cleaned[label_column].astype("string").str.strip()
    cleaned = cleaned.loc[labels.notna() & (labels != "")].copy()
    labels = labels.loc[cleaned.index]

    y = labels.str.upper().ne("BENIGN").astype(int)
    cleaned["binary_label"] = y

    feature_frame = cleaned.drop(columns=[label_column, "binary_label"], errors="ignore")
    numeric_features = feature_frame.apply(pd.to_numeric, errors="coerce")
    numeric_features = numeric_features.replace([np.inf, -np.inf], np.nan)

    all_missing_columns = numeric_features.columns[numeric_features.isna().all()].tolist()
    numeric_features = numeric_features.drop(columns=all_missing_columns)
    if numeric_features.empty:
        raise ValueError("No numeric feature columns remain after cleaning.")

    missing_before = int(numeric_features.isna().sum().sum())
    medians = numeric_features.median(numeric_only=True)
    numeric_features = numeric_features.fillna(medians).fillna(0)

    summary = pd.DataFrame(
        [
            {"metric": "rows_input", "value": len(df)},
            {"metric": "rows_after_missing_label_drop", "value": len(cleaned)},
            {"metric": "columns_input", "value": df.shape[1]},
            {"metric": "numeric_features_used", "value": numeric_features.shape[1]},
            {"metric": "dropped_all_missing_numeric_columns", "value": len(all_missing_columns)},
            {"metric": "missing_numeric_values_imputed", "value": missing_before},
            {"metric": "benign_rows", "value": int((y == 0).sum())},
            {"metric": "malicious_rows", "value": int((y == 1).sum())},
            {"metric": "label_column", "value": str(label_column).strip()},
        ]
    )

    return numeric_features, y.reset_index(drop=True), summary
