from pprint import pprint

import pandas as pd

from core.mapping.mapper import auto_map_columns
from core.output.builder import build_output_dataframe
from core.schemas.resolver import resolve_schema
from core.validation.validator import validate_mapping


def main():
    schema = resolve_schema(
        "schemas/recovery/project.yaml",
        "schemas/recovery/templates/cobranca_varejo_11.yaml",
    )

    df = pd.DataFrame(
        {
            "NrCpfCnpj": ["01234567890"],
            "FirstName": ["Gabriel"],
            "IdCaso": ["ABC123"],
            "NrTelefoneCompleto": ["011999999999"],
            "DsCarteiraAjustada": ["Carteira A"],
            "DsSquad": ["Squad 1"],
        }
    )

    mapping = auto_map_columns(df, schema)
    validation = validate_mapping(mapping, schema)
    assert validation["valid"] is True

    result = build_output_dataframe(
        df=df,
        mapping=mapping,
        schema=schema,
    )

    df_output = result["df"]
    report = result["report"]

    assert list(df_output.columns) == [
        "CPF",
        "nome",
        "IdCaso",
        "TEL_DEEP",
        "DsCarteiraAjustada",
        "DsSquad",
    ]

    assert report["renamed_columns"] == {
        "NrCpfCnpj": "CPF",
        "FirstName": "nome",
        "NrTelefoneCompleto": "TEL_DEEP",
    }

    assert report["mapped_unchanged_columns"] == [
        "IdCaso",
        "DsCarteiraAjustada",
        "DsSquad",
    ]

    assert report["kept_unmapped_columns"] == []
    assert report["input_rows"] == 1
    assert report["output_rows"] == 1

    assert df_output.loc[0, "CPF"] == "01234567890"
    assert df_output.loc[0, "nome"] == "Gabriel"
    assert df_output.loc[0, "IdCaso"] == "ABC123"
    assert df_output.loc[0, "TEL_DEEP"] == "011999999999"
    assert df_output.loc[0, "DsCarteiraAjustada"] == "Carteira A"
    assert df_output.loc[0, "DsSquad"] == "Squad 1"

    print("Output Builder Same Name Mapping OK\n")
    print("Report:")
    pprint(report)
    print("\nOutput:")
    print(df_output)


if __name__ == "__main__":
    main()
