from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from utils import ND, clean_sector, finalize_nd, normalize_boolean, parse_persons, parse_phone_numbers, read_table, write_outputs


DROP_COLUMNS = [
    "description",
    "average_rating",
    "hours_monday",
    "hours_tuesday",
    "hours_wednesday",
    "hours_thursday",
    "hours_friday",
    "hours_saturday",
    "hours_sunday",
    "credibility_score",
    "languages",
    "forms_of_contact",
    "location_attributes",
    "categories",
    "on_architectes_ch",
    "on_bienvivre_ch",
    "status",
    "user_notes",
]

RENAME_COLUMNS = {
    "keyword": "Secteur d’activité",
    "title": "Affaire",
    "street": "Rue",
    "zipcode": "Code postal",
    "city": "Ville",
    "picture_count": "Nombre de photos",
    "review_count": "Nombre d’avis",
    "copyright_year": "Année de création du site",
    "has_local_search": "Site Mywebsite",
    "zip": "Annuaire Zip",
}

BOOLEAN_COLUMNS = ["Site Mywebsite", "Annuaire Zip", "has_social_media"]

V3_MAPPING = [
    ("Affaire - Titre de l’affaire - CD", "Affaire"),
    ("Affaire Étiquette - CD", "TOP"),
    ("Affaire Etape - CD", "Prospects"),
    ("Affaire Téléphone 1 - CP", "Téléphone 1"),
    ("Affaire Responsable 1 - CP", "Responsable 1"),
    ("Affaire – Fonction responsable 1 - CP", "Fonction 1"),
    ("Affaire - Responsable 2 - CP", "Responsable 2"),
    ("Affaire - Fonction responsable 2 - CP", "Fonction 2"),
    ("Organisation - Propriétaire – utilisateur - CD", "Fabien"),
    ("Organisation - CD", "Affaire"),
    ("Organisation - Adresse complète - CD", "__address__"),
    ("Organisation – Rue - CD", "Rue"),
    ("Organisation - Code postal - CD", "Code postal"),
    ("Organisation – Ville - CD", "Ville"),
    ("Organisation - Téléphone 1 - CP", "Téléphone 1"),
    ("Organisation - Responsable 1 - CP", "Responsable 1"),
    ("Organisation - Fonction responsable 1 - CP", "Fonction 1"),
    ("Organisation - Responsable 2 - CP", "Responsable 2"),
    ("Organisation - Fonction responsable 2 - CP", "Fonction 2"),
    ("Organisation - Responsable 3 - CP", "Responsable 3"),
    ("Organisation – Fonction responsable 3 - CP", "Fonction 3"),
    ("Organisation - Responsable 4 - CP", "Responsable 4"),
    ("Organisation – Fonction responsable 4 - CP", "Fonction 4"),
    ("Organisation - url inscription Local - CP", "url"),
    ("Organisation - Secteur d'activité - CP", "Secteur d’activité"),
    ("Organisation - Téléphone 2 - CP", "Téléphone 2"),
    ("Organisation - Téléphone 3 - CP", "Téléphone 3"),
    ("Organisation - Téléphone 4 - CP", "Téléphone 4"),
    ("Organisation - email - email société - CP", "email"),
    ("Organisation – website - CP", "website"),
    ("Organisation - Site Mywebsite - CP", "Site Mywebsite"),
    ("Organisation - Copyright du site - CP", "Année de création du site"),
    ("Organisation - Nombre de photos - CP", "Nombre de photos"),
    ("Organisation - Nombre d'avis - CP", "Nombre d’avis"),
    ("Organisation – Zip - CP", "Annuaire Zip"),
    ("Organisation - has_social_media - CP", "has_social_media"),
    ("Organisation - facebook_url - CP", "facebook_url"),
    ("Organisation - instagram_url - CP", "instagram_url"),
    ("Organisation - linkedin_url - CP", "linkedin_url"),
    ("Organisation - twitter_url - CP", "twitter_url"),
    ("Organisation - youtube_url - CP", "youtube_url"),
    ("Personne – email - CD", "email"),
    ("Personne - Responsable 1 _ CD", "Responsable 1"),
    ("Personne - Téléphone 1 - CD", "Téléphone 1"),
    ("Personne - Téléphone 2 - CP", "Téléphone 2"),
    ("Personne - Responsable 1 - CP", "Responsable 1"),
    ("Personne - Fonction responsable 1 - CP", "Fonction 1"),
    ("Personne - Responsable 2 - CP", "Responsable 2"),
    ("Personne – Fonction responsable 2 - CP", "Fonction 2"),
    ("Personne - Responsable 3 - CP", "Responsable 3"),
    ("Personne - Fonction responsable 3 - CP", "Fonction 3"),
    ("Personne - Responsable 4 -CP", "Responsable 4"),
    ("Personne - Fonction responsable 4 - CP", "Fonction 4"),
]


