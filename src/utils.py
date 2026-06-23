from __future__ import annotations

import ast
import math
import re
from pathlib import Path
from typing import Any

import pandas as pd


ND = "ND"

NULL_STRINGS = {
    "",
    "n/a",
    "na",
    "nan",
    "none",
    "null",
    "nil",
    "#n/a",
    "non renseigné",
    "non renseigne",
}

TRUE_STRINGS = {
    "true",
    "vrai",
    "1",
    "yes",
    "oui",
    "y",
    "checked",
    "coché",
    "coche",
    "case cochée",
    "case cochee",
    "x",
}

FALSE_STRINGS = {
    "false",
    "faux",
    "0",
    "no",
    "non",
    "n",
    "unchecked",
    "non coché",
    "non coche",
    "case non cochée",
    "case non cochee",
}


def is_missing(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, float) and math.isnan(value):
        return True
    text = str(value).strip()
    return text.lower() in NULL_STRINGS


def clean_text(value: Any) -> str:
    if is_missing(value):
        return ND
    text = str(value).strip()
    text = re.sub(r"\s+", " ", text)
    return text if text else ND


def normalize_boolean(value: Any) -> str:
    if is_missing(value):
        return ND
    text = clean_text(value)
    lowered = text.casefold()
    if lowered in TRUE_STRINGS:
        return "oui"
    if lowered in FALSE_STRINGS:
        return "non"
    return text


def normalize_nd(value: Any) -> str:
    if is_missing(value):
        return ND
    if isinstance(value, bool):
        return "oui" if value else "non"
    text = clean_text(value)
    lowered = text.casefold()
    if lowered in TRUE_STRINGS:
        return "oui"
    if lowered in FALSE_STRINGS:
        return "non"
    return text


def clean_sector(value: Any) -> str:
    text = clean_text(value)
    if text == ND:
        return ND
    text = re.sub(r"\bromandie\b", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\b[àa]\s*$", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text).strip(" -_,;")
    if not text:
        return ND
    return text[:1].upper() + text[1:]


PHONE_RE = re.compile(r"(?:\+|00)?\d[\d\s()./-]{5,}\d")


def _normalize_phone(raw_phone: str) -> str:
    phone = raw_phone.strip().strip("*").strip()
    phone = re.sub(r"\s+", " ", phone)
    digits = re.sub(r"\D", "", phone)
    if len(digits) < 7:
        return ND
    if re.search(r"[A-Za-z]", phone):
        return ND
    return phone


def parse_phone_numbers(value: Any, max_numbers: int = 4) -> list[str]:
    if is_missing(value):
        return [ND] * max_numbers
    text = str(value)
    candidates: list[str] = []
    for part in re.split(r"[,;\n|]+", text):
        part = part.strip()
        if not part:
            continue
        match = PHONE_RE.search(part)
        candidates.append(_normalize_phone(match.group(0) if match else part))

    phones: list[str] = []
    seen: set[str] = set()
    for candidate in candidates:
        if candidate == ND:
            if len(phones) < max_numbers:
                phones.append(ND)
            continue
        key = re.sub(r"\D", "", candidate)
        if key in seen:
            continue
        seen.add(key)
        phones.append(candidate)
        if len(phones) == max_numbers:
            break

    while len(phones) < max_numbers:
        phones.append(ND)
    return phones[:max_numbers]


def parse_persons(value: Any, max_people: int = 4) -> list[dict[str, str]]:
    if is_missing(value):
        people: list[dict[str, str]] = []
    else:
        try:
            parsed = ast.literal_eval(str(value))
        except (SyntaxError, ValueError):
            parsed = []
        people = parsed if isinstance(parsed, list) else []

    normalized: list[dict[str, str]] = []
    for person in people:
        if not isinstance(person, dict):
            continue
        name = clean_text(person.get("name"))
        role = clean_text(person.get("role"))
        if name == ND and role == ND:
            continue
        normalized.append({"name": name, "role": role})

    def is_president(role: str) -> bool:
        folded = role.casefold()
        return bool(re.search(r"(?<!vice[-\s])pr[ée]sident|(?<!vice[-\s])president", folded))

    def is_secondary_priority(role: str) -> bool:
        folded = role.casefold()
        return (
            "directeur" in folded
            or "director" in folded
            or "vice-président" in folded
            or "vice-president" in folded
            or "vice président" in folded
            or "vice president" in folded
        )

    presidents = [p for p in normalized if is_president(p["role"])]
    directors = [p for p in normalized if p not in presidents and is_secondary_priority(p["role"])]
    others = [p for p in normalized if p not in presidents and p not in directors]
    slots = [{"name": ND, "role": ND} for _ in range(max_people)]
    if presidents:
        slots[0] = presidents[0]
    if max_people > 1 and directors:
        slots[1] = directors[0]

    remaining = others + presidents[1:] + directors[1:]
    for person in remaining:
        for index, slot in enumerate(slots):
            if slot["name"] == ND and slot["role"] == ND:
                if index == 0 and directors and not presidents:
                    continue
                slots[index] = person
                break
    return slots


def read_table(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix in {".xlsx", ".xlsm", ".xls"}:
        return pd.read_excel(path, dtype=str)
    if suffix == ".csv":
        return pd.read_csv(path, sep=None, engine="python", dtype=str, encoding="utf-8-sig")
    raise ValueError(f"Unsupported input file type: {path.suffix}")


def write_outputs(df: pd.DataFrame, output_dir: Path, stem: str, version: str) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    xlsx_path = output_dir / f"{stem}_{version}.xlsx"
    csv_path = output_dir / f"{stem}_{version}.csv"
    df.to_excel(xlsx_path, index=False)
    df.to_csv(csv_path, index=False, sep=";", encoding="utf-8")
    return xlsx_path, csv_path


def finalize_nd(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    for column in result.columns:
        result[column] = result[column].map(normalize_nd)
    return result
