from pprint import pprint

from core.schemas.discovery import list_projects, list_templates


def main():
    projects = list_projects("schemas")
    project_ids = {project["project_id"] for project in projects}

    assert "afinz" in project_ids
    assert "recovery" in project_ids
    assert "standard_template" in project_ids

    print("Projects discovery OK\n")
    pprint(projects)

    afinz_templates = list_templates("afinz", "schemas")
    afinz_template_ids = {template["template_id"] for template in afinz_templates}

    assert "informar_pendencia_maior_60" in afinz_template_ids
    assert "informar_pendencia_maior_60_2_" in afinz_template_ids
    assert "informar_pendencia_meno_60_2_" in afinz_template_ids
    assert "informar_pendencia_menor_60_" in afinz_template_ids

    recovery_templates = list_templates("recovery", "schemas")
    recovery_template_ids = {template["template_id"] for template in recovery_templates}

    assert "cobranca_varejo_11" in recovery_template_ids
    assert "cobranca_varejo_12" in recovery_template_ids

    print("\nAfinz templates discovery OK")
    pprint(afinz_templates)

    print("\nRecovery templates discovery OK")
    pprint(recovery_templates)


if __name__ == "__main__":
    main()
