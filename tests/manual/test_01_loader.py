from pprint import pprint

from core.schemas.loader import load_yaml


def main():
    afinz_project = load_yaml("schemas/afinz/project.yaml")
    recovery_template = load_yaml(
        "schemas/recovery/templates/cobranca_varejo_11.yaml"
    )

    assert isinstance(afinz_project, dict)
    assert isinstance(recovery_template, dict)

    assert afinz_project["id"] == "afinz"
    assert afinz_project["name"] == "Afinz"

    assert recovery_template["id"] == "cobranca_varejo_11"
    assert recovery_template["name"] == "cobranca_varejo_11"
    assert recovery_template["output"]["file_prefix"] == "COBRANCA_VAREJOA_11"

    print("Loader OK\n")
    print("Afinz project:")
    pprint(afinz_project)
    print("\nRecovery template:")
    pprint(recovery_template)


if __name__ == "__main__":
    main()
