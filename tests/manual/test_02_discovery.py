from pprint import pprint

from core.schemas.discovery import list_projects, list_templates


def main():
    projects = list_projects("schemas")

    assert len(projects) > 0
    assert any(project["project_id"] == "afinz" for project in projects)

    print("Projects discovery OK\n")
    pprint(projects)

    templates = list_templates("afinz", "schemas")

    assert len(templates) > 0
    assert any(template["template_id"] == "cp_preventivo_03" for template in templates)

    print("\nTemplates discovery OK\n")
    pprint(templates)


if __name__ == "__main__":
    main()
