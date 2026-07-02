from __future__ import annotations

from pprint import pprint

import pandas as pd

from core.preprocessing.cleaner import clean_dataframe
from core.schemas.resolver import resolve_schema


def main():
    schema = resolve_schema(
        "schemas/afinz/project.yaml",
        "schemas/afinz/templates/cp_preventivo_03.yaml",
    )

    df = pd.DataFrame(
        {
            " Unnamed: 0 ": ["1", "2", ""],
            " nome ": ["Gabriel", "Yama", ""],
            " telefone ": ["011999999999", "011988888888", ""],
            "empty_col": ["", "", ""],
        }
    )

    result = clean_dataframe(df, schema)

    cleaned = result["df"]
    report = result["report"]

    assert "Unnamed: 0" not in cleaned.columns
    assert "empty_col" not in cleaned.columns

    assert list(cleaned.columns) == ["nome", "telefone"]
    assert len(cleaned) == 2

    assert report["original_rows"] == 3
    assert report["final_rows"] == 2
    assert report["dropped_empty_rows"] == 1
    assert "Unnamed: 0" in report["dropped_unnamed_columns"]
    assert "empty_col" in report["dropped_empty_columns"]

    print("Cleaner OK\n")

    print("Report:")
    pprint(report)

    print("\nCleaned DataFrame:")
    print(cleaned)


if __name__ == "__main__":
    main()
