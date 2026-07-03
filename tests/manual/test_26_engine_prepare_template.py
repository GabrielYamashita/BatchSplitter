from pprint import pprint

from core.engine import prepare_template


def main():
    result = prepare_template(
        project_schema_path="schemas/recovery/project.yaml",
        template_schema_path="schemas/recovery/templates/cobranca_varejo_11.yaml",
    )

    schema = result["schema"]
    preview = result["schema_preview"]

    assert schema["_meta"]["project_id"] == "recovery"
    assert schema["_meta"]["template_id"] == "cobranca_varejo_11"
    assert schema["output"]["file_prefix"] == "COBRANCA_VAREJO_11"

    expected_fields = {
        "nome",
        "telefone",
        "cpf",
        "id_caso",
        "ds_carteira_ajustada",
        "ds_squad",
    }
    assert expected_fields == set(schema["fields"].keys())

    output_names = {field["output_name"] for field in preview["fields"]}
    assert {
        "nome",
        "TEL_DEEP",
        "CPF",
        "IdCaso",
        "DsCarteiraAjustada",
        "DsSquad",
    }.issubset(output_names)

    print("Engine Prepare Template OK\n")
    pprint(preview)


if __name__ == "__main__":
    main()
