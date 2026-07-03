from __future__ import annotations

from typing import Any

import pandas as pd


def get_active_fields(schema: dict[str, Any]) -> dict[str, dict[str, Any]]:
    fields = schema.get("fields", {})

    return {
        field_key: field_config
        for field_key, field_config in fields.items()
        if field_config.get("enabled", True) is not False
    }


def build_source_column_to_field(mapping: dict[str, Any]) -> dict[str, str]:
    """
    Converts:
    {
        "nome": "Nome Cliente",
        "telefone": "Celular"
    }

    Into:
    {
        "Nome Cliente": "nome",
        "Celular": "telefone"
    }
    """
    mapped = mapping.get("mapped", {})

    return {source_column: field_key for field_key, source_column in mapped.items()}


def build_output_dataframe(
    df: pd.DataFrame,
    mapping: dict[str, Any],
    schema: dict[str, Any],
) -> dict[str, Any]:
    """
    Builds the final output DataFrame.

    Rules:
    - Output column order follows the uploaded CSV order.
    - Mapped columns are renamed to field.output_name.
    - Mapped columns with the same input/output name are tracked separately.
    - Unmapped columns are kept with their original names.
    - Fields with enabled:false are not mapped, but raw CSV columns are still kept.
    """
    fields = get_active_fields(schema)
    source_column_to_field = build_source_column_to_field(mapping)

    output = pd.DataFrame()

    renamed_columns: dict[str, str] = {}
    mapped_unchanged_columns: list[str] = []
    kept_unmapped_columns: list[str] = []

    for source_column in df.columns:
        field_key = source_column_to_field.get(source_column)
        field_config = fields.get(field_key) if field_key else None

        if field_key and field_config:
            output_name = field_config.get("output_name")

            if not output_name:
                raise ValueError(f"Field '{field_key}' has no output_name.")

            if output_name in output.columns:
                raise ValueError(f"Duplicate output column generated: {output_name}")

            output[output_name] = df[source_column]

            if source_column == output_name:
                mapped_unchanged_columns.append(source_column)
            else:
                renamed_columns[source_column] = output_name

            continue

        if source_column in output.columns:
            raise ValueError(f"Duplicate output column generated: {source_column}")

        output[source_column] = df[source_column]
        kept_unmapped_columns.append(source_column)

    return {
        "df": output,
        "report": {
            "input_columns": list(df.columns),
            "output_columns": list(output.columns),
            "renamed_columns": renamed_columns,
            "mapped_unchanged_columns": mapped_unchanged_columns,
            "kept_unmapped_columns": kept_unmapped_columns,
            "input_rows": len(df),
            "output_rows": len(output),
        },
    }
