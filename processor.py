"""Read, clean, summarize, and export e-commerce order data."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import BinaryIO, Iterable

import pandas as pd

REQUIRED_COLUMNS = ("order_id", "date", "product", "sku", "quantity", "unit_price")
TEXT_COLUMNS = ("order_id", "product", "sku")
SUPPORTED_EXTENSIONS = {".csv", ".xlsx"}


def _file_name(file: BinaryIO | str | Path) -> str:
    if isinstance(file, (str, Path)):
        return Path(file).name
    name = getattr(file, "name", None)
    if not name:
        raise ValueError("Each uploaded file must have a file name.")
    return Path(str(name)).name


def read_orders(file: BinaryIO | str | Path) -> pd.DataFrame:
    """Read one CSV/XLSX file and validate its required columns."""
    name = _file_name(file)
    extension = Path(name).suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"{name}: only CSV and XLSX files are supported.")
    if hasattr(file, "seek"):
        file.seek(0)
    try:
        if extension == ".csv":
            frame = pd.read_csv(file, dtype="string")
        else:
            frame = pd.read_excel(file, engine="openpyxl", dtype="string")
    except pd.errors.EmptyDataError as exc:
        raise ValueError(f"{name}: the file is empty.") from exc
    except Exception as exc:
        raise ValueError(f"{name}: could not read the file ({exc}).") from exc

    frame.columns = (frame.columns.astype(str).str.strip().str.lower().str.replace(r"[\s-]+", "_", regex=True))
    if frame.columns.duplicated().any():
        duplicates = sorted(set(frame.columns[frame.columns.duplicated()]))
        raise ValueError(f"{name}: duplicate columns: {', '.join(duplicates)}.")
    missing = sorted(set(REQUIRED_COLUMNS) - set(frame.columns))
    if missing:
        raise ValueError(f"{name}: missing columns: {', '.join(missing)}.")
    return frame.loc[:, REQUIRED_COLUMNS].copy()


def process_orders(files: Iterable[BinaryIO | str | Path]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, int | float]]:
    """Combine files, clean rows, remove duplicates, and build summaries."""
    file_list = list(files)
    if not file_list:
        raise ValueError("Upload at least one CSV or XLSX file.")
    combined = pd.concat([read_orders(file) for file in file_list], ignore_index=True)
    original_rows = len(combined)
    for column in TEXT_COLUMNS:
        combined[column] = combined[column].astype("string").str.strip().replace("", pd.NA)
    combined["date"] = pd.to_datetime(combined["date"], errors="coerce").dt.normalize()
    combined["quantity"] = pd.to_numeric(combined["quantity"], errors="coerce")
    combined["unit_price"] = pd.to_numeric(combined["unit_price"], errors="coerce")
    invalid_mask = (
        combined[[*TEXT_COLUMNS, "date", "quantity", "unit_price"]].isna().any(axis=1)
        | (combined["quantity"] <= 0)
        | (combined["unit_price"] < 0)
    )
    invalid_rows = int(invalid_mask.sum())
    valid = combined.loc[~invalid_mask].copy()
    duplicate_mask = valid.duplicated(subset=["order_id", "sku"], keep="first")
    duplicates = int(duplicate_mask.sum())
    cleaned = valid.loc[~duplicate_mask].copy()
    cleaned["sales"] = cleaned["quantity"] * cleaned["unit_price"]
    cleaned = cleaned.sort_values(["date", "order_id", "sku"], kind="stable").reset_index(drop=True)
    daily = (
        cleaned.groupby("date", as_index=False)
        .agg(order_count=("order_id", "nunique"), units_sold=("quantity", "sum"), sales=("sales", "sum"))
        .sort_values("date").reset_index(drop=True)
    )
    products = (
        cleaned.groupby(["sku", "product"], as_index=False)
        .agg(order_count=("order_id", "nunique"), units_sold=("quantity", "sum"), sales=("sales", "sum"))
        .sort_values(["sales", "units_sold"], ascending=False, kind="stable").reset_index(drop=True)
    )
    stats: dict[str, int | float] = {
        "original_rows": original_rows,
        "cleaned_rows": len(cleaned),
        "invalid_rows": invalid_rows,
        "duplicates": duplicates,
        "total_orders": int(cleaned["order_id"].nunique()),
        "total_units": float(cleaned["quantity"].sum()),
        "total_sales": float(cleaned["sales"].sum()),
    }
    return cleaned, daily, products, stats


def export_report(cleaned: pd.DataFrame, daily: pd.DataFrame, products: pd.DataFrame) -> bytes:
    """Create an Excel workbook containing the three MVP report sheets."""
    def make_excel_safe(frame: pd.DataFrame) -> pd.DataFrame:
        safe = frame.copy()
        for column in safe.select_dtypes(include=["object", "string"]).columns:
            safe[column] = safe[column].map(
                lambda value: f"'{value}"
                if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@"))
                else value
            )
        return safe

    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl", datetime_format="yyyy-mm-dd") as writer:
        make_excel_safe(cleaned).to_excel(writer, sheet_name="Cleaned Orders", index=False)
        make_excel_safe(daily).to_excel(writer, sheet_name="Daily Sales", index=False)
        make_excel_safe(products).to_excel(writer, sheet_name="Product Ranking", index=False)
        for sheet in writer.book.worksheets:
            sheet.freeze_panes = "A2"
            sheet.auto_filter.ref = sheet.dimensions
            for cells in sheet.columns:
                width = min(max(len(str(cell.value or "")) for cell in cells) + 2, 40)
                sheet.column_dimensions[cells[0].column_letter].width = width
    return output.getvalue()
