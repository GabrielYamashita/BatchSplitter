from __future__ import annotations

import io
import zipfile
from pprint import pprint

import pandas as pd

from core.engine import (
    apply_mapping_and_build_output,
    generate_zip,
    prepare_batches,
    prepare_template,
    prepare_uploaded_file,
)


class NamedBytesIO(io.BytesIO):
    def __init__(self, content: bytes, name: str):
        super().__init__(content)
        self.name = name


def main():
    template_result = prepare_template(
        project_schema_path="schemas/recovery/project.yaml",
        template_schema_path="schemas/recovery/templates/cobranca_varejo_11.yaml",
    )

    schema = template_result["schema"]

    lines = ["NrCpfCnpj;FirstName;IdCaso;NrTelefoneCompleto;DsCarteiraAjustada;DsSquad"]

    for i in range(2501):
        lines.append(f"{i:011d};Cliente {i};CASO{i:04d};0119{i:08d};Carteira A;Squad 1")

    csv_content = "\n".join(lines).encode("utf-8")
    uploaded_file = NamedBytesIO(csv_content, "clientes.csv")

    upload_result = prepare_uploaded_file(
        uploaded_file=uploaded_file,
        schema=schema,
    )

    assert upload_result["validation"]["valid"] is True

    output_result = apply_mapping_and_build_output(
        df_clean=upload_result["df_clean"],
        schema=schema,
        mapping=upload_result["mapping"],
    )

    assert output_result["success"] is True

    df_output = output_result["df_output"]
    output_report = output_result["output_result"]["report"]

    assert list(df_output.columns) == [
        "CPF",
        "nome",
        "IdCaso",
        "TEL_DEEP",
        "DsCarteiraAjustada",
        "DsSquad",
    ]
    assert len(df_output) == 2501
    assert output_report["kept_unmapped_columns"] == []

    runtime_config = {
        "batch_size": 1000,
        "remainder_threshold_percent": 50,
        "batch_num": 5,
        "date": "0307",
    }

    batch_result = prepare_batches(
        df_output=df_output,
        schema=schema,
        runtime_config=runtime_config,
    )

    batch_plan = batch_result["batch_plan"]
    batch_summary = batch_result["batch_summary"]

    assert batch_summary["summary"] == "2 Lotes de 1000 + 1 Lote de 501"

    zip_result = generate_zip(
        df_output=df_output,
        batch_plan=batch_plan,
        schema=schema,
        runtime_config=runtime_config,
    )

    files = zip_result["files"]
    zip_bytes = zip_result["zip_bytes"]

    assert [file["filename"] for file in files] == [
        "Recovery_COBRANCA_VAREJO_11_Lote05_01_0307.csv",
        "Recovery_COBRANCA_VAREJO_11_Lote05_02_0307.csv",
        "Recovery_COBRANCA_VAREJO_11_Lote05_03_0307.csv",
    ]
    assert [file["rows"] for file in files] == [1000, 1000, 501]

    with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as zip_file:
        names = zip_file.namelist()
        assert names == [
            "Recovery_COBRANCA_VAREJO_11_Lote05_01_0307.csv",
            "Recovery_COBRANCA_VAREJO_11_Lote05_02_0307.csv",
            "Recovery_COBRANCA_VAREJO_11_Lote05_03_0307.csv",
        ]

        first_file = pd.read_csv(
            io.BytesIO(zip_file.read(names[0])),
            sep=";",
            dtype=str,
            keep_default_na=False,
        )

        assert list(first_file.columns) == [
            "CPF",
            "nome",
            "IdCaso",
            "TEL_DEEP",
            "DsCarteiraAjustada",
            "DsSquad",
        ]
        assert len(first_file) == 1000

    print("Engine Full Flow OK\n")
    print("Batch summary:")
    pprint(batch_summary)
    print("\nGenerated files:")
    pprint(files)


if __name__ == "__main__":
    main()
