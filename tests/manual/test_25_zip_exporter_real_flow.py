import io
import zipfile
from pprint import pprint

import pandas as pd

from core.batching.planner import build_batch_plan
from core.batching.summarizer import summarize_batch_plan
from core.export.zip_exporter import export_batches_to_zip
from core.mapping.mapper import auto_map_columns
from core.output.builder import build_output_dataframe
from core.schemas.resolver import resolve_schema
from core.validation.validator import validate_mapping


def main():
    schema = resolve_schema(
        "schemas/afinz/project.yaml",
        "schemas/afinz/templates/cp_preventivo_03.yaml",
    )

    df_clean = pd.DataFrame(
        {
            "Nome Cliente": [f"Cliente {i}" for i in range(2501)],
            "Celular": [f"0119{i:08d}" for i in range(2501)],
            "CPF": [f"{i:011d}" for i in range(2501)],
        }
    )

    mapping = auto_map_columns(df_clean, schema)
    validation = validate_mapping(mapping, schema)

    assert validation["valid"] is True

    output_result = build_output_dataframe(
        df=df_clean,
        mapping=mapping,
        schema=schema,
    )

    df_output = output_result["df"]

    assert list(df_output.columns) == ["nome", "TEL_DEEP"]
    assert len(df_output) == 2501

    runtime_config = {
        "batch_size": 1000,
        "remainder_threshold_percent": 50,
        "batch_num": 5,
        "date": "0307",
    }

    batch_plan = build_batch_plan(df_output, schema, runtime_config)
    batch_summary = summarize_batch_plan(batch_plan)

    assert batch_summary["summary"] == "2 Lotes de 1000 + 1 Lote de 501"

    zip_result = export_batches_to_zip(
        df_output=df_output,
        batch_plan=batch_plan,
        schema=schema,
        runtime_config=runtime_config,
    )

    zip_bytes = zip_result["zip_bytes"]
    files = zip_result["files"]

    assert [file["filename"] for file in files] == [
        "CP_PREVENTIVO_03_Lote05_01_0307.csv",
        "CP_PREVENTIVO_03_Lote05_02_0307.csv",
        "CP_PREVENTIVO_03_Lote05_03_0307.csv",
    ]

    assert [file["rows"] for file in files] == [1000, 1000, 501]

    with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as zip_file:
        names = zip_file.namelist()

        assert names == [
            "CP_PREVENTIVO_03_Lote05_01_0307.csv",
            "CP_PREVENTIVO_03_Lote05_02_0307.csv",
            "CP_PREVENTIVO_03_Lote05_03_0307.csv",
        ]

        third_file = pd.read_csv(
            io.BytesIO(zip_file.read(names[2])),
            sep=";",
            dtype=str,
            keep_default_na=False,
        )

        assert len(third_file) == 501
        assert list(third_file.columns) == ["nome", "TEL_DEEP"]

    print("ZIP Exporter Real Flow OK\n")

    print("Batch summary:")
    pprint(batch_summary)

    print("\nFiles:")
    pprint(files)


if __name__ == "__main__":
    main()
