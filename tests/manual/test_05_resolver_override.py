from pprint import pprint

from core.schemas.resolver import resolve_schema


def main():
    schema = resolve_schema(
        "schemas/afinz/project.yaml",
        "schemas/afinz/templates/override.yaml",
    )

    assert "nome" not in schema["fields"]
    assert "telefone" in schema["fields"]

    assert schema["fields"]["telefone"]["output_name"] == "TEL_DEEP"

    print("Resolver Override OK\n")

    print("Resolved fields:")
    pprint(schema["fields"])


if __name__ == "__main__":
    main()
