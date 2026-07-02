from pprint import pprint

import pandas as pd

from core.batching.planner import build_batch_plan
from core.schemas.resolver import resolve_schema


def main():
    schema = resolve_schema(
        "schemas/afinz/project.yaml",
        "schemas/afinz/templates/cp_preventivo_03.yaml",
    )

    df = pd.DataFrame({"nome": [str(i) for i in range(9299)]})

    runtime_config = {
        "batch_size": 1000,
        "remainder_threshold_percent": 30,
        "batch_num": 7,
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
        1299,
    ]

    assert plan[-1] == {
        "batch_num": 7,
        "file_num": 9,
        "start": 8000,
        "end": 9299,
        "rows": 1299,
    }

    print("Batch Planner Below Custom Percent OK\n")
    pprint(plan)


if __name__ == "__main__":
    main()
