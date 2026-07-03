from pprint import pprint

import pandas as pd

from core.mapping.mapper import auto_map_columns
from core.schemas.resolver import resolve_schema
from core.validation.validator import validate_mapping


def main():
    schema = resolve_schema(
        "schemas/afinz/project.yaml",
        "schemas/afinz/templates/informar_pendencia_maior_60.yaml",
    )

    valid_df = pd.DataFrame(
        {
            "Nome Cliente": ["Gabriel"],
            "Celular": ["011999999999"],
        }
    )

    valid_mapping = auto_map_columns(valid_df, schema)
    valid_result = validate_mapping(valid_mapping, schema)

    assert valid_result["valid"] is True
    assert valid_result["errors"] == []

    invalid_df = pd.DataFrame(
        {
            "Nome Cliente": ["Gabriel"],
        }
    )

    invalid_mapping = auto_map_columns(invalid_df, schema)
    invalid_result = validate_mapping(invalid_mapping, schema)

    assert invalid_result["valid"] is False
    assert any(
        error["type"] == "missing_required_field"
        and error["field"] == "telefone"
        for error in invalid_result["errors"]
    )

    print("Validator OK\n")
    print("Valid result:")
    pprint(valid_result)
    print("\nInvalid result:")
    pprint(invalid_result)


if __name__ == "__main__":
    main()
