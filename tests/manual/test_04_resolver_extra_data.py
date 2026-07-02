from pprint import pprint

from core.schemas.resolver import resolve_schema


def main():
    schema = resolve_schema(
        "schemas/afinz/project.yaml",
        "schemas/afinz/templates/extra_data.yaml",
    )

    expected_fields = {
        "nome",
        "telefone",
        "valor_parcela",
        "data_vencimento",
        "dias_atraso",
    }

    resolved_fields = set(schema["fields"].keys())

    assert expected_fields.issubset(resolved_fields)

    assert schema["fields"]["nome"]["output_name"] == "nome"
    assert schema["fields"]["telefone"]["output_name"] == "TEL_DEEP"
    assert schema["fields"]["valor_parcela"]["required"] is True

    print("Resolver Extra Data OK\n")

    print("Resolved fields:")
    pprint(schema["fields"])


if __name__ == "__main__":
    main()
