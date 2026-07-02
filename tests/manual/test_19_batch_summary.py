from pprint import pprint

import pandas as pd

from core.batching.planner import build_batch_plan
from core.batching.summarizer import summarize_batch_plan
from core.schemas.resolver import resolve_schema


def main():
    schema = resolve_schema(
        "schemas/afinz/project.yaml",
        "schemas/afinz/templates/cp_preventivo_03.yaml",
    )

    df = pd.DataFrame({"nome": [str(i) for i in range(9500)]})

    runtime_config = {
        "batch_size": 1000,
        "remainder_threshold_percent": 50,
        "lote_num": 88,
    }

    plan = build_batch_plan(df, schema, runtime_config)
    summary = summarize_batch_plan(plan)

    assert summary["summary"] == "9 Lotes de 1000 + 1 Lote de 500"
    assert summary["total_batches"] == 10
    assert summary["total_rows"] == 9500

    print("Batch Summary OK\n")
    pprint(summary)


if __name__ == "__main__":
    main()
