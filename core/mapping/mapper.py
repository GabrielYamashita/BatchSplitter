from __future__ import annotations

from typing import Any

import pandas as pd

from core.mapping.normalizer import normalize_name


def get_active_fields(schema: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """
    Resolver should already remove enabled:false fields.
    This function keeps the mapper safe if an unresolved schema is passed.
    """
    fields = schema.get("fields", {})

    return {
        field_key: field_config
        for field_key, field_config in fields.items()
        if field_config.get("enabled", True) is not False
    }


def build_alias_index(schema: dict[str, Any]) -> dict[str, str]:
    """
    Returns:
    {
        normalized_alias: field_key
    }
    """
    alias_index: dict[str, str] = {}
    fields = get_active_fields(schema)

    for field_key, field_config in fields.items():
        aliases = list(field_config.get("aliases", []))

        # Useful implicit aliases.
        aliases.append(field_key)

        output_name = field_config.get("output_name")
        if output_name:
            aliases.append(output_name)

        for alias in aliases:
            normalized_alias = normalize_name(alias)

            if not normalized_alias:
                continue

            existing_field = alias_index.get(normalized_alias)

            if existing_field and existing_field != field_key:
                raise ValueError(
                    f"Alias conflict: '{alias}' maps to both "
                    f"'{existing_field}' and '{field_key}'."
                )

            alias_index[normalized_alias] = field_key

    return alias_index


def auto_map_columns(
    df: pd.DataFrame,
    schema: dict[str, Any],
) -> dict[str, Any]:
    """
    Maps CSV columns to schema fields.

    Direction:
    mapped[field_key] = original_csv_column
    """
    alias_index = build_alias_index(schema)

    mapped: dict[str, str] = {}
    unmapped_columns: list[str] = []
    conflicts: list[dict[str, Any]] = []

    for column in df.columns:
        normalized_column = normalize_name(column)
        field_key = alias_index.get(normalized_column)

        if not field_key:
            unmapped_columns.append(column)
            continue

        if field_key in mapped:
            conflicts.append(
                {
                    "field": field_key,
                    "first_column": mapped[field_key],
                    "second_column": column,
                }
            )
            continue

        mapped[field_key] = column

    fields = get_active_fields(schema)

    required_fields = [
        field_key
        for field_key, field_config in fields.items()
        if field_config.get("required", False)
    ]

    missing_required = [
        field_key for field_key in required_fields if field_key not in mapped
    ]

    return {
        "mapped": mapped,
        "unmapped_columns": unmapped_columns,
        "missing_required": missing_required,
        "conflicts": conflicts,
    }
