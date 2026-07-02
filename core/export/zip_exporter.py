from __future__ import annotations

import io
import re
import zipfile
from typing import Any

import pandas as pd


def format_number(value: int | str, width: int = 2) -> str:
    return f"{int(value):0{width}d}"


def sanitize_filename(filename: str) -> str:
    """
    Avoid unsafe path characters inside ZIP names.
    Keeps the filename simple and predictable.
    """
    filename = str(filename).strip()
    filename = filename.replace("\\", "_").replace("/", "_")
    filename = re.sub(r"[\r\n\t]+", "_", filename)
    return filename


def render_filename(
    schema: dict[str, Any],
    batch: dict[str, int],
    runtime_config: dict[str, Any],
) -> str:
    output_config = schema.get("output", {})

    pattern = output_config.get(
        "filename_pattern",
        "{prefix}_Lote{batch_num}_{file_num}_{date}.csv",
    )

    prefix = output_config.get("file_prefix", schema.get("id", "batch"))
    date = runtime_config.get("date", "")

    filename = pattern.format(
        prefix=prefix,
        batch_num=format_number(batch["batch_num"]),
        file_num=format_number(batch["file_num"]),
        date=date,
    )

    extension = output_config.get("extension", "csv")

    if extension and not filename.lower().endswith(f".{extension.lower()}"):
        filename = f"{filename}.{extension}"

    return sanitize_filename(filename)


def dataframe_to_csv_bytes(
    df: pd.DataFrame,
    schema: dict[str, Any],
) -> bytes:
    output_config = schema.get("output", {})

    delimiter = output_config.get("delimiter", ";")
    encoding = output_config.get("encoding", "utf-8-sig")
    include_header = bool(output_config.get("include_header", True))

    csv_buffer = io.StringIO()

    df.to_csv(
        csv_buffer,
        index=False,
        sep=delimiter,
        header=include_header,
    )

    return csv_buffer.getvalue().encode(encoding)


def export_batches_to_zip(
    df_output: pd.DataFrame,
    batch_plan: list[dict[str, int]],
    schema: dict[str, Any],
    runtime_config: dict[str, Any],
) -> dict[str, Any]:
    """
    Returns:
    {
        "zip_bytes": bytes,
        "files": [
            {
                "filename": str,
                "rows": int,
                "batch_num": int,
                "file_num": int,
            }
        ]
    }
    """
    zip_buffer = io.BytesIO()
    files = []

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for batch in batch_plan:
            batch_df = df_output.iloc[batch["start"] : batch["end"]].copy()

            filename = render_filename(
                schema=schema,
                batch=batch,
                runtime_config=runtime_config,
            )

            csv_bytes = dataframe_to_csv_bytes(batch_df, schema)

            zip_file.writestr(filename, csv_bytes)

            files.append(
                {
                    "filename": filename,
                    "rows": len(batch_df),
                    "batch_num": batch["batch_num"],
                    "file_num": batch["file_num"],
                }
            )

    zip_buffer.seek(0)

    return {
        "zip_bytes": zip_buffer.getvalue(),
        "files": files,
    }
