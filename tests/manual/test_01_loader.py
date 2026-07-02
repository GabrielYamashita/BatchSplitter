from pprint import pprint

from core.schemas.loader import load_yaml


def main():
    project = load_yaml("schemas/afinz/project.yaml")
    template = load_yaml("schemas/afinz/templates/cp_preventivo_03.yaml")

    assert isinstance(project, dict)
    assert isinstance(template, dict)

    assert project["id"] == "afinz"
    assert project["name"] == "Afinz"

    assert template["id"] == "cp_preventivo_03"
    assert template["name"] == "cp_preventivo_03"

    print("Loader OK\n")

    print("Project:")
    pprint(project)

    print("\nTemplate:")
    pprint(template)


if __name__ == "__main__":
    main()
