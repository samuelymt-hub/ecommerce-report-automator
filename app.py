"""Streamlit interface for the E-commerce Report Automator."""

from pathlib import Path

import plotly.express as px
import streamlit as st

from processor import REQUIRED_COLUMNS, export_report, process_orders


st.set_page_config(
    page_title="E-commerce Report Automator",
    page_icon="📊",
    layout="wide",
)

st.title("📊 E-commerce Report Automator")
st.caption("上传订单文件，自动完成清洗、汇总分析并生成 Excel 报表。")

with st.sidebar:
    st.header("使用说明")
    st.markdown(
        "1. 上传一个或多个 CSV/XLSX 文件  \n"
        "2. 查看清洗结果与销售分析  \n"
        "3. 下载生成的 Excel 报表"
    )
    st.divider()
    st.subheader("必要字段")
    st.code(", ".join(REQUIRED_COLUMNS), language="text")
    st.caption("当前去重键：order_id + sku；币种：人民币。")

sample_path = Path(__file__).parent / "sample_data" / "orders_1.csv"
sample_paths = [
    Path(__file__).parent / "sample_data" / "orders_1.csv",
    Path(__file__).parent / "sample_data" / "orders_2.csv",
]
if sample_path.exists():
    st.download_button(
        "下载示例 CSV",
        data=sample_path.read_bytes(),
        file_name="sample_orders.csv",
        mime="text/csv",
    )

if st.button("使用内置示例数据", help="立即加载两份模拟订单，不会上传真实数据。"):
    st.session_state["demo_mode"] = True

if st.query_params.get("demo") == "true":
    st.session_state["demo_mode"] = True

uploaded_files = st.file_uploader(
    "上传订单文件",
    type=["csv", "xlsx"],
    accept_multiple_files=True,
    help="可以同时上传多个文件；所有文件必须包含相同的必要字段。",
)

files = sample_paths if st.session_state.get("demo_mode") else uploaded_files

if not files:
    st.info("请上传订单文件开始分析。你也可以先下载示例 CSV 查看数据格式。")
    st.stop()

try:
    orders, daily, products, stats = process_orders(files)
except ValueError as exc:
    st.error(f"处理失败：{exc}")
    st.stop()
except Exception:
    st.error("处理文件时发生未知错误，请检查文件格式后重试。")
    st.stop()

source_label = "内置示例" if st.session_state.get("demo_mode") else "上传"
st.success(f"已成功处理 {len(files)} 个{source_label}文件。")

metric_1, metric_2, metric_3, metric_4 = st.columns(4)
metric_1.metric("总销售额", f"¥{stats['total_sales']:,.2f}")
metric_2.metric("订单数", f"{stats['total_orders']:,}")
metric_3.metric("有效明细", f"{stats['cleaned_rows']:,}")
metric_4.metric("已清理记录", f"{stats['duplicates'] + stats['invalid_rows']:,}")

if stats["duplicates"] or stats["invalid_rows"]:
    st.caption(
        f"原始记录 {stats['original_rows']} 条；去除重复 {stats['duplicates']} 条；"
        f"排除无效数据 {stats['invalid_rows']} 条。"
    )

trend_tab, product_tab, detail_tab = st.tabs(["销售趋势", "商品排行", "订单明细"])

with trend_tab:
    trend_figure = px.line(
        daily,
        x="date",
        y="sales",
        markers=True,
        labels={"date": "日期", "sales": "销售额（¥）"},
        title="每日销售额",
    )
    trend_figure.update_layout(hovermode="x unified")
    st.plotly_chart(trend_figure, width="stretch")
    st.dataframe(
        daily,
        width="stretch",
        hide_index=True,
        column_config={
            "date": st.column_config.DateColumn("日期", format="YYYY-MM-DD"),
            "order_count": st.column_config.NumberColumn("订单数", format="%d"),
            "units_sold": st.column_config.NumberColumn("销售数量"),
            "sales": st.column_config.NumberColumn("销售额", format="¥ %.2f"),
        },
    )

with product_tab:
    product_figure = px.bar(
        products,
        x="product",
        y="sales",
        color="product",
        labels={"product": "商品", "sales": "销售额（¥）"},
        title="商品销售额排行",
    )
    product_figure.update_layout(showlegend=False)
    st.plotly_chart(product_figure, width="stretch")
    st.dataframe(
        products,
        width="stretch",
        hide_index=True,
        column_config={
            "sku": "SKU",
            "product": "商品",
            "order_count": st.column_config.NumberColumn("订单数", format="%d"),
            "units_sold": st.column_config.NumberColumn("销售数量"),
            "sales": st.column_config.NumberColumn("销售额", format="¥ %.2f"),
        },
    )

with detail_tab:
    st.dataframe(
        orders,
        width="stretch",
        hide_index=True,
        column_config={
            "order_id": "订单编号",
            "date": st.column_config.DateColumn("日期", format="YYYY-MM-DD"),
            "product": "商品",
            "sku": "SKU",
            "quantity": st.column_config.NumberColumn("数量"),
            "unit_price": st.column_config.NumberColumn("单价", format="¥ %.2f"),
            "sales": st.column_config.NumberColumn("销售额", format="¥ %.2f"),
        },
    )

report = export_report(orders, daily, products)
st.download_button(
    "下载 Excel 报表",
    data=report,
    file_name="ecommerce_sales_report.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    type="primary",
)
