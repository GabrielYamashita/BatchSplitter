from pathlib import Path
from typing import Any

from core.schemas.loader import load_yaml


def list_projects(schema_root: str | Path = "schemas") -> list[dict[str, Any]]:
    schema_root = Path(schema_root)

    if not schema_root.exists():
        return []

    projects = []

    for project_dir in schema_root.iterdir():
        if not project_dir.is_dir():
            continue

        project_path = project_dir / "project.yaml"

        if not project_path.exists():
            continue

        project_schema = load_yaml(project_path)

        if project_schema.get("active", True) is False:
            continue

        projects.append(
            {
                "project_id": project_schema.get("id", project_dir.name),
                "project_name": project_schema.get("name", project_dir.name),
                "project_path": str(project_path),
                "project_dir": str(project_dir),
            }
        )

    return sorted(projects, key=lambda item: item["project_name"].lower())


def list_templates(
    project_id: str,
    schema_root: str | Path = "schemas",
) -> list[dict[str, Any]]:
    schema_root = Path(schema_root)
    project_dir = schema_root / project_id
    templates_dir = project_dir / "templates"

    if not templates_dir.exists():
        return []

    templates = []

    for template_path in templates_dir.glob("*.yaml"):
        template_schema = load_yaml(template_path)

        if template_schema.get("active", True) is False:
            continue

        templates.append(
            {
                "template_id": template_schema.get("id", template_path.stem),
                "template_name": template_schema.get("name", template_path.stem),
                "template_path": str(template_path),
                "project_id": project_id,
            }
        )

    return sorted(templates, key=lambda item: item["template_name"].lower())
