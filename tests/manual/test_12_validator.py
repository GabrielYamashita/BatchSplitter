from pprint import pprint

import pandas as pd

from core.mapping.mapper import auto_map_columns
from core.schemas.resolver import resolve_schema
from core.validation.validator import validate_mapping


def main():
    schema = resolve_schema(
        "schemas/afinz/project.yaml",
        "schemas/afinz/templates/cp_preventivo_03.yaml",
    )

    df_valid = pd.DataFrame(
        {
            "nome": ["Gabriel", "Yama"],
            "telefone": ["011999999999", "011988888888"],
        }
    )

    mapping_valid = auto_map_columns(df_valid, schema)
    validation_valid = validate_mapping(mapping_valid, schema)

    assert validation_valid["valid"] is True
    assert validation_valid["errors"] == []

    df_invalid = pd.DataFrame(
        {
            "nome": ["Gabriel", "Yama"],
        }
    )

    mapping_invalid = auto_map_columns(df_invalid, schema)
    validation_invalid = validate_mapping(mapping_invalid, schema)

    assert validation_invalid["valid"] is False
    assert any(
        error["type"] == "missing_required_field" and error["field"] == "telefone"
        for error in validation_invalid["errors"]
    )

    print("Validator OK\n")

    print("Valid mapping:")
    pprint(validation_valid)

    print("\nInvalid mapping:")
    pprint(validation_invalid)


if __name__ == "__main__":
    main()
