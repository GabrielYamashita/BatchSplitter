from __future__ import annotations

import io
from pprint import pprint

from core.engine import prepare_template, prepare_uploaded_file


class NamedBytesIO(io.BytesIO):
    def __init__(self, content: bytes, name: str):
        super().__init__(content)
        self.name = name


def main():
    template_result = prepare_template(
        project_schema_path="schemas/afinz/project.yaml",
        template_schema_path="schemas/afinz/templates/cp_preventivo_03.yaml",
    )

    schema = template_result["schema"]

    csv_content = (
        "Nome Cliente;Celular;CPF\n"
        "Gabriel;011999999999;01234567890\n"
        "Yama;011988888888;00123456789\n"
    ).encode("utf-8")

    uploaded_file = NamedBytesIO(csv_content, "clientes.csv")

    result = prepare_uploaded_file(
        uploaded_file=uploaded_file,
        schema=schema,
        preview_rows=1,
    )

    assert result["read_info"]["delimiter"] == ";"
    assert result["cleaning_report"]["final_rows"] == 2

    assert result["input_preview"]["rows"] == 2
    assert result["input_preview"]["columns"] == [
        "Nome Cliente",
        "Celular",
        "CPF",
    ]

    mapping = result["mapping"]

    assert mapping["mapped"]["nome"] == "Nome Cliente"
    assert mapping["mapped"]["telefone"] == "Celular"
    assert mapping["missing_required"] == []

    assert result["validation"]["valid"] is True

    print("Engine Prepare Uploaded File OK\n")

    print("Read info:")
    pprint(result["read_info"])

    print("\nCleaning report:")
    pprint(result["cleaning_report"])

    print("\nMapping:")
    pprint(result["mapping"])

    print("\nValidation:")
    pprint(result["validation"])

    print("\nInput preview:")
    print(result["input_preview"]["sample"])


if __name__ == "__main__":
    main()
