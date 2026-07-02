from __future__ import annotations

from typing import Any

from core.mapping.normalizer import normalize_name


def validate_mapping(
    mapping: dict[str, Any],
    schema: dict[str, Any],
) -> dict[str, Any]:
    errors: list[dict[str, Any]] = []

    fields = {
        field_key: field_config
        for field_key, field_config in schema.get("fields", {}).items()
        if field_config.get("enabled", True) is not False
    }

    mapped = mapping.get("mapped", {})

    for conflict in mapping.get("conflicts", []):
        errors.append(
            {
                "type": "mapping_conflict",
                "message": str(conflict.get("message") or conflict),
                "details": conflict,
            }
        )

    for field_key, field_config in fields.items():
        if field_config.get("required", False) and field_key not in mapped:
            errors.append(
                {
                    "type": "missing_required_field",
                    "field": field_key,
                    "message": f"Required field '{field_key}' was not mapped.",
                    "aliases": field_config.get("aliases", []),
                }
            )

    used_columns = {}

    for field_key, column_name in mapped.items():
        if column_name in used_columns:
            errors.append(
                {
                    "type": "duplicate_source_column",
                    "message": (
                        f"CSV column '{column_name}' was mapped to both "
                        f"'{used_columns[column_name]}' and '{field_key}'."
                    ),
                    "column": column_name,
                    "fields": [used_columns[column_name], field_key],
                }
            )

        used_columns[column_name] = field_key

    output_names = {}

    for field_key, field_config in fields.items():
        output_name = field_config.get("output_name")

        if not output_name:
            errors.append(
                {
                    "type": "missing_output_name",
                    "field": field_key,
                    "message": f"Field '{field_key}' has no output_name.",
                }
            )
            continue

        normalized_output_name = normalize_name(output_name)

        if normalized_output_name in output_names:
            errors.append(
                {
                    "type": "duplicate_output_name",
                    "message": (
                        f"Fields '{output_names[normalized_output_name]}' and "
                        f"'{field_key}' use the same output_name '{output_name}'."
                    ),
                    "fields": [output_names[normalized_output_name], field_key],
                    "output_name": output_name,
                }
            )

        output_names[normalized_output_name] = field_key

    return {
        "valid": len(errors) == 0,
        "errors": errors,
    }
