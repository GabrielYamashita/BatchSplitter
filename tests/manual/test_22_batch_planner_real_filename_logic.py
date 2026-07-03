from pprint import pprint

import pandas as pd

from core.batching.planner import build_batch_plan
from core.batching.summarizer import summarize_batch_plan
from core.schemas.resolver import resolve_schema


def main():
    schema = resolve_schema(
        "schemas/afinz/project.yaml",
        "schemas/afinz/templates/informar_pendencia_maior_60.yaml",
    )

    df = pd.DataFrame({"nome": [str(i) for i in range(2501)]})

    runtime_config = {
        "batch_size": 1000,
        "remainder_threshold_percent": 50,
        "batch_num": 5,
        "date": "0307",
    }

    plan = build_batch_plan(df, schema, runtime_config)
    summary = summarize_batch_plan(plan)
    rows = [batch["rows"] for batch in plan]

    assert rows == [1000, 1000, 501]
    assert plan == [
        {
            "batch_num": 5,
            "file_num": 1,
            "start": 0,
            "end": 1000,
            "rows": 1000,
        },
        {
            "batch_num": 5,
            "file_num": 2,
            "start": 1000,
            "end": 2000,
            "rows": 1000,
        },
        {
            "batch_num": 5,
            "file_num": 3,
            "start": 2000,
            "end": 2501,
            "rows": 501,
        },
    ]
    assert summary["summary"] == "2 Lotes de 1000 + 1 Lote de 501"
    assert summary["total_batches"] == 3
    assert summary["total_rows"] == 2501

    print("Batch Planner Real Filename Logic OK\n")
    pprint(plan)
    pprint(summary)


if __name__ == "__main__":
    main()
