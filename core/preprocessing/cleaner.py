from __future__ import annotations

from typing import Any

import pandas as pd


def is_blank_value(value) -> bool:
    return str(value).strip() == ""


def is_blank_row(row: pd.Series) -> bool:
    return all(is_blank_value(value) for value in row)


def is_blank_column(series: pd.Series) -> bool:
    return all(is_blank_value(value) for value in series)


def find_duplicate_columns(columns: list[str]) -> list[str]:
    seen = set()
    duplicates = []

    for column in columns:
        if column in seen and column not in duplicates:
            duplicates.append(column)

        seen.add(column)

    return duplicates


def clean_dataframe(df: pd.DataFrame, schema: dict[str, Any]) -> dict[str, Any]:
    cleaning = schema.get("cleaning", {})
    cleaned = df.copy()

    original_rows = len(cleaned)

    if cleaning.get("normalize_column_names", True):
        cleaned.columns = [str(column).strip() for column in cleaned.columns]

    duplicates = find_duplicate_columns(list(cleaned.columns))

    if duplicates:
        raise ValueError(f"Duplicated columns after cleaning: {duplicates}")

    dropped_unnamed_columns = []

    if cleaning.get("drop_unnamed_columns", True):
        dropped_unnamed_columns = [
            column
            for column in cleaned.columns
            if str(column).lower().startswith("unnamed")
        ]

        if dropped_unnamed_columns:
            cleaned = cleaned.drop(columns=dropped_unnamed_columns)

    dropped_empty_columns = []

    if cleaning.get("drop_empty_columns", True):
        dropped_empty_columns = [
            column for column in cleaned.columns if is_blank_column(cleaned[column])
        ]

        if dropped_empty_columns:
            cleaned = cleaned.drop(columns=dropped_empty_columns)

    dropped_empty_rows = 0

    if cleaning.get("drop_empty_rows", True):
        blank_rows_mask = cleaned.apply(is_blank_row, axis=1)
        dropped_empty_rows = int(blank_rows_mask.sum())
        cleaned = cleaned.loc[~blank_rows_mask]

    cleaned = cleaned.reset_index(drop=True)

    return {
        "df": cleaned,
        "report": {
            "original_rows": original_rows,
            "final_rows": len(cleaned),
            "dropped_empty_rows": dropped_empty_rows,
            "dropped_empty_columns": dropped_empty_columns,
            "dropped_unnamed_columns": dropped_unnamed_columns,
        },
    }
