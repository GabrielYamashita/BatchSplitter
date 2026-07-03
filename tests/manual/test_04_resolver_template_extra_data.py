from pprint import pprint

from core.schemas.resolver import resolve_schema


def main():
    schema = resolve_schema(
        "schemas/templates/project.yaml",
        "schemas/templates/templates/extra_data_version.yaml",
    )

    expected_fields = {
        "nome",
        "telefone",
        "valor_parcela",
        "data_vencimento",
        "dias_atraso",
    }

    assert expected_fields == set(schema["fields"].keys())
    assert schema["_meta"]["project_id"] == "standard_template"
    assert schema["_meta"]["template_id"] == "extra_data"

    assert schema["fields"]["nome"]["output_name"] == "nome"
    assert schema["fields"]["telefone"]["output_name"] == "TEL_DEEP"
    assert schema["fields"]["valor_parcela"]["required"] is False
    assert schema["fields"]["data_vencimento"]["required"] is False
    assert schema["fields"]["dias_atraso"]["required"] is False

    assert schema["output"]["file_prefix"] == "EXTRA_DATA"

    print("Resolver Template Extra Data OK\n")
    print("Resolved fields:")
    pprint(schema["fields"])


if __name__ == "__main__":
    main()
