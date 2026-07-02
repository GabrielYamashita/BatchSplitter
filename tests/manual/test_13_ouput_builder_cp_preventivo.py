from pprint import pprint

import pandas as pd

from core.mapping.mapper import auto_map_columns
from core.output.builder import build_output_dataframe
from core.preview.dataframe_preview import build_dataframe_preview
from core.schemas.resolver import resolve_schema
from core.validation.validator import validate_mapping


def main():
    schema = resolve_schema(
        "schemas/afinz/project.yaml",
        "schemas/afinz/templates/cp_preventivo_03.yaml",
    )

    df = pd.DataFrame(
        {
            "Celular": ["011999999999", "011988888888"],
            "Nome Cliente": ["Gabriel", "Yama"],
            "CPF": ["01234567890", "00123456789"],
        }
    )

    mapping = auto_map_columns(df, schema)
    validation = validate_mapping(mapping, schema)

    assert validation["valid"] is True

    result = build_output_dataframe(df, mapping, schema)

    df_output = result["df"]
    report = result["report"]

    assert list(df_output.columns) == ["TEL_DEEP", "nome", "CPF"]
    assert len(df_output) == 2

    assert df_output.loc[0, "TEL_DEEP"] == "011999999999"
    assert df_output.loc[0, "nome"] == "Gabriel"
    assert df_output.loc[0, "CPF"] == "01234567890"

    assert report["renamed_columns"] == {
        "Celular": "TEL_DEEP",
        "Nome Cliente": "nome",
    }

    assert report["kept_unmapped_columns"] == ["CPF"]

    preview = build_dataframe_preview(df_output, max_rows=1)

    assert preview["rows"] == 2
    assert preview["columns"] == ["TEL_DEEP", "nome", "CPF"]
    assert len(preview["sample"]) == 1

    print("Output Builder CP Preventivo OK\n")

    print("Mapping:")
    pprint(mapping)

    print("\nReport:")
    pprint(report)

    print("\nOutput:")
    print(df_output)

    print("\nPreview:")
    pprint(
        {
            "rows": preview["rows"],
            "columns": preview["columns"],
        }
    )


if __name__ == "__main__":
    main()
