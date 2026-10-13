from io import BytesIO

import pandas as pd
import pytest
from openpyxl import load_workbook

from processor import (
    export_report,
    process_orders,
    process_orders_with_quality,
    read_orders,
    suggest_column_mapping,
)


def make_csv(rows: list[dict], name: str = "orders.csv") -> BytesIO:
    file = BytesIO(pd.DataFrame(rows).to_csv(index=False).encode("utf-8"))
    file.name = name
    return file


def make_xlsx(rows: list[dict], name: str = "orders.xlsx") -> BytesIO:
    file = BytesIO()
    pd.DataFrame(rows).to_excel(file, index=False, engine="openpyxl")
    file.name = name
    file.seek(0)
    return file


def test_sample_files_reach_expected_milestone() -> None:
    cleaned, daily, products, stats = process_orders(
        ["sample_data/orders_1.csv", "sample_data/orders_2.csv"]
    )
    assert stats["original_rows"] == 8
    assert stats["cleaned_rows"] == 7
    assert stats["duplicates"] == 1
    assert stats["invalid_rows"] == 0
    assert stats["total_orders"] == 7
    assert stats["total_sales"] == pytest.approx(584.00)
    assert len(daily) == 4
    assert list(products["sku"]) == ["P001", "P002", "P003"]
    assert cleaned["order_id"].tolist().count("ORD003") == 1


def test_invalid_rows_are_excluded() -> None:
    rows = [
        {"order_id": "1", "date": "2026-10-01", "product": "A", "sku": "A1", "quantity": 2, "unit_price": 10},
        {"order_id": "2", "date": "bad", "product": "B", "sku": "B1", "quantity": 1, "unit_price": 20},
        {"order_id": "3", "date": "2026-10-01", "product": "C", "sku": "C1", "quantity": 0, "unit_price": 20},
    ]
    cleaned, _, _, stats = process_orders([make_csv(rows)])
    assert len(cleaned) == 1
    assert stats["invalid_rows"] == 2
    assert stats["total_sales"] == pytest.approx(20)


def test_missing_columns_raise_clear_error() -> None:
    with pytest.raises(ValueError, match=r"missing columns:.*unit_price"):
        read_orders(make_csv([{"order_id": "1"}]))


def test_export_contains_expected_sheets() -> None:
    cleaned, daily, products, _ = process_orders(["sample_data/orders_1.csv"])
    workbook = export_report(cleaned, daily, products)
    assert workbook.startswith(b"PK")
    excel = pd.ExcelFile(BytesIO(workbook), engine="openpyxl")
    assert excel.sheet_names == ["Cleaned Orders", "Daily Sales", "Product Ranking"]


def test_at_least_one_file_is_required() -> None:
    with pytest.raises(ValueError, match="at least one"):
        process_orders([])


def test_xlsx_input_is_supported() -> None:
    rows = [
        {"order_id": "001", "date": "2026-10-01", "product": "A", "sku": "A1", "quantity": 2, "unit_price": 12.5}
    ]
    cleaned, _, _, stats = process_orders([make_xlsx(rows)])
    assert cleaned.loc[0, "order_id"] == "001"
    assert stats["total_sales"] == pytest.approx(25)


def test_column_names_are_normalized_and_ids_keep_leading_zeroes() -> None:
    content = (
        " Order ID ,Date,Product,SKU,Quantity,Unit-Price\n"
        "001,2026-10-01,Phone Stand,P001,2,10\n"
    )
    file = BytesIO(content.encode("utf-8"))
    file.name = "messy_headers.csv"
    cleaned, _, _, _ = process_orders([file])
    assert cleaned.loc[0, "order_id"] == "001"
    assert cleaned.loc[0, "sales"] == pytest.approx(20)


def test_empty_and_unsupported_files_raise_clear_errors() -> None:
    empty = BytesIO(b"")
    empty.name = "empty.csv"
    with pytest.raises(ValueError, match="file is empty"):
        read_orders(empty)

    unsupported = BytesIO(b"anything")
    unsupported.name = "orders.txt"
    with pytest.raises(ValueError, match="only CSV and XLSX"):
        read_orders(unsupported)


def test_headers_that_normalize_to_duplicates_are_rejected() -> None:
    content = (
        "order_id,Order ID,date,product,sku,quantity,unit_price\n"
        "1,1,2026-10-01,A,A1,1,10\n"
    )
    file = BytesIO(content.encode("utf-8"))
    file.name = "duplicate_headers.csv"
    with pytest.raises(ValueError, match="duplicate columns: order_id"):
        read_orders(file)


