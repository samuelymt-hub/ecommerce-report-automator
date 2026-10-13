from processor import REQUIRED_COLUMNS


def test_required_columns_are_defined() -> None:
    assert REQUIRED_COLUMNS == (
        "order_id",
        "date",
        "product",
        "sku",
        "quantity",
        "unit_price",
    )

