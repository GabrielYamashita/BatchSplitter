from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from core.batching.planner import build_batch_plan
from core.batching.summarizer import summarize_batch_plan
from core.export.zip_exporter import export_batches_to_zip
from core.io.csv_reader import read_csv_auto
from core.mapping.manual import apply_manual_mapping
from core.mapping.mapper import auto_map_columns
from core.output.builder import build_output_dataframe
from core.output.transforms import apply_output_transforms
from core.preprocessing.cleaner import clean_dataframe
from core.preview.dataframe_preview import build_dataframe_preview
from core.schemas.resolver import resolve_schema
from core.validation.validator import validate_mapping


def build_schema_preview(schema: dict[str, Any]) -> dict[str, Any]:
    fields = schema.get("fields", {})

    output_fields = []

    for field_key, field_config in fields.items():
        output_fields.append(
            {
                "field": field_key,
                "required": bool(field_config.get("required", False)),
                "output_name": field_config.get("output_name"),
                "aliases": field_config.get("aliases", []),
            }
        )

    return {
        "project_id": schema.get("_meta", {}).get("project_id"),
        "project_name": schema.get("_meta", {}).get("project_name"),
        "template_id": schema.get("_meta", {}).get("template_id"),
        "template_name": schema.get("_meta", {}).get("template_name"),
        "output": schema.get("output", {}),
        "batch": schema.get("batch", {}),
        "fields": output_fields,
    }


def prepare_template(
    project_schema_path: str | Path,
    template_schema_path: str | Path,
) -> dict[str, Any]:
    """
    Used after user selects project/template.

    Returns resolved schema and a preview for Streamlit.
    """
    schema = resolve_schema(
        project_schema_path=project_schema_path,
        template_schema_path=template_schema_path,
    )

    return {
        "schema": schema,
        "schema_preview": build_schema_preview(schema),
    }


def prepare_uploaded_file(
    uploaded_file,
    schema: dict[str, Any],
    preview_rows: int = 10,
) -> dict[str, Any]:
    """
    Reads, cleans, previews, auto-maps and validates the uploaded CSV.

    Does not build final output.
    Does not generate batches.
    Does not generate ZIP.
    """
    read_result = read_csv_auto(uploaded_file, schema)
    df_raw = read_result["df"]

    clean_result = clean_dataframe(df_raw, schema)
    df_clean = clean_result["df"]

    input_preview = build_dataframe_preview(df_clean, max_rows=preview_rows)

    mapping = auto_map_columns(df_clean, schema)
    validation = validate_mapping(mapping, schema)

    return {
        "df_raw": df_raw,
        "df_clean": df_clean,
        "read_info": {
            "encoding": read_result["encoding"],
            "delimiter": read_result["delimiter"],
            "rows": read_result["rows"],
            "columns": read_result["columns"],
        },
        "cleaning_report": clean_result["report"],
        "input_preview": input_preview,
        "mapping": mapping,
        "validation": validation,
    }


def apply_mapping_and_build_output(
    df_clean: pd.DataFrame,
    schema: dict[str, Any],
    mapping: dict[str, Any],
    manual_mapping: dict[str, str] | None = None,
    preview_rows: int = 10,
) -> dict[str, Any]:
    """
    Applies optional manual mapping, validates, and builds final output DataFrame.

    If validation fails, returns errors and does not build df_output.
    """
    manual_mapping = manual_mapping or {}

    final_mapping = apply_manual_mapping(
        mapping=mapping,
        manual_mapping=manual_mapping,
        df=df_clean,
        schema=schema,
    )

    validation = validate_mapping(final_mapping, schema)

    if not validation["valid"]:
        return {
            "success": False,
            "mapping": final_mapping,
            "validation": validation,
            "df_output": None,
            "output_result": None,
            "output_preview": None,
        }

    output_result = build_output_dataframe(
        df=df_clean,
        mapping=final_mapping,
        schema=schema,
    )

    df_output = output_result["df"]

    df_output = apply_output_transforms(
        df=df_output,
        schema=schema,
    )

    output_preview = build_dataframe_preview(
        df_output,
        max_rows=preview_rows,
    )

    return {
        "success": True,
        "mapping": final_mapping,
        "validation": validation,
        "df_output": df_output,
        "output_result": output_result,
        "output_preview": output_preview,
    }


def prepare_batches(
    df_output: pd.DataFrame,
    schema: dict[str, Any],
    runtime_config: dict[str, Any],
) -> dict[str, Any]:
    """
    Builds batch plan and human-readable summary.

    Does not generate ZIP.
    """
    batch_plan = build_batch_plan(
        df=df_output,
        schema=schema,
        runtime_config=runtime_config,
    )

    batch_summary = summarize_batch_plan(batch_plan)

    return {
        "batch_plan": batch_plan,
        "batch_summary": batch_summary,
    }


def generate_zip(
    df_output: pd.DataFrame,
    batch_plan: list[dict[str, int]],
    schema: dict[str, Any],
    runtime_config: dict[str, Any],
) -> dict[str, Any]:
    """
    Final generation step.

    Streamlit should call this only after user confirms preview.
    """
    return export_batches_to_zip(
        df_output=df_output,
        batch_plan=batch_plan,
        schema=schema,
        runtime_config=runtime_config,
    )
