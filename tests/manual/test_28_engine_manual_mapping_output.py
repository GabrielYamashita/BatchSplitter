from __future__ import annotations

import io
from pprint import pprint

from core.engine import (
    apply_mapping_and_build_output,
    prepare_template,
    prepare_uploaded_file,
)


class NamedBytesIO(io.BytesIO):
    def __init__(self, content: bytes, name: str):
        super().__init__(content)
        self.name = name


def main():
    template_result = prepare_template(
        project_schema_path="schemas/afinz/project.yaml",
        template_schema_path="schemas/afinz/templates/informar_pendencia_maior_60.yaml",
    )

    schema = template_result["schema"]

    csv_content = (
        "Nome Cliente;Fone Principal;CPF\n"
        "Gabriel;011999999999;01234567890\n"
        "Yama;011988888888;00123456789\n"
    ).encode("utf-8")

    uploaded_file = NamedBytesIO(csv_content, "clientes.csv")

    upload_result = prepare_uploaded_file(
        uploaded_file=uploaded_file,
        schema=schema,
    )

    assert upload_result["validation"]["valid"] is False
    assert "telefone" in upload_result["mapping"]["missing_required"]

    manual_mapping = {
        "telefone": "Fone Principal",
    }

    output_result = apply_mapping_and_build_output(
        df_clean=upload_result["df_clean"],
        schema=schema,
        mapping=upload_result["mapping"],
        manual_mapping=manual_mapping,
        preview_rows=2,
    )

    assert output_result["success"] is True
    assert output_result["validation"]["valid"] is True

    df_output = output_result["df_output"]
    output_report = output_result["output_result"]["report"]

    assert list(df_output.columns) == ["nome", "TEL_DEEP", "CPF"]
    assert len(df_output) == 2
    assert output_report["kept_unmapped_columns"] == ["CPF"]

    assert df_output.loc[0, "nome"] == "Gabriel"
    assert df_output.loc[0, "TEL_DEEP"] == "011999999999"
    assert df_output.loc[0, "CPF"] == "01234567890"

    print("Engine Manual Mapping Output OK\n")
    print("Final mapping:")
    pprint(output_result["mapping"])
    print("\nOutput report:")
    pprint(output_report)
    print("\nOutput preview:")
    print(output_result["output_preview"]["sample"])


if __name__ == "__main__":
    main()
