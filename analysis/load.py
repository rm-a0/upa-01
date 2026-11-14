"""Load data.tsv into a typed DataFrame. Both notebooks start from this.

Columns:
    url, name                    str
    price                        float, EUR
    brand                        category
    colour, material             list[str], NaN when missing
    length_cm, weight_g, lumens  float, NaN when missing
    rechargeable, tactical, edc, bundle  bool, keyword found in the product name
"""

from pathlib import Path

import pandas as pd

DATA_TSV = Path(__file__).resolve().parent.parent / "data.tsv"

COLUMNS = [
    "url",
    "name",
    "price",
    "brand",
    "colour",
    "length_cm",
    "weight_g",
    "material",
    "lumens",
]
NUMERIC = ["price", "length_cm", "weight_g", "lumens"]
MULTI_VALUE = ["colour", "material"]
FLAGS = ["rechargeable", "tactical", "edc", "bundle"]

UNITS = {"length_cm": "cm", "weight_g": "g", "lumens": "lumens"}


def to_number(values: pd.Series, unit: str) -> pd.Series:
    """'1,500 g' -> 1500.0, '' -> NaN."""
    text = values.str.removesuffix(unit).str.replace(",", "").str.strip()
    return pd.to_numeric(text.mask(text == "")).astype(float)


def to_list(values: pd.Series) -> pd.Series:
    """'aluminum, carbon fiber' -> ['aluminum', 'carbon fiber'], '' -> NaN."""
    return values.map(lambda v: [p.strip() for p in v.split(",")] if v else None)


def load(path: Path = DATA_TSV) -> pd.DataFrame:
    """Read the raw TSV and return one typed row per product."""
    df = pd.read_csv(
        path, sep="\t", header=None, names=COLUMNS, dtype=str, keep_default_na=False
    )
    df["price"] = df["price"].astype(float)
    df["brand"] = df["brand"].astype("category")
    for column, unit in UNITS.items():
        df[column] = to_number(df[column], unit)
    for column in MULTI_VALUE:
        df[column] = to_list(df[column])

    name = df["name"].str.lower()
    df["rechargeable"] = name.str.contains("rechargeable")
    df["tactical"] = name.str.contains("tactical")
    df["edc"] = name.str.contains(r"\bedc")
    df["bundle"] = name.str.contains(
        r"\b(?:battery|kit|pack|holster|cable|attachments?)\b"
    )
    return df
