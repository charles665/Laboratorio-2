from __future__ import annotations

from typing import Any

import pandas as pd


def _basic_profile(df: pd.DataFrame) -> dict[str, Any]:
    return {
        "rows": len(df),
        "columns": list(df.columns),
        "missing_values": df.isna().sum().to_dict(),
        "duplicate_rows": int(df.duplicated().sum()),
        "duplicate_keys": {},
    }


def _duplicate_keys(df: pd.DataFrame, key: str) -> int:
    if key not in df:
        return 0
    return int(df[key].duplicated(keep=False).sum())


def profile_data(
    sales: pd.DataFrame,
    references: dict[str, pd.DataFrame],
) -> dict[str, Any]:
    """Returns data-quality findings without changing the source DataFrames."""
    profiles = {"sales": _basic_profile(sales)}
    for name, frame in references.items():
        profiles[name] = _basic_profile(frame)

    key_by_table = {
        "sales": "sale_line_id",
        "products": "product_id",
        "stores": "store_id",
        "channels": "channel_id",
        "promotions": "promotion_id",
    }
    for name, key in key_by_table.items():
        if name in profiles:
            frame = sales if name == "sales" else references[name]
            profiles[name]["duplicate_keys"] = {key: _duplicate_keys(frame, key)}

    findings: dict[str, Any] = {
        "invalid_references": {},
        "domain_violations": {},
        "cross_field_inconsistencies": {},
    }
    reference_keys = {
        name: set(frame[key].dropna())
        for name, frame in references.items()
        for key in [key_by_table.get(name)]
        if key and key in frame
    }
    foreign_keys = {
        "product_id": "products",
        "store_id": "stores",
        "channel_id": "channels",
        "promotion_id": "promotions",
    }
    for column, table in foreign_keys.items():
        if column in sales and column in reference_keys:
            invalid = sales.loc[~sales[column].isin(reference_keys[table]), column]
            findings["invalid_references"][column] = sorted(invalid.dropna().unique().tolist())

    if "quantity" in sales:
        findings["domain_violations"]["quantity_non_positive"] = int((sales["quantity"] <= 0).sum())
    if "unit_price_sale" in sales:
        findings["domain_violations"]["unit_price_sale_non_positive"] = int((sales["unit_price_sale"] <= 0).sum())

    if {"store_id", "channel_id"}.issubset(sales.columns):
        store_channels = references["stores"].set_index("store_id")["channel_id"]
        expected = sales["store_id"].map(store_channels)
        findings["cross_field_inconsistencies"]["store_channel_mismatch"] = int(
            (expected.notna() & (expected != sales["channel_id"])).sum()
        )

    return {"tables": profiles, "findings": findings}