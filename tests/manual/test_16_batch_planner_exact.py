from pprint import pprint

import pandas as pd

from core.batching.planner import build_batch_plan
from core.schemas.resolver import resolve_schema


def main():
    schema = resolve_schema(
        "schemas/afinz/project.yaml",
        "schemas/afinz/templates/informar_pendencia_maior_60.yaml",
    )

    df = pd.DataFrame({"nome": [str(i) for i in range(10000)]})

    runtime_config = {
        "batch_size": 1000,
        "remainder_threshold_percent": 50,
        "batch_num": 5,
    }

    plan = build_batch_plan(df, schema, runtime_config)

    assert len(plan) == 10
    assert all(batch["rows"] == 1000 for batch in plan)
    assert plan[0] == {
        "batch_num": 5,
        "file_num": 1,
        "start": 0,
        "end": 1000,
        "rows": 1000,
    }
    assert plan[-1] == {
        "batch_num": 5,
        "file_num": 10,
        "start": 9000,
        "end": 10000,
        "rows": 1000,
    }

    print("Batch Planner Exact OK\n")
    pprint(plan)


if __name__ == "__main__":
    main()
