from pprint import pprint

from core.schemas.resolver import resolve_schema


def main():
    schema = resolve_schema(
        "schemas/afinz/project.yaml",
        "schemas/afinz/templates/cp_preventivo_03.yaml",
    )

    assert schema["id"] == "cp_preventivo_03"
    assert schema["name"] == "cp_preventivo_03"

    assert schema["_meta"]["project_id"] == "afinz"
    assert schema["_meta"]["template_id"] == "cp_preventivo_03"

    assert "nome" in schema["fields"]
    assert "telefone" in schema["fields"]

    assert schema["fields"]["nome"]["output_name"] == "nome"
    assert schema["fields"]["telefone"]["output_name"] == "TEL_DEEP"

    assert schema["output"]["file_prefix"] == "CP_PREVENTIVO_03"
    assert "filename_pattern" in schema["output"]

    print("Resolver CP Preventivo OK\n")

    print("Resolved fields:")
    pprint(schema["fields"])

    print("\nResolved output:")
    pprint(schema["output"])


if __name__ == "__main__":
    main()
