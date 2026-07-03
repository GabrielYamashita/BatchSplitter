from pprint import pprint

from core.schemas.resolver import resolve_schema


def main():
    schema = resolve_schema(
        "schemas/templates/project.yaml",
        "schemas/templates/templates/override_version.yaml",
    )

    assert "nome" not in schema["fields"]
    assert "telefone" in schema["fields"]

    assert schema["fields"]["telefone"]["required"] is True
    assert schema["fields"]["telefone"]["output_name"] == "WHATSAPP"
    assert schema["output"]["file_prefix"] == "OVERRIDE"

    print("Resolver Template Override OK\n")
    print("Resolved fields:")
    pprint(schema["fields"])


if __name__ == "__main__":
    main()
