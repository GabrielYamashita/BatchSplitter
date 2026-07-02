from __future__ import annotations

from typing import Any

import pandas as pd


def build_dataframe_preview(
    df: pd.DataFrame,
    max_rows: int = 10,
) -> dict[str, Any]:
    """
    Returns dataframe preview data for Streamlit.

    Streamlit can display:
    - rows
    - columns
    - sample dataframe
    """
    return {
        "rows": len(df),
        "total_columns": len(df.columns),
        "columns": list(df.columns),
        "sample": df.head(max_rows).copy(),
    }