def create_v2(raw: pd.DataFrame) -> pd.DataFrame:
    df = raw.copy()
    df = df.drop(columns=[column for column in DROP_COLUMNS if column in df.columns])
    df = df.rename(columns={old: new for old, new in RENAME_COLUMNS.items() if old in df.columns})

    if "Secteur d’activité" in df.columns:
        df["Secteur d’activité"] = df["Secteur d’activité"].map(clean_sector)

    people_rows = df["persons"].map(parse_persons) if "persons" in df.columns else pd.Series([[{"name": ND, "role": ND}] * 4] * len(df))
    for index in range(4):
        df[f"Responsable {index + 1}"] = people_rows.map(lambda people, i=index: people[i]["name"])
        df[f"Fonction {index + 1}"] = people_rows.map(lambda people, i=index: people[i]["role"])
    if "persons" in df.columns:
        df = df.drop(columns=["persons"])

    phone_rows = df["phone_numbers"].map(parse_phone_numbers) if "phone_numbers" in df.columns else pd.Series([[ND] * 4] * len(df))
    for index in range(4):
        df[f"Téléphone {index + 1}"] = phone_rows.map(lambda phones, i=index: phones[i])
    if "phone_numbers" in df.columns:
        df = df.drop(columns=["phone_numbers"])

    for column in BOOLEAN_COLUMNS:
        if column in df.columns:
            df[column] = df[column].map(normalize_boolean)

    return finalize_nd(df)


def combine_address(v2: pd.DataFrame) -> pd.Series:
    parts = []
    for column in ["Rue", "Code postal", "Ville"]:
        if column in v2.columns:
            parts.append(v2[column].replace(ND, ""))
        else:
            parts.append(pd.Series([""] * len(v2), index=v2.index))
    address = (parts[0].str.strip() + " " + parts[1].str.strip() + " " + parts[2].str.strip()).str.replace(r"\s+", " ", regex=True).str.strip()
    return address.mask(address == "", ND)


def create_v3(v2: pd.DataFrame) -> pd.DataFrame:
    data: dict[str, pd.Series | str] = {}
    address = combine_address(v2)
    for target, source in V3_MAPPING:
        if source in {"TOP", "Prospects", "Fabien"}:
            data[target] = source
        elif source == "__address__":
            data[target] = address
        elif source in v2.columns:
            data[target] = v2[source]
        else:
            data[target] = ND

    v3 = pd.DataFrame(data, index=v2.index)
    for column in [
        "Organisation - Site Mywebsite - CP",
        "Organisation – Zip - CP",
        "Organisation - has_social_media - CP",
    ]:
        v3[column] = v3[column].map(normalize_boolean)
    return finalize_nd(v3)


def transform(input_path: Path, output_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame, tuple[Path, Path], tuple[Path, Path]]:
    raw = read_table(input_path)
    v2 = create_v2(raw)
    v3 = create_v3(v2)
    v2_paths = write_outputs(v2, output_dir, input_path.stem, "V2")
    v3_paths = write_outputs(v3, output_dir, input_path.stem, "V3")
    return v2, v3, v2_paths, v3_paths


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Transform a local.ch scraper export into Pipedrive V2/V3 import files.")
    parser.add_argument("--input", required=True, type=Path, help="Raw scraper export CSV/XLSX path.")
    parser.add_argument("--output-dir", default=Path("output"), type=Path, help="Directory for generated files.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    v2, v3, v2_paths, v3_paths = transform(args.input, args.output_dir)
    print(f"V2 rows/columns: {v2.shape[0]}/{v2.shape[1]}")
    print(f"V3 rows/columns: {v3.shape[0]}/{v3.shape[1]}")
    print(f"Wrote: {v2_paths[0]}")
    print(f"Wrote: {v2_paths[1]}")
    print(f"Wrote: {v3_paths[0]}")
    print(f"Wrote: {v3_paths[1]}")


if __name__ == "__main__":
    main()