def test_all_invalid_rows_do_not_crash_summaries() -> None:
    rows = [
        {"order_id": "1", "date": "invalid", "product": "A", "sku": "A1", "quantity": -1, "unit_price": 10}
    ]
    cleaned, daily, products, stats = process_orders([make_csv(rows)])
    assert cleaned.empty
    assert daily.empty
    assert products.empty
    assert stats["invalid_rows"] == 1
    assert stats["total_sales"] == 0


def test_exported_values_match_summaries() -> None:
    cleaned, daily, products, _ = process_orders(
        ["sample_data/orders_1.csv", "sample_data/orders_2.csv"]
    )
    workbook = export_report(cleaned, daily, products)
    exported_orders = pd.read_excel(BytesIO(workbook), sheet_name="Cleaned Orders")
    exported_daily = pd.read_excel(BytesIO(workbook), sheet_name="Daily Sales")
    exported_products = pd.read_excel(BytesIO(workbook), sheet_name="Product Ranking")
    assert len(exported_orders) == 7
    assert exported_orders["sales"].sum() == pytest.approx(584)
    assert exported_daily["sales"].sum() == pytest.approx(584)
    assert exported_products["sales"].sum() == pytest.approx(584)


def test_export_neutralizes_excel_formula_text() -> None:
    rows = [
        {"order_id": "1", "date": "2026-10-01", "product": "=2+2", "sku": "@TEST", "quantity": 1, "unit_price": 10}
    ]
    cleaned, daily, products, _ = process_orders([make_csv(rows)])
    workbook = export_report(cleaned, daily, products)
    sheet = load_workbook(BytesIO(workbook), data_only=False)["Cleaned Orders"]
    assert sheet["C2"].data_type == "s"
    assert sheet["C2"].value == "'=2+2"
    assert sheet["D2"].data_type == "s"
    assert sheet["D2"].value == "'@TEST"


def test_chinese_headers_are_mapped_automatically() -> None:
    rows = [
        {"订单编号": "CN001", "下单日期": "2026-10-01", "商品名称": "支架", "货号": "A1", "数量": 2, "单价": 19.9}
    ]
    cleaned, _, _, stats = process_orders([make_csv(rows)])
    assert cleaned.loc[0, "order_id"] == "CN001"
    assert cleaned.loc[0, "sku"] == "A1"
    assert stats["total_sales"] == pytest.approx(39.8)


def test_explicit_column_mapping_supports_custom_headers() -> None:
    rows = [
        {"编号": "X01", "时间": "2026-10-01", "名称": "A", "编码": "SKU1", "销量": 3, "金额": 12}
    ]
    mapping = {
        "order_id": "编号",
        "date": "时间",
        "product": "名称",
        "sku": "编码",
        "quantity": "销量",
        "unit_price": "金额",
    }
    cleaned, _, _, stats = process_orders([make_csv(rows)], column_mapping=mapping)
    assert cleaned.loc[0, "order_id"] == "X01"
    assert stats["total_sales"] == pytest.approx(36)


def test_custom_deduplication_fields_are_applied() -> None:
    rows = [
        {"order_id": "1", "date": "2026-10-01", "product": "A", "sku": "A1", "quantity": 1, "unit_price": 10},
        {"order_id": "1", "date": "2026-10-01", "product": "B", "sku": "B1", "quantity": 1, "unit_price": 20},
    ]
    result = process_orders_with_quality([make_csv(rows)], dedupe_columns=["order_id"])
    assert len(result.cleaned) == 1
    assert result.stats["duplicates"] == 1
    assert result.rejected.loc[0, "rejection_reason"] == "duplicate by order_id"


def test_quality_report_retains_invalid_and_duplicate_rows() -> None:
    rows = [
        {"order_id": "1", "date": "2026-10-01", "product": "A", "sku": "A1", "quantity": 1, "unit_price": 10},
        {"order_id": "1", "date": "2026-10-01", "product": "A", "sku": "A1", "quantity": 1, "unit_price": 10},
        {"order_id": "2", "date": "bad", "product": "B", "sku": "B1", "quantity": 0, "unit_price": 20},
    ]
    result = process_orders_with_quality([make_csv(rows)])
    assert result.stats["rejected_rows"] == 2
    assert set(result.rejected["rejection_reason"].str.contains("duplicate")) == {False, True}

    workbook = export_report(result.cleaned, result.daily, result.products, result.rejected)
    excel = pd.ExcelFile(BytesIO(workbook), engine="openpyxl")
    assert excel.sheet_names == ["Cleaned Orders", "Daily Sales", "Product Ranking", "Rejected Rows"]


def test_mapping_suggestions_recognize_mixed_language_headers() -> None:
    suggestions = suggest_column_mapping(["订单号", "order date", "Product Name", "SKU", "件数", "售价"])
    assert suggestions == {
        "order_id": "订单号",
        "date": "order_date",
        "product": "product_name",
        "sku": "sku",
        "quantity": "件数",
        "unit_price": "售价",
    }
