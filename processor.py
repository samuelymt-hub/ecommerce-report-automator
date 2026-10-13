"""Read, clean, summarize, and export e-commerce order data."""

from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import BinaryIO, Iterable, Mapping, Sequence

import pandas as pd

REQUIRED_COLUMNS = ("order_id", "date", "product", "sku", "quantity", "unit_price")
TEXT_COLUMNS = ("order_id", "product", "sku")
SUPPORTED_EXTENSIONS = {".csv", ".xlsx"}
DEFAULT_DEDUPE_COLUMNS = ("order_id", "sku")

COLUMN_ALIASES: dict[str, tuple[str, ...]] = {
    "order_id": ("order_id", "orderid", "order_no", "order_number", "订单号", "订单编号", "订单id"),
    "date": ("date", "order_date", "created_at", "下单日期", "订单日期", "日期", "创建时间"),
    "product": ("product", "product_name", "item", "item_name", "商品", "商品名称", "产品", "产品名称"),
    "sku": ("sku", "product_sku", "item_sku", "sku_code", "商品sku", "sku编码", "货号"),
    "quantity": ("quantity", "qty", "units", "数量", "件数", "购买数量", "销售数量"),
    "unit_price": ("unit_price", "price", "sale_price", "售价", "单价", "商品单价", "销售单价"),
}


@dataclass(frozen=True)
class ProcessingResult:
    """Complete processing output, including rows excluded by quality rules."""

    cleaned: pd.DataFrame
    daily: pd.DataFrame
    products: pd.DataFrame
    rejected: pd.DataFrame
    stats: dict[str, int | float]


def normalize_column_name(value: object) -> str:
    """Normalize a source header while preserving non-Latin characters."""
    return (
        pd.Series([str(value)])
        .str.strip()
        .str.lower()
        .str.replace(r"[\s-]+", "_", regex=True)
        .iloc[0]
    )


def _file_name(file: BinaryIO | str | Path) -> str:
    if isinstance(file, (str, Path)):
        return Path(file).name
    name = getattr(file, "name", None)
    if not name:
        raise ValueError("Each uploaded file must have a file name.")
    return Path(str(name)).name


def _read_frame(file: BinaryIO | str | Path) -> pd.DataFrame:
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

    frame.columns = [normalize_column_name(column) for column in frame.columns]
    if frame.columns.duplicated().any():
        duplicates = sorted(set(frame.columns[frame.columns.duplicated()]))
        raise ValueError(f"{name}: duplicate columns: {', '.join(duplicates)}.")
    return frame


def inspect_order_columns(file: BinaryIO | str | Path) -> tuple[str, ...]:
    """Return normalized headers for a source file without applying a schema."""
    return tuple(_read_frame(file).columns)


def suggest_column_mapping(columns: Sequence[object]) -> dict[str, str | None]:
    """Suggest canonical-to-source mappings using common Chinese and English aliases."""
    available = [normalize_column_name(column) for column in columns]
    suggestions: dict[str, str | None] = {}
    for canonical in REQUIRED_COLUMNS:
        aliases = {normalize_column_name(alias) for alias in COLUMN_ALIASES[canonical]}
        suggestions[canonical] = next((column for column in available if column in aliases), None)
    return suggestions


def read_orders(
    file: BinaryIO | str | Path,
    column_mapping: Mapping[str, str | None] | None = None,
) -> pd.DataFrame:
    """Read one CSV/XLSX file, apply field aliases/mapping, and validate its schema."""
    name = _file_name(file)
    frame = _read_frame(file)
    suggestions = suggest_column_mapping(frame.columns)

    if column_mapping:
        for canonical, source in column_mapping.items():
            if canonical not in REQUIRED_COLUMNS or not source:
                continue
            normalized_source = normalize_column_name(source)
            if normalized_source in frame.columns:
                suggestions[canonical] = normalized_source

    selected_sources = [source for source in suggestions.values() if source]
    duplicates = sorted({source for source in selected_sources if selected_sources.count(source) > 1})
    if duplicates:
        raise ValueError(f"{name}: one source column cannot map to multiple fields: {', '.join(duplicates)}.")

    rename_map = {source: canonical for canonical, source in suggestions.items() if source}
    mapped = frame.rename(columns=rename_map)
    missing = sorted(set(REQUIRED_COLUMNS) - set(mapped.columns))
    if missing:
        raise ValueError(f"{name}: missing columns: {', '.join(missing)}.")
    return mapped.loc[:, REQUIRED_COLUMNS].copy()


def _append_reason(reasons: pd.Series, mask: pd.Series, message: str) -> None:
    reasons.loc[mask] = reasons.loc[mask].map(
        lambda current: f"{current}; {message}" if current else message
    )


