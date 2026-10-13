"""Streamlit interface for the E-commerce Report Automator."""

from pathlib import Path

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from processor import REQUIRED_COLUMNS, export_report, process_orders


st.set_page_config(
    page_title="Reportly · E-commerce Analytics",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    :root {
        --brand: #6c4ce8;
        --brand-dark: #4c2fc4;
        --brand-soft: #eee9ff;
        --ink: #171526;
        --muted: #77738b;
        --line: #e9e6f2;
        --surface: #ffffff;
        --canvas: #f7f5fc;
    }
    .stApp {
        background:
            radial-gradient(circle at 82% 2%, rgba(108,76,232,.08), transparent 25rem),
            var(--canvas);
        color: var(--ink);
    }
    .block-container {
        max-width: 1440px;
        padding: 1.8rem 2.4rem 3.5rem;
    }
    section[data-testid="stSidebar"] {
        background: rgba(255,255,255,.96);
        border-right: 1px solid var(--line);
    }
    section[data-testid="stSidebar"] .block-container {
        padding: 1.7rem 1.2rem;
    }
    .brand {
        display: flex;
        align-items: center;
        gap: .65rem;
        margin-bottom: 1.7rem;
        font-size: 1.28rem;
        font-weight: 800;
        letter-spacing: -.03em;
        color: var(--ink);
    }
    .brand-mark {
        display: grid;
        place-items: center;
        width: 2rem;
        height: 2rem;
        border-radius: .65rem;
        background: linear-gradient(135deg, #8c6cff, #5a38d6);
        color: white;
        box-shadow: 0 7px 18px rgba(108,76,232,.25);
    }
    .nav-active {
        padding: .72rem .85rem;
        border-radius: .7rem;
        background: var(--brand-soft);
        color: var(--brand-dark);
        font-weight: 700;
        margin-bottom: .5rem;
    }
    .nav-item {
        padding: .62rem .85rem;
        color: var(--muted);
        font-size: .92rem;
    }
    .side-note {
        margin-top: 1.5rem;
        padding: 1rem;
        border: 1px solid var(--line);
        border-radius: .85rem;
        background: #fbfaff;
        color: var(--muted);
        font-size: .79rem;
        line-height: 1.6;
    }
    .page-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
        gap: 1rem;
        margin-bottom: 1.2rem;
    }
    .eyebrow {
        color: var(--brand);
        font-size: .76rem;
        font-weight: 800;
        letter-spacing: .13em;
        text-transform: uppercase;
    }
    .page-title {
        margin: .2rem 0 .15rem;
        color: var(--ink);
        font-size: clamp(1.8rem, 3vw, 2.45rem);
        font-weight: 800;
        letter-spacing: -.045em;
    }
    .page-subtitle {
        color: var(--muted);
        font-size: .95rem;
    }
    .status-pill {
        white-space: nowrap;
        padding: .55rem .85rem;
        border: 1px solid #dcd5fa;
        border-radius: 999px;
        background: rgba(255,255,255,.8);
        color: var(--brand-dark);
        font-size: .8rem;
        font-weight: 700;
    }
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(255,255,255,.92);
        border-color: var(--line) !important;
        border-radius: 1rem !important;
        box-shadow: 0 10px 32px rgba(34,24,72,.045);
    }
    [data-testid="stMetric"] {
        min-height: 8rem;
        padding: 1.15rem 1.2rem;
        border: 1px solid var(--line);
        border-radius: 1rem;
        background: rgba(255,255,255,.96);
        box-shadow: 0 8px 25px rgba(34,24,72,.045);
    }
    [data-testid="stMetricLabel"] {
        color: var(--muted);
        font-weight: 650;
    }
    [data-testid="stMetricValue"] {
        color: var(--ink);
        font-size: 1.75rem;
        font-weight: 800;
        letter-spacing: -.035em;
    }
    [data-testid="stMetricDelta"] {
        color: #1f9d67;
    }
    [data-testid="stFileUploaderDropzone"] {
        background: #faf9ff;
        border: 1px dashed #bdb0f4;
        border-radius: .9rem;
    }
    .stButton > button, .stDownloadButton > button {
        border-radius: .7rem;
        font-weight: 700;
        min-height: 2.65rem;
    }
    .stButton > button[kind="secondary"] {
        border-color: #d9d3ed;
        background: white;
        color: var(--brand-dark);
    }
    .stDownloadButton > button[kind="primary"] {
        border: 0;
        background: linear-gradient(135deg, #7957f2, #5b3bd1);
        box-shadow: 0 8px 20px rgba(108,76,232,.22);
    }
    [data-testid="stTabs"] [data-baseweb="tab-list"] {
        gap: .45rem;
        padding: .35rem;
        border: 1px solid var(--line);
        border-radius: .85rem;
        background: rgba(255,255,255,.86);
    }
    [data-testid="stTabs"] button[role="tab"] {
        padding: .62rem 1rem;
        border-radius: .6rem;
    }
    [data-testid="stTabs"] button[aria-selected="true"] {
        background: var(--brand-soft);
        color: var(--brand-dark);
    }
    [data-testid="stDataFrame"] {
        border: 1px solid var(--line);
        border-radius: .75rem;
        overflow: hidden;
    }
    .empty-state {
        padding: 1.8rem 1.4rem;
        border: 1px solid var(--line);
        border-radius: 1rem;
        background: white;
        text-align: center;
    }
    .empty-state h3 { margin: .35rem 0; color: var(--ink); }
    .empty-state p { margin: 0; color: var(--muted); }
    #MainMenu, footer { visibility: hidden; }
    @media (max-width: 800px) {
        .block-container { padding: 1.2rem 1rem 2.5rem; }
        .page-header { align-items: flex-start; flex-direction: column; }
        .status-pill { display: none; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


with st.sidebar:
    st.markdown(
        '<div class="brand"><span class="brand-mark">◈</span> REPORTLY</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="nav-active">▦　Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="nav-item">▤　订单分析</div>', unsafe_allow_html=True)
    st.markdown('<div class="nav-item">◫　商品表现</div>', unsafe_allow_html=True)
    st.markdown('<div class="nav-item">↧　报表导出</div>', unsafe_allow_html=True)
    st.divider()
    st.caption("订单文件规范")
    st.code(", ".join(REQUIRED_COLUMNS), language="text")
    st.markdown(
        """
        <div class="side-note">
            <b>当前业务规则</b><br>
            去重键：order_id + sku<br>
            结算币种：人民币 CNY<br>
            数据仅在本次会话中处理
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    """
    <div class="page-header">
        <div>
            <div class="eyebrow">E-commerce intelligence</div>
            <div class="page-title">销售运营仪表盘</div>
            <div class="page-subtitle">合并订单、清理异常数据并生成可交付的销售报表。</div>
        </div>
        <div class="status-pill">● 本地安全处理</div>
    </div>
    """,
    unsafe_allow_html=True,
)

sample_path = Path(__file__).parent / "sample_data" / "orders_1.csv"
sample_paths = [
    Path(__file__).parent / "sample_data" / "orders_1.csv",
    Path(__file__).parent / "sample_data" / "orders_2.csv",
]

with st.container(border=True):
    action_col, upload_col = st.columns([0.34, 0.66], gap="large")
    with action_col:
        st.subheader("快速体验")
        st.caption("使用模拟订单即时预览完整仪表盘。")
        if st.button(
            "使用内置示例数据",
            help="立即加载两份模拟订单，不会上传真实数据。",
            width="stretch",
        ):
            st.session_state["demo_mode"] = True
        if sample_path.exists():
            st.download_button(
                "下载示例 CSV",
                data=sample_path.read_bytes(),
                file_name="sample_orders.csv",
                mime="text/csv",
                width="stretch",
            )
    with upload_col:
        st.subheader("导入订单")
        uploaded_files = st.file_uploader(
            "拖放或选择 CSV / XLSX 文件",
            type=["csv", "xlsx"],
            accept_multiple_files=True,
            help="可同时上传多个文件；每个文件必须包含相同的必要字段。",
            label_visibility="collapsed",
        )
        st.caption("支持 CSV、XLSX · 单个文件不超过 200 MB")

if st.query_params.get("demo") == "true":
    st.session_state["demo_mode"] = True

files = sample_paths if st.session_state.get("demo_mode") else uploaded_files

if not files:
    st.markdown(
        """
        <div class="empty-state">
            <div style="font-size:1.7rem">✦</div>
            <h3>准备好生成第一份销售报告了吗？</h3>
            <p>选择内置示例，或上传你的订单文件开始分析。</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
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

average_order_value = (
    stats["total_sales"] / stats["total_orders"] if stats["total_orders"] else 0
)
metric_1, metric_2, metric_3, metric_4 = st.columns(4)
metric_1.metric("总销售额", f"¥{stats['total_sales']:,.2f}", "已完成汇总")
metric_2.metric("平均订单金额", f"¥{average_order_value:,.2f}", "按有效订单")
metric_3.metric("有效订单", f"{stats['total_orders']:,}", f"{stats['cleaned_rows']} 条明细")
metric_4.metric("销售件数", f"{stats['total_units']:,.0f}", f"清理 {stats['duplicates'] + stats['invalid_rows']} 条")

if stats["duplicates"] or stats["invalid_rows"]:
    st.caption(
        f"原始记录 {stats['original_rows']} 条 · 去除重复 {stats['duplicates']} 条 · "
        f"排除无效数据 {stats['invalid_rows']} 条"
    )

dashboard_tab, product_tab, detail_tab = st.tabs(
    ["Dashboard", "商品分析", "订单明细"]
)

chart_layout = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "font": {"family": "Inter, Segoe UI, sans-serif", "color": "#5f5a70"},
    "margin": {"l": 18, "r": 18, "t": 58, "b": 18},
    "hoverlabel": {"bgcolor": "#211b36", "font_color": "white"},
}

with dashboard_tab:
    trend_col, share_col = st.columns([0.66, 0.34], gap="large")
    with trend_col:
        with st.container(border=True):
            trend_figure = px.line(
                daily,
                x="date",
                y="sales",
                markers=True,
                labels={"date": "日期", "sales": "销售额（¥）"},
                title="销售趋势",
            )
            trend_figure.update_traces(
                line={"color": "#6c4ce8", "width": 3},
                marker={"size": 7, "color": "#6c4ce8"},
                fill="tozeroy",
                fillcolor="rgba(108,76,232,.09)",
            )
            trend_figure.update_layout(**chart_layout, hovermode="x unified")
            trend_figure.update_xaxes(showgrid=False, title=None)
            trend_figure.update_yaxes(
                gridcolor="#eeeaf7", zeroline=False, title=None, tickprefix="¥"
            )
            st.plotly_chart(trend_figure, width="stretch", config={"displayModeBar": False})
    with share_col:
        with st.container(border=True):
            share_figure = go.Figure(
                data=[
                    go.Pie(
                        labels=products["product"],
                        values=products["sales"],
                        hole=0.68,
                        marker_colors=["#5d3bd1", "#896cf0", "#c0b2f8", "#ded7fb"],
                        textinfo="none",
                        hovertemplate="%{label}<br>¥%{value:,.2f}<extra></extra>",
                    )
                ]
            )
            share_figure.update_layout(
                **chart_layout,
                title="商品销售占比",
                showlegend=True,
                legend={"orientation": "h", "y": -0.08, "x": 0.02},
                annotations=[
                    {
                        "text": f"¥{stats['total_sales']:,.0f}<br><span style='font-size:11px'>总销售额</span>",
                        "x": 0.5,
                        "y": 0.5,
                        "showarrow": False,
                        "font": {"size": 17, "color": "#171526"},
                    }
                ],
            )
            st.plotly_chart(share_figure, width="stretch", config={"displayModeBar": False})

    with st.container(border=True):
        st.markdown("#### 每日销售明细")
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
    with st.container(border=True):
        ranking_figure = px.bar(
            products.sort_values("sales"),
            x="sales",
            y="product",
            orientation="h",
            color="sales",
            color_continuous_scale=["#dcd4fb", "#6c4ce8"],
            labels={"product": "商品", "sales": "销售额（¥）"},
            title="商品销售额排行",
            text_auto=".2s",
        )
        ranking_figure.update_layout(**chart_layout, coloraxis_showscale=False)
        ranking_figure.update_xaxes(gridcolor="#eeeaf7", title=None, tickprefix="¥")
        ranking_figure.update_yaxes(title=None)
        st.plotly_chart(ranking_figure, width="stretch", config={"displayModeBar": False})
        st.dataframe(
            products,
            width="stretch",
            hide_index=True,
            column_config={
                "sku": "SKU",
                "product": "商品",
                "order_count": st.column_config.NumberColumn("订单数", format="%d"),
                "units_sold": st.column_config.NumberColumn("销售数量"),
                "sales": st.column_config.ProgressColumn(
                    "销售额",
                    format="¥ %.2f",
                    min_value=0,
                    max_value=float(products["sales"].max()) if len(products) else 1,
                ),
            },
        )

with detail_tab:
    with st.container(border=True):
        table_head, download_head = st.columns([0.72, 0.28])
        with table_head:
            st.markdown("#### 清洗后订单")
            st.caption(f"共 {len(orders)} 条有效明细，可直接导出交付。")
        report = export_report(orders, daily, products)
        with download_head:
            st.download_button(
                "下载 Excel 报表",
                data=report,
                file_name="ecommerce_sales_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary",
                width="stretch",
            )
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
