import pandas as pd

from core.batching.planner import build_batch_plan
from core.export.zip_exporter import render_filename
from core.schemas.resolver import resolve_schema


def main():
    schema = resolve_schema(
        "schemas/afinz/project.yaml",
        "schemas/afinz/templates/informar_pendencia_maior_60.yaml",
    )

    runtime_config = {
        "batch_size": 1000,
        "remainder_threshold_percent": 50,
        "batch_num": 5,
        "date": "0307",
    }

    df = pd.DataFrame({"x": [str(i) for i in range(2501)]})
    plan = build_batch_plan(df, schema, runtime_config)

    filenames = [
        render_filename(schema, batch, runtime_config)
        for batch in plan
    ]

    assert filenames == [
        "Afinz_PENDENCIA_MAIOR_60_Lote05_01_0307.csv",
        "Afinz_PENDENCIA_MAIOR_60_Lote05_02_0307.csv",
        "Afinz_PENDENCIA_MAIOR_60_Lote05_03_0307.csv",
    ]

    print("Filename Renderer OK\n")
    for filename in filenames:
        print(filename)


if __name__ == "__main__":
    main()