def process_orders_with_quality(
    files: Iterable[BinaryIO | str | Path],
    column_mapping: Mapping[str, str | None] | None = None,
    dedupe_columns: Sequence[str] = DEFAULT_DEDUPE_COLUMNS,
) -> ProcessingResult:
    """Combine files, clean rows, retain rejected rows, and build summaries."""
    file_list = list(files)
    if not file_list:
        raise ValueError("Upload at least one CSV or XLSX file.")

    dedupe_fields = tuple(dict.fromkeys(dedupe_columns))
    if not dedupe_fields:
        raise ValueError("Select at least one deduplication field.")
    unsupported_dedupe = sorted(set(dedupe_fields) - set(REQUIRED_COLUMNS))
    if unsupported_dedupe:
        raise ValueError(f"Unsupported deduplication fields: {', '.join(unsupported_dedupe)}.")

    frames: list[pd.DataFrame] = []
    for file in file_list:
        frame = read_orders(file, column_mapping=column_mapping)
        frame.insert(0, "source_file", _file_name(file))
        frames.append(frame)
    combined = pd.concat(frames, ignore_index=True)
    raw = combined.copy()
    original_rows = len(combined)

    for column in TEXT_COLUMNS:
        combined[column] = combined[column].astype("string").str.strip().replace("", pd.NA)
    combined["date"] = pd.to_datetime(combined["date"], errors="coerce").dt.normalize()
    combined["quantity"] = pd.to_numeric(combined["quantity"], errors="coerce")
    combined["unit_price"] = pd.to_numeric(combined["unit_price"], errors="coerce")

    reasons = pd.Series("", index=combined.index, dtype="string")
    for column in TEXT_COLUMNS:
        _append_reason(reasons, combined[column].isna(), f"missing {column}")
    _append_reason(reasons, combined["date"].isna(), "invalid date")
    _append_reason(reasons, combined["quantity"].isna(), "invalid quantity")
    _append_reason(
        reasons,
        combined["quantity"].notna() & (combined["quantity"] <= 0),
        "quantity must be greater than 0",
    )
    _append_reason(reasons, combined["unit_price"].isna(), "invalid unit_price")
    _append_reason(
        reasons,
        combined["unit_price"].notna() & (combined["unit_price"] < 0),
        "unit_price cannot be negative",
    )

    invalid_mask = reasons.ne("")
    invalid_rows = int(invalid_mask.sum())
    rejected_invalid = raw.loc[invalid_mask].copy()
    rejected_invalid["rejection_reason"] = reasons.loc[invalid_mask].values

    valid = combined.loc[~invalid_mask].copy()
    duplicate_mask = valid.duplicated(subset=list(dedupe_fields), keep="first")
    duplicate_rows = int(duplicate_mask.sum())
    rejected_duplicates = raw.loc[valid.index[duplicate_mask]].copy()
    rejected_duplicates["rejection_reason"] = f"duplicate by {' + '.join(dedupe_fields)}"

    rejected = pd.concat([rejected_invalid, rejected_duplicates], ignore_index=True)
    rejected = rejected.loc[:, ["source_file", *REQUIRED_COLUMNS, "rejection_reason"]]

    cleaned = valid.loc[~duplicate_mask, REQUIRED_COLUMNS].copy()
    cleaned["sales"] = cleaned["quantity"] * cleaned["unit_price"]
    cleaned = cleaned.sort_values(["date", "order_id", "sku"], kind="stable").reset_index(drop=True)
    daily = (
        cleaned.groupby("date", as_index=False)
        .agg(order_count=("order_id", "nunique"), units_sold=("quantity", "sum"), sales=("sales", "sum"))
        .sort_values("date")
        .reset_index(drop=True)
    )
    products = (
        cleaned.groupby(["sku", "product"], as_index=False)
        .agg(order_count=("order_id", "nunique"), units_sold=("quantity", "sum"), sales=("sales", "sum"))
        .sort_values(["sales", "units_sold"], ascending=False, kind="stable")
        .reset_index(drop=True)
    )
    stats: dict[str, int | float] = {
        "original_rows": original_rows,
        "cleaned_rows": len(cleaned),
        "invalid_rows": invalid_rows,
        "duplicates": duplicate_rows,
        "rejected_rows": len(rejected),
        "total_orders": int(cleaned["order_id"].nunique()),
        "total_units": float(cleaned["quantity"].sum()),
        "total_sales": float(cleaned["sales"].sum()),
    }
    return ProcessingResult(cleaned, daily, products, rejected, stats)


def process_orders(
    files: Iterable[BinaryIO | str | Path],
    column_mapping: Mapping[str, str | None] | None = None,
    dedupe_columns: Sequence[str] = DEFAULT_DEDUPE_COLUMNS,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, int | float]]:
    """Backward-compatible processing API returning the original four values."""
    result = process_orders_with_quality(files, column_mapping, dedupe_columns)
    return result.cleaned, result.daily, result.products, result.stats


def export_report(
    cleaned: pd.DataFrame,
    daily: pd.DataFrame,
    products: pd.DataFrame,
    rejected: pd.DataFrame | None = None,
) -> bytes:
    """Create an Excel workbook containing report and optional quality sheets."""
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
        if rejected is not None:
            make_excel_safe(rejected).to_excel(writer, sheet_name="Rejected Rows", index=False)
        for sheet in writer.book.worksheets:
            sheet.freeze_panes = "A2"
            sheet.auto_filter.ref = sheet.dimensions
            for cells in sheet.columns:
                width = min(max(len(str(cell.value or "")) for cell in cells) + 2, 40)
                sheet.column_dimensions[cells[0].column_letter].width = width
    return output.getvalue()
