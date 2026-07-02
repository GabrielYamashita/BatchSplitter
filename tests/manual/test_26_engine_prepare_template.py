from pprint import pprint

from core.engine import prepare_template


def main():
    result = prepare_template(
        project_schema_path="schemas/afinz/project.yaml",
        template_schema_path="schemas/afinz/templates/cp_preventivo_03.yaml",
    )

    schema = result["schema"]
    preview = result["schema_preview"]

    assert schema["_meta"]["project_id"] == "afinz"
    assert schema["_meta"]["template_id"] == "cp_preventivo_03"

    assert "nome" in schema["fields"]
    assert "telefone" in schema["fields"]

    assert schema["output"]["file_prefix"] == "CP_PREVENTIVO_03"

    assert preview["project_id"] == "afinz"
    assert preview["template_id"] == "cp_preventivo_03"

    output_names = [field["output_name"] for field in preview["fields"]]

    assert "nome" in output_names
    assert "TEL_DEEP" in output_names

    print("Engine Prepare Template OK\n")
    pprint(preview)


if __name__ == "__main__":
    main()
