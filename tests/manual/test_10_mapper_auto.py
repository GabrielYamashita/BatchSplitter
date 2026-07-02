from pprint import pprint

import pandas as pd

from core.mapping.mapper import auto_map_columns
from core.schemas.resolver import resolve_schema


def main():
    schema = resolve_schema(
        "schemas/afinz/project.yaml",
        "schemas/afinz/templates/cp_preventivo_03.yaml",
    )

    df = pd.DataFrame(
        {
            "Nome Cliente": ["Gabriel", "Yama"],
            "Celular": ["011999999999", "011988888888"],
            "Observação": ["A", "B"],
        }
    )

    mapping = auto_map_columns(df, schema)

    assert mapping["mapped"]["nome"] == "Nome Cliente"
    assert mapping["mapped"]["telefone"] == "Celular"

    assert mapping["missing_required"] == []
    assert "Observação" in mapping["unmapped_columns"]
    assert mapping["conflicts"] == []

    print("Auto Mapper OK\n")
    pprint(mapping)


if __name__ == "__main__":
    main()
