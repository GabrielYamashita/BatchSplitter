from core.batching.planner import build_batch_plan
from core.export.zip_exporter import render_filename
from core.schemas.resolver import resolve_schema


def main():
    schema = resolve_schema(
        "schemas/afinz/project.yaml",
        "schemas/afinz/templates/cp_preventivo_03.yaml",
    )

    runtime_config = {
        "batch_size": 1000,
        "remainder_threshold_percent": 50,
        "batch_num": 5,
        "date": "0307",
    }

    plan = build_batch_plan_from_dummy_total(
        total_rows=2501,
        schema=schema,
        runtime_config=runtime_config,
    )

    filenames = [render_filename(schema, batch, runtime_config) for batch in plan]

    assert filenames == [
        "Afinz_CP_PREVENTIVO_03_Lote05_01_0307.csv",
        "Afinz_CP_PREVENTIVO_03_Lote05_02_0307.csv",
        "Afinz_CP_PREVENTIVO_03_Lote05_03_0307.csv",
    ]

    print("Filename Renderer OK\n")

    for filename in filenames:
        print(filename)


def build_batch_plan_from_dummy_total(total_rows, schema, runtime_config):
    import pandas as pd

    df = pd.DataFrame({"x": [str(i) for i in range(total_rows)]})
    return build_batch_plan(df, schema, runtime_config)


if __name__ == "__main__":
    main()
