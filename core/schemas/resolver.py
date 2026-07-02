from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

from core.schemas.loader import load_yaml


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(base)

    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)

    return result


def remove_disabled_fields(schema: dict[str, Any]) -> dict[str, Any]:
    schema = copy.deepcopy(schema)
    fields = schema.get("fields", {})

    if not isinstance(fields, dict):
        raise ValueError("'fields' must be a dictionary.")

    disabled_fields = [
        field_key
        for field_key, field_config in fields.items()
        if isinstance(field_config, dict) and field_config.get("enabled", True) is False
    ]

    for field_key in disabled_fields:
        fields.pop(field_key, None)

    schema["fields"] = fields
    return schema


def resolve_schema(
    project_schema_path: str | Path,
    template_schema_path: str | Path,
) -> dict[str, Any]:
    project_schema = load_yaml(project_schema_path)
    template_schema = load_yaml(template_schema_path)

    resolved = deep_merge(project_schema, template_schema)
    resolved = remove_disabled_fields(resolved)

    resolved["_meta"] = {
        "project_schema_path": str(project_schema_path),
        "template_schema_path": str(template_schema_path),
        "project_id": project_schema.get("id"),
        "project_name": project_schema.get("name"),
        "template_id": template_schema.get("id"),
        "template_name": template_schema.get("name"),
    }

    return resolved
