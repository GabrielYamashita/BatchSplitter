import io
import zipfile
from pprint import pprint

import pandas as pd

from core.batching.planner import build_batch_plan
from core.export.zip_exporter import export_batches_to_zip
from core.schemas.resolver import resolve_schema


def main():
    schema = resolve_schema(
        "schemas/afinz/project.yaml",
        "schemas/afinz/templates/informar_pendencia_maior_60.yaml",
    )

    df_output = pd.DataFrame(
        {
            "nome": ["Gabriel", "Yama", "Teste"],
            "TEL_DEEP": ["011999999999", "011988888888", "011977777777"],
        }
    )

    runtime_config = {
        "batch_size": 2,
        "remainder_threshold_percent": 50,
        "batch_num": 5,
        "date": "0307",
    }

    batch_plan = build_batch_plan(df_output, schema, runtime_config)

    result = export_batches_to_zip(
        df_output=df_output,
        batch_plan=batch_plan,
        schema=schema,
        runtime_config=runtime_config,
    )

    zip_bytes = result["zip_bytes"]
    files = result["files"]

    assert isinstance(zip_bytes, bytes)
    assert len(zip_bytes) > 0
    assert files == [
        {
            "filename": "Afinz_PENDENCIA_MAIOR_60_Lote05_01_0307.csv",
            "rows": 2,
            "batch_num": 5,
            "file_num": 1,
        },
        {
            "filename": "Afinz_PENDENCIA_MAIOR_60_Lote05_02_0307.csv",
            "rows": 1,
            "batch_num": 5,
            "file_num": 2,
        },
    ]

    with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as zip_file:
        names = zip_file.namelist()
        assert names == [
            "Afinz_PENDENCIA_MAIOR_60_Lote05_01_0307.csv",
            "Afinz_PENDENCIA_MAIOR_60_Lote05_02_0307.csv",
        ]

        first_file_bytes = zip_file.read(names[0])
        first_df = pd.read_csv(
            io.BytesIO(first_file_bytes),
            sep=";",
            dtype=str,
            keep_default_na=False,
        )

        assert list(first_df.columns) == ["nome", "TEL_DEEP"]
        assert len(first_df) == 2
        assert first_df.loc[0, "nome"] == "Gabriel"
        assert first_df.loc[0, "TEL_DEEP"] == "011999999999"

    print("ZIP Exporter Basic OK\n")
    print("Files:")
    pprint(files)


if __name__ == "__main__":
    main()
