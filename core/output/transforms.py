from __future__ import annotations

import pandas as pd

NAME_PARTICLES = {"de", "da", "do", "das", "dos", "e"}


def title_case_name(value) -> str:
    if pd.isna(value):
        return ""

    text = str(value).strip()

    if not text:
        return ""

    words = text.lower().split()

    formatted_words = []

    for index, word in enumerate(words):
        if index > 0 and word in NAME_PARTICLES:
            formatted_words.append(word)
        else:
            formatted_words.append(word.capitalize())

    return " ".join(formatted_words)


def cpf_pad_left_preserve_format(value) -> str:
    if pd.isna(value):
        return ""

    text = str(value).strip()

    if not text:
        return ""

    digits_count = sum(char.isdigit() for char in text)

    if digits_count >= 11:
        return text

    zeros_to_add = 11 - digits_count

    return ("0" * zeros_to_add) + text


TRANSFORMS = {
    "title_case_name": title_case_name,
    "cpf_pad_left_preserve_format": cpf_pad_left_preserve_format,
}


def apply_output_transforms(df: pd.DataFrame, schema: dict) -> pd.DataFrame:
    output = df.copy()

    for field_config in schema.get("fields", {}).values():
        output_name = field_config.get("output_name")
        transforms = field_config.get("transforms", [])

        if not output_name:
            continue

        if output_name not in output.columns:
            continue

        for transform_name in transforms:
            transform_func = TRANSFORMS.get(transform_name)

            if not transform_func:
                raise ValueError(f"Transform not found: {transform_name}")

            output[output_name] = output[output_name].apply(transform_func)

    return output
