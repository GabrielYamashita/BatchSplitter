from __future__ import annotations

import csv
import io
from pathlib import Path
from typing import Any

import pandas as pd


def read_file_bytes(file) -> bytes:
    """
    Accepts:
    - Streamlit UploadedFile
    - file-like object
    - bytes
    - local file path

    Returns raw bytes.
    """
    if isinstance(file, bytes):
        return file

    if isinstance(file, (str, Path)):
        return Path(file).read_bytes()

    if hasattr(file, "seek"):
        file.seek(0)

    content = file.read()

    if isinstance(content, str):
        return content.encode("utf-8")

    if isinstance(content, bytes):
        return content

    raise TypeError("Unsupported file type. Expected bytes, path, or file-like object.")


def detect_delimiter(
    content: bytes,
    encoding: str,
    candidates: list[str],
) -> str:
    sample = content[:4096].decode(encoding, errors="ignore")

    try:
        dialect = csv.Sniffer().sniff(sample, delimiters="".join(candidates))
        return dialect.delimiter
    except Exception:
        pass

    first_line = sample.splitlines()[0] if sample.splitlines() else ""

    scores = {delimiter: first_line.count(delimiter) for delimiter in candidates}

    best_delimiter = max(scores, key=scores.get)

    if scores[best_delimiter] > 0:
        return best_delimiter

    return candidates[0] if candidates else ";"


def read_csv_auto(file, schema: dict[str, Any]) -> dict[str, Any]:
    """
    Reads a CSV according to schema input config.

    Returns:
    {
        "df": DataFrame,
        "encoding": str,
        "delimiter": str,
        "rows": int,
        "columns": list[str],
    }
    """
    input_config = schema.get("input", {})

    encodings = input_config.get(
        "encoding_fallbacks",
        ["utf-8", "utf-8-sig", "latin1"],
    )

    candidates = input_config.get(
        "delimiter_candidates",
        [";", ",", "|", "\t"],
    )

    auto_detect = input_config.get("auto_detect_delimiter", True)

    content = read_file_bytes(file)

    last_error: Exception | None = None

    for encoding in encodings:
        try:
            delimiter = (
                detect_delimiter(content, encoding, candidates)
                if auto_detect
                else candidates[0]
            )

            df = pd.read_csv(
                io.BytesIO(content),
                sep=delimiter,
                encoding=encoding,
                dtype=str,
                keep_default_na=False,
            )

            return {
                "df": df,
                "encoding": encoding,
                "delimiter": delimiter,
                "rows": len(df),
                "columns": list(df.columns),
            }

        except Exception as error:
            last_error = error

    raise ValueError(f"Could not read CSV file. Last error: {last_error}")
