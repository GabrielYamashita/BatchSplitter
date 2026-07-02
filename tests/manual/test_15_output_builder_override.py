from pprint import pprint

import pandas as pd

from core.mapping.mapper import auto_map_columns
from core.output.builder import build_output_dataframe
from core.schemas.resolver import resolve_schema
from core.validation.validator import validate_mapping


def main():
    schema = resolve_schema(
        "schemas/afinz/project.yaml",
        "schemas/afinz/templates/override.yaml",
    )

    df = pd.DataFrame(
        {
            "nome": ["Gabriel", "Yama"],
            "telefone": ["011999999999", "011988888888"],
        }
    )

    mapping = auto_map_columns(df, schema)
    validation = validate_mapping(mapping, schema)

    assert validation["valid"] is True

    result = build_output_dataframe(df, mapping, schema)

    df_output = result["df"]
    report = result["report"]

    assert list(df_output.columns) == ["TEL_DEEP"]

    assert "nome" in report["dropped_unmapped_columns"]

    assert df_output.loc[0, "TEL_DEEP"] == "011999999999"

    print("Output Builder Override OK\n")

    print("Resolved fields:")
    pprint(schema["fields"])

    print("\nMapping:")
    pprint(mapping)

    print("\nReport:")
    pprint(report)

    print("\nOutput:")
    print(df_output)


if __name__ == "__main__":
    main()
