from pprint import pprint

import pandas as pd

from core.mapping.mapper import auto_map_columns
from core.output.builder import build_output_dataframe
from core.schemas.resolver import resolve_schema
from core.validation.validator import validate_mapping


def main():
    schema = resolve_schema(
        "schemas/afinz/project.yaml",
        "schemas/afinz/templates/extra_data.yaml",
    )

    df = pd.DataFrame(
        {
            "dias_atraso": ["10", "20"],
            "telefone": ["011999999999", "011988888888"],
            "valor_parcela": ["150.00", "200.00"],
            "nome": ["Gabriel", "Yama"],
            "data_vencimento": ["0107", "0207"],
            "observacao": ["A", "B"],
        }
    )

    mapping = auto_map_columns(df, schema)
    validation = validate_mapping(mapping, schema)

    assert validation["valid"] is True

    result = build_output_dataframe(df, mapping, schema)

    df_output = result["df"]
    report = result["report"]

    assert list(df_output.columns) == [
        "dias_atraso",
        "TEL_DEEP",
        "valor_parcela",
        "nome",
        "data_vencimento",
        "observacao",
    ]

    assert report["kept_unmapped_columns"] == ["observacao"]

    assert df_output.loc[0, "TEL_DEEP"] == "011999999999"
    assert df_output.loc[0, "valor_parcela"] == "150.00"
    assert df_output.loc[0, "nome"] == "Gabriel"
    assert df_output.loc[0, "observacao"] == "A"

    print("Output Builder Extra Data OK\n")

    print("Mapping:")
    pprint(mapping)

    print("\nReport:")
    pprint(report)

    print("\nOutput:")
    print(df_output)


if __name__ == "__main__":
    main()
