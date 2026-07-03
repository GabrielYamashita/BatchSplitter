from pprint import pprint

import pandas as pd

from core.mapping.manual import apply_manual_mapping
from core.mapping.mapper import auto_map_columns
from core.schemas.resolver import resolve_schema


def main():
    schema = resolve_schema(
        "schemas/afinz/project.yaml",
        "schemas/afinz/templates/informar_pendencia_maior_60.yaml",
    )

    df = pd.DataFrame(
        {
            "Nome Cliente": ["Gabriel", "Yama"],
            "Fone Principal": ["011999999999", "011988888888"],
        }
    )

    mapping = auto_map_columns(df, schema)

    assert mapping["mapped"]["nome"] == "Nome Cliente"
    assert "telefone" in mapping["missing_required"]

    manual_mapping = {
        "telefone": "Fone Principal",
    }

    updated_mapping = apply_manual_mapping(
        mapping=mapping,
        manual_mapping=manual_mapping,
        df=df,
        schema=schema,
    )

    assert updated_mapping["mapped"]["telefone"] == "Fone Principal"
    assert updated_mapping["missing_required"] == []
    assert "Fone Principal" not in updated_mapping["unmapped_columns"]

    print("Manual Mapper OK\n")
    pprint(updated_mapping)


if __name__ == "__main__":
    main()
