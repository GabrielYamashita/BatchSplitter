from __future__ import annotations

import pandas as pd

from core.output.transforms import (
    apply_output_transforms,
    cpf_pad_left_preserve_format,
    title_case_name,
)


def test_title_case_name_transform() -> None:
    assert title_case_name("JOAO DA SILVA") == "Joao da Silva"
    assert title_case_name("MARIA DOS SANTOS") == "Maria dos Santos"
    assert title_case_name("ANA E CARLOS") == "Ana e Carlos"
    assert title_case_name("  PEDRO   DA   COSTA  ") == "Pedro da Costa"
    assert title_case_name("") == ""


def test_cpf_pad_left_preserve_format_transform() -> None:
    assert cpf_pad_left_preserve_format("123456-00") == "000123456-00"
    assert cpf_pad_left_preserve_format("12345678901") == "12345678901"
    assert cpf_pad_left_preserve_format(123456789) == "00123456789"
    assert cpf_pad_left_preserve_format("") == ""


def test_apply_output_transforms_from_schema() -> None:
    df = pd.DataFrame(
        {
            "nome": [
                "JOAO DA SILVA",
                "MARIA DOS SANTOS",
                "ANA E CARLOS",
            ],
            "CPF": [
                "123456-00",
                "12345678901",
                123456789,
            ],
            "TEL_DEEP": [
                "5511999999999",
                "5511888888888",
                "5511777777777",
            ],
            "IdCaso": [
                "A1",
                "A2",
                "A3",
            ],
        }
    )

    schema = {
        "fields": {
            "nome": {
                "required": True,
                "output_name": "nome",
                "transforms": ["title_case_name"],
            },
            "cpf": {
                "required": False,
                "output_name": "CPF",
                "transforms": ["cpf_pad_left_preserve_format"],
            },
            "telefone": {
                "required": True,
                "output_name": "TEL_DEEP",
            },
        }
    }

    result = apply_output_transforms(df=df, schema=schema)

    assert list(result.columns) == ["nome", "CPF", "TEL_DEEP", "IdCaso"]

    assert result["nome"].tolist() == [
        "Joao da Silva",
        "Maria dos Santos",
        "Ana e Carlos",
    ]

    assert result["CPF"].tolist() == [
        "000123456-00",
        "12345678901",
        "00123456789",
    ]

    # Columns without transforms must remain unchanged.
    assert result["TEL_DEEP"].tolist() == [
        "5511999999999",
        "5511888888888",
        "5511777777777",
    ]

    assert result["IdCaso"].tolist() == [
        "A1",
        "A2",
        "A3",
    ]


def test_unknown_transform_raises_error() -> None:
    df = pd.DataFrame({"nome": ["JOAO DA SILVA"]})

    schema = {
        "fields": {
            "nome": {
                "required": True,
                "output_name": "nome",
                "transforms": ["transform_that_does_not_exist"],
            }
        }
    }

    try:
        apply_output_transforms(df=df, schema=schema)
    except ValueError as error:
        assert "Transform not found" in str(error)
    else:
        raise AssertionError("Expected ValueError for unknown transform.")


def run() -> None:
    test_title_case_name_transform()
    test_cpf_pad_left_preserve_format_transform()
    test_apply_output_transforms_from_schema()
    test_unknown_transform_raises_error()


if __name__ == "__main__":
    run()
    print("test_31_output_transforms passed")
