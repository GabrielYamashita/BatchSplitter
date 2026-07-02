from pprint import pprint

from core.schemas.discovery import list_projects, list_templates
from core.schemas.resolver import resolve_schema

SCHEMA_ROOT = "schemas"


def main():
    print("\nPROJECTS")
    projects = list_projects(SCHEMA_ROOT)
    pprint(projects)

    print("\nTEMPLATES")
    templates = list_templates("Afinz", SCHEMA_ROOT)
    pprint(templates)

    # cp_preventivo_03
    print("\nRESOLVED: cp_preventivo_03")
    schema = resolve_schema(
        "schemas/afinz/project.yaml",
        "schemas/afinz/templates/cp_preventivo_03.yaml",
    )

    print("Template:", schema["_meta"]["template_name"])
    print("Output prefix:", schema["output"]["file_prefix"])
    print("Fields:")
    pprint(schema["fields"])

    # extra_data
    print("\nRESOLVED: extra_data")
    schema = resolve_schema(
        "schemas/afinz/project.yaml",
        "schemas/afinz/templates/extra_data.yaml",
    )

    print("Template:", schema["_meta"]["template_name"])
    print("Output prefix:", schema["output"]["file_prefix"])
    print("Fields:")
    pprint(schema["fields"])

    # override
    print("\nRESOLVED: override")
    schema_override = resolve_schema(
        "schemas/afinz/project.yaml",
        "schemas/afinz/templates/override.yaml",
    )

    print("Template:", schema_override["_meta"]["template_name"])
    print("Output prefix:", schema_override["output"]["file_prefix"])
    print("Fields:")
    pprint(schema_override["fields"])


if __name__ == "__main__":
    main()
