from pprint import pprint

import pandas as pd

from core.batching.planner import build_batch_plan
from core.schemas.resolver import resolve_schema


def main():
    schema = resolve_schema(
        "schemas/afinz/project.yaml",
        "schemas/afinz/templates/cp_preventivo_03.yaml",
    )

    df = pd.DataFrame({"nome": [str(i) for i in range(9499)]})

    runtime_config = {
        "batch_size": 1000,
        "remainder_threshold_percent": 50,
        "batch_num": 5,
    }

    plan = build_batch_plan(df, schema, runtime_config)

    rows = [batch["rows"] for batch in plan]

    assert len(plan) == 9

    assert rows == [
        1000,
        1000,
        1000,
        1000,
        1000,
        1000,
        1000,
        1000,
        1499,
    ]

    assert plan[-1] == {
        "batch_num": 5,
        "file_num": 9,
        "start": 8000,
        "end": 9499,
        "rows": 1499,
    }

    print("Batch Planner Merge Small Remainder OK\n")
    pprint(plan)


if __name__ == "__main__":
    main()
