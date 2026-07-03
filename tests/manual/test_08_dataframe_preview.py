from __future__ import annotations

from pprint import pprint

import pandas as pd

from core.preview.dataframe_preview import build_dataframe_preview


def main():
    df = pd.DataFrame(
        {
            "nome": ["Gabriel", "Yama", "Teste"],
            "telefone": ["011999999999", "011988888888", "011977777777"],
        }
    )

    preview = build_dataframe_preview(df, max_rows=2)

    assert preview["rows"] == 3
    assert preview["total_columns"] == 2
    assert preview["columns"] == ["nome", "telefone"]
    assert len(preview["sample"]) == 2

    print("DataFrame Preview OK\n")
    pprint(
        {
            "rows": preview["rows"],
            "total_columns": preview["total_columns"],
            "columns": preview["columns"],
        }
    )
    print("\nSample:")
    print(preview["sample"])


if __name__ == "__main__":
    main()
