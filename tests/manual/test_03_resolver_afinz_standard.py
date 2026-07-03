from pprint import pprint

from core.schemas.resolver import resolve_schema


def main():
    schema = resolve_schema(
        "schemas/afinz/project.yaml",
        "schemas/afinz/templates/informar_pendencia_maior_60.yaml",
    )

    assert schema["id"] == "informar_pendencia_maior_60"
    assert schema["name"] == "informar_pendencia_maior_60"

    assert schema["_meta"]["project_id"] == "afinz"
    assert schema["_meta"]["project_name"] == "Afinz"
    assert schema["_meta"]["template_id"] == "informar_pendencia_maior_60"

    assert set(schema["fields"].keys()) == {"nome", "telefone"}
    assert schema["fields"]["nome"]["output_name"] == "nome"
    assert schema["fields"]["telefone"]["output_name"] == "TEL_DEEP"

    assert schema["output"]["file_prefix"] == "PENDENCIA_MAIOR_60"
    assert schema["output"]["filename_pattern"] == (
        "{name}_{prefix}_Lote{batch_num}_{file_num}_{date}.csv"
    )

    print("Resolver Afinz Standard OK\n")
    print("Resolved fields:")
    pprint(schema["fields"])
    print("\nResolved output:")
    pprint(schema["output"])


if __name__ == "__main__":
    main()
