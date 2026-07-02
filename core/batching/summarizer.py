from __future__ import annotations

from collections import OrderedDict


def pluralize_lote(count: int) -> str:
    return "Lote" if count == 1 else "Lotes"


def summarize_batch_plan(batch_plan: list[dict[str, int]]) -> dict:
    if not batch_plan:
        return {
            "summary": "Nenhum lote gerado",
            "total_batches": 0,
            "total_rows": 0,
            "groups": [],
        }

    groups_map: OrderedDict[int, int] = OrderedDict()

    for batch in batch_plan:
        rows = int(batch["rows"])
        groups_map[rows] = groups_map.get(rows, 0) + 1

    groups = [
        {
            "rows": rows,
            "count": count,
            "label": f"{count} {pluralize_lote(count)} de {rows}",
        }
        for rows, count in groups_map.items()
    ]

    summary = " + ".join(group["label"] for group in groups)

    total_rows = sum(int(batch["rows"]) for batch in batch_plan)

    return {
        "summary": summary,
        "total_batches": len(batch_plan),
        "total_rows": total_rows,
        "groups": groups,
    }
