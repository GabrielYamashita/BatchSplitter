from __future__ import annotations

from typing import Any

import pandas as pd


def apply_manual_mapping(
    mapping: dict[str, Any],
    manual_mapping: dict[str, str],
    df: pd.DataFrame,
    schema: dict[str, Any],
) -> dict[str, Any]:
    """
    Applies user corrections from the front.

    manual_mapping example:
    {
        "telefone": "Fone Principal"
    }

    Meaning:
    field telefone should use CSV column Fone Principal.
    """
    updated_mapping = {
        "mapped": dict(mapping.get("mapped", {})),
        "unmapped_columns": list(mapping.get("unmapped_columns", [])),
        "missing_required": list(mapping.get("missing_required", [])),
        "conflicts": list(mapping.get("conflicts", [])),
    }

    available_columns = set(df.columns)
    fields = schema.get("fields", {})

    for field_key, column_name in manual_mapping.items():
        if field_key not in fields:
            updated_mapping["conflicts"].append(
                {
                    "field": field_key,
                    "error": "unknown_field",
                    "message": f"Unknown field: {field_key}",
                }
            )
            continue

        if column_name not in available_columns:
            updated_mapping["conflicts"].append(
                {
                    "field": field_key,
                    "error": "unknown_column",
                    "message": f"Column not found in CSV: {column_name}",
                }
            )
            continue

        updated_mapping["mapped"][field_key] = column_name

        if column_name in updated_mapping["unmapped_columns"]:
            updated_mapping["unmapped_columns"].remove(column_name)

        if field_key in updated_mapping["missing_required"]:
            updated_mapping["missing_required"].remove(field_key)

    # Recalculate missing required after manual changes.
    required_fields = [
        field_key
        for field_key, field_config in fields.items()
        if field_config.get("enabled", True) is not False
        and field_config.get("required", False)
    ]

    updated_mapping["missing_required"] = [
        field_key
        for field_key in required_fields
        if field_key not in updated_mapping["mapped"]
    ]

    return updated_mapping
