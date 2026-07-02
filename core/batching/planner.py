from __future__ import annotations

from typing import Any

import pandas as pd


def get_batch_config(
    schema: dict[str, Any],
    runtime_config: dict[str, Any] | None = None,
) -> dict[str, int | float]:
    runtime_config = runtime_config or {}

    batch_config = schema.get("batch", {})

    batch_size = int(
        runtime_config.get(
            "batch_size",
            batch_config.get("default_size", 2000),
        )
    )

    remainder_threshold_percent = float(
        runtime_config.get(
            "remainder_threshold_percent",
            batch_config.get("remainder_threshold_percent", 50),
        )
    )

    batch_num = int(
        runtime_config.get(
            "batch_num",
            batch_config.get("default_batch_num", 1),
        )
    )

    if batch_size <= 0:
        raise ValueError("batch_size must be greater than zero.")

    if remainder_threshold_percent < 0 or remainder_threshold_percent > 100:
        raise ValueError("remainder_threshold_percent must be between 0 and 100.")

    if batch_num <= 0:
        raise ValueError("batch_num must be greater than zero.")

    return {
        "batch_size": batch_size,
        "remainder_threshold_percent": remainder_threshold_percent,
        "batch_num": batch_num,
    }


def should_merge_remainder(
    remainder: int,
    batch_size: int,
    remainder_threshold_percent: float,
) -> bool:
    if remainder <= 0:
        return False

    remainder_percent = (remainder / batch_size) * 100

    return remainder_percent < remainder_threshold_percent


def build_batch_plan_from_total(
    total_rows: int,
    schema: dict[str, Any],
    runtime_config: dict[str, Any] | None = None,
) -> list[dict[str, int]]:
    config = get_batch_config(schema, runtime_config)

    batch_size = int(config["batch_size"])
    remainder_threshold_percent = float(config["remainder_threshold_percent"])
    batch_num = int(config["batch_num"])

    if total_rows < 0:
        raise ValueError("total_rows cannot be negative.")

    if total_rows == 0:
        return []

    batches: list[dict[str, int]] = []

    start = 0
    file_num = 1

    while start < total_rows:
        end = min(start + batch_size, total_rows)
        remaining = total_rows - end

        if should_merge_remainder(
            remainder=remaining,
            batch_size=batch_size,
            remainder_threshold_percent=remainder_threshold_percent,
        ):
            end = total_rows

        batches.append(
            {
                "batch_num": batch_num,
                "file_num": file_num,
                "start": start,
                "end": end,
                "rows": end - start,
            }
        )

        start = end
        file_num += 1

    return batches


def build_batch_plan(
    df: pd.DataFrame,
    schema: dict[str, Any],
    runtime_config: dict[str, Any] | None = None,
) -> list[dict[str, int]]:
    return build_batch_plan_from_total(
        total_rows=len(df),
        schema=schema,
        runtime_config=runtime_config,
    )
