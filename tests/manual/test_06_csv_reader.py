from __future__ import annotations

import io
from pprint import pprint

from core.io.csv_reader import read_csv_auto
from core.schemas.resolver import resolve_schema


class NamedBytesIO(io.BytesIO):
    def __init__(self, content: bytes, name: str):
        super().__init__(content)
        self.name = name


def main():
    schema = resolve_schema(
        "schemas/afinz/project.yaml",
        "schemas/afinz/templates/cp_preventivo_03.yaml",
    )

    csv_content = (
        "nome;telefone;cpf\n"
        "Gabriel;011999999999;01234567890\n"
        "Yama;011988888888;00123456789\n"
    ).encode("utf-8")

    uploaded_file = NamedBytesIO(csv_content, "clientes.csv")

    result = read_csv_auto(uploaded_file, schema)
    df = result["df"]

    assert result["delimiter"] == ";"
    assert result["encoding"] in ["utf-8", "utf-8-sig"]
    assert result["rows"] == 2

    assert list(df.columns) == ["nome", "telefone", "cpf"]

    assert df.loc[0, "cpf"] == "01234567890"
    assert df.loc[1, "cpf"] == "00123456789"

    assert df.loc[0, "telefone"] == "011999999999"

    print("CSV Reader OK\n")
    pprint(
        {
            "delimiter": result["delimiter"],
            "encoding": result["encoding"],
            "rows": result["rows"],
            "columns": result["columns"],
        }
    )

    print("\nDataFrame:")
    print(df)


if __name__ == "__main__":
    main()
