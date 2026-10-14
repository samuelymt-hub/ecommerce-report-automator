"""Streamlit interface for the E-commerce Report Automator."""

import importlib
from pathlib import Path

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Streamlit Cloud can keep imported local modules alive during a hot deploy while
# rerunning this entrypoint. Reload the small processing module so app.py and
# processor.py always come from the same deployed revision.
import processor as _processor

_processor = importlib.reload(_processor)
DEFAULT_DEDUPE_COLUMNS = _processor.DEFAULT_DEDUPE_COLUMNS
REQUIRED_COLUMNS = _processor.REQUIRED_COLUMNS
export_report = _processor.export_report
inspect_order_columns = _processor.inspect_order_columns
process_orders_with_quality = _processor.process_orders_with_quality
suggest_column_mapping = _processor.suggest_column_mapping


COPY = {
    "zh": {
        "nav_dashboard": "▦　Dashboard",
        "nav_orders": "▤　订单分析",
        "nav_products": "◫　商品表现",
        "nav_export": "↧　报表导出",
        "file_schema": "订单文件规范",
        "rules": "当前业务规则",
        "dedupe": "去重键",
        "currency": "结算币种",
        "no_storage": "未配置持久化数据存储",
        "title": "销售运营仪表盘",
        "subtitle": "合并订单、清理异常数据并生成可交付的销售报表。",
        "orders_title": "订单中心",
        "orders_subtitle": "搜索、筛选和检查每一笔清洗后的有效订单。",
        "products_title": "商品表现",
        "products_subtitle": "识别高贡献商品、销量结构和 SKU 表现。",
        "reports_title": "报表与数据质量",
        "reports_subtitle": "导出交付文件，并追踪重复或异常记录。",
        "session": "● 会话内处理",
        "quick_start": "快速体验",
        "data_source": "数据来源与导入",
        "quick_caption": "使用模拟订单即时预览完整仪表盘。",
        "use_demo": "使用内置示例数据",
        "demo_help": "立即加载两份模拟订单，不会上传真实数据。",
        "download_sample": "下载示例 CSV",
        "import_orders": "导入订单",
        "upload_label": "拖放或选择 CSV / XLSX 文件",
        "upload_help": "可同时上传多个文件；系统会自动识别常见中英文列名。",
        "upload_limit": "支持 CSV、XLSX · 单个文件不超过 200 MB",
        "privacy": "公开演示请仅使用模拟或脱敏数据，请勿上传姓名、电话、地址等敏感信息。",
        "empty_title": "准备好生成第一份销售报告了吗？",
        "empty_text": "选择内置示例，或上传你的订单文件开始分析。",
        "config_title": "② 确认字段与处理规则",
        "config_caption": "系统已自动匹配常见中英文列名；如有需要，可在下方调整。",
        "field_mapping": "字段映射",
        "not_mapped": "— 未映射 —",
        "dedupe_fields": "去重字段",
        "dedupe_help": "相同字段组合只保留第一条记录。",
        "currency_label": "显示币种",
        "report_name": "报表文件名",
        "processing_failed": "处理失败",
        "unknown_error": "处理文件时发生未知错误，请检查文件格式后重试。",
        "processed": "已成功处理 {count} 个{source}文件。",
        "source_demo": "内置示例",
        "source_upload": "上传",
        "total_sales": "总销售额",
        "avg_order": "平均订单金额",
        "valid_orders": "有效订单",
        "units": "销售件数",
        "daily_revenue": "日均净收入",
        "active_days": "{count} 个销售日",
        "clean_revenue": "清洗后有效收入",
        "summary_done": "已完成汇总",
        "per_order": "按有效订单",
        "details": "{count} 条明细",
        "cleaned": "清理 {count} 条",
        "quality_summary": "原始记录 {original} 条 · 去除重复 {duplicates} 条 · 排除无效数据 {invalid} 条",
        "tab_dashboard": "Dashboard",
        "tab_products": "商品分析",
        "tab_details": "订单明细",
        "tab_quality": "数据质量",
        "sales_trend": "销售趋势",
        "date": "日期",
        "sales_amount": "销售额",
        "product_share": "商品销售占比",
        "daily_detail": "每日销售明细",
        "order_count": "订单数",
        "sales_units": "销售数量",
        "product_ranking": "商品销售额排行",
        "product": "商品",
        "clean_orders": "清洗后订单",
        "valid_caption": "共 {count} 条有效明细，可直接导出交付。",
        "download_excel": "下载 Excel 报表",
        "quality_title": "数据质量报告",
        "quality_caption": "每一条被排除的记录都会保留来源文件和具体原因。",
        "raw_rows": "原始记录",
        "valid_rows": "有效记录",
        "duplicate_rows": "重复记录",
        "invalid_rows": "异常记录",
        "rejected_title": "排除记录明细",
        "download_rejected": "下载排除记录 CSV",
        "quality_passed": "没有发现重复或异常数据，本次文件全部通过质量检查。",
        "recent_orders": "最近订单",
        "recent_caption": "最近 {count} 条有效订单明细。",
        "search_orders": "搜索订单号、商品或 SKU",
        "filter_products": "筛选商品",
        "date_range": "订单日期范围",
        "filtered_sales": "筛选销售额",
        "filtered_orders": "筛选订单数",
        "filtered_units": "筛选销售件数",
        "visible_rows": "当前明细",
        "rows_count": "{count} 条记录",
        "no_orders": "当前筛选条件下没有订单。",
        "search_products": "搜索商品名称或 SKU",
        "product_count": "商品数量",
        "top_product": "销售冠军",
        "top_sku": "冠军 SKU",
        "top_share": "冠军销售占比",
        "no_products": "当前搜索条件下没有商品。",
        "export_center": "交付文件",
        "export_caption": "Excel 包含有效订单、每日销售、商品排行和排除记录四个工作表。",
    },
    "en": {
        "nav_dashboard": "▦　Dashboard",
        "nav_orders": "▤　Order analysis",
        "nav_products": "◫　Product performance",
        "nav_export": "↧　Report export",
        "file_schema": "Required order fields",
        "rules": "Current rules",
        "dedupe": "Deduplication key",
        "currency": "Display currency",
        "no_storage": "No persistent data storage configured",
        "title": "Sales Operations Dashboard",
        "subtitle": "Merge orders, remove invalid data, and generate delivery-ready sales reports.",
        "orders_title": "Order center",
        "orders_subtitle": "Search, filter, and inspect every cleaned valid order.",
        "products_title": "Product performance",
        "products_subtitle": "Identify high-contribution products, sales mix, and SKU performance.",
        "reports_title": "Reports and data quality",
        "reports_subtitle": "Export deliverables and trace duplicate or invalid records.",
        "session": "● Session processing",
        "quick_start": "Quick start",
        "data_source": "Data source and import",
        "quick_caption": "Preview the full dashboard with synthetic orders.",
        "use_demo": "Use built-in sample data",
        "demo_help": "Load two synthetic order files instantly.",
        "download_sample": "Download sample CSV",
        "import_orders": "Import orders",
        "upload_label": "Drop or select CSV / XLSX files",
        "upload_help": "Upload multiple files; common Chinese and English headers are detected automatically.",
        "upload_limit": "CSV and XLSX · Up to 200 MB per file",
        "privacy": "Use synthetic or de-identified data only. Do not upload names, phone numbers, addresses, or other sensitive information.",
        "empty_title": "Ready to generate your first sales report?",
        "empty_text": "Load the sample data or upload your order files to begin.",
        "config_title": "② Confirm fields and processing rules",
        "config_caption": "Common Chinese and English headers are matched automatically. Adjust them below if needed.",
        "field_mapping": "Field mapping",
        "not_mapped": "— Not mapped —",
        "dedupe_fields": "Deduplication fields",
        "dedupe_help": "Only the first row for each matching field combination is kept.",
        "currency_label": "Display currency",
        "report_name": "Report file name",
        "processing_failed": "Processing failed",
        "unknown_error": "An unexpected error occurred. Check the file format and try again.",
        "processed": "Successfully processed {count} {source} file(s).",
        "source_demo": "sample",
        "source_upload": "uploaded",
        "total_sales": "Total sales",
        "avg_order": "Average order value",
        "valid_orders": "Valid orders",
        "units": "Units sold",
        "daily_revenue": "Avg. daily net revenue",
        "active_days": "{count} selling days",
        "clean_revenue": "After data cleaning",
        "summary_done": "Summary ready",
        "per_order": "Per valid order",
        "details": "{count} line items",
        "cleaned": "Removed {count}",
        "quality_summary": "{original} input rows · {duplicates} duplicates · {invalid} invalid rows",
        "tab_dashboard": "Dashboard",
        "tab_products": "Products",
        "tab_details": "Order details",
        "tab_quality": "Data quality",
        "sales_trend": "Sales trend",
        "date": "Date",
        "sales_amount": "Sales",
        "product_share": "Product sales share",
        "daily_detail": "Daily sales",
        "order_count": "Orders",
        "sales_units": "Units sold",
        "product_ranking": "Product sales ranking",
        "product": "Product",
        "clean_orders": "Cleaned orders",
        "valid_caption": "{count} valid line items, ready to export.",
        "download_excel": "Download Excel report",
        "quality_title": "Data quality report",
        "quality_caption": "Every excluded row retains its source file and a specific rejection reason.",
        "raw_rows": "Input rows",
        "valid_rows": "Valid rows",
        "duplicate_rows": "Duplicates",
        "invalid_rows": "Invalid rows",
        "rejected_title": "Excluded row details",
        "download_rejected": "Download excluded rows CSV",
        "quality_passed": "No duplicates or invalid rows were found. Every row passed the quality checks.",
        "recent_orders": "Recent orders",
        "recent_caption": "The latest {count} valid order line items.",
        "search_orders": "Search order ID, product, or SKU",
        "filter_products": "Filter products",
        "date_range": "Order date range",
        "filtered_sales": "Filtered sales",
        "filtered_orders": "Filtered orders",
        "filtered_units": "Filtered units",
        "visible_rows": "Visible rows",
        "rows_count": "{count} rows",
        "no_orders": "No orders match the current filters.",
        "search_products": "Search product name or SKU",
        "product_count": "Products",
        "top_product": "Top product",
        "top_sku": "Top SKU",
        "top_share": "Top sales share",
        "no_products": "No products match the current search.",
        "export_center": "Delivery files",
        "export_caption": "The Excel workbook includes valid orders, daily sales, product ranking, and excluded rows.",
    },
}

FIELD_LABELS = {
    "zh": {
        "order_id": "订单编号",
        "date": "下单日期",
        "product": "商品名称",
        "sku": "商品 SKU",
        "quantity": "数量",
        "unit_price": "单价",
    },
    "en": {
        "order_id": "Order ID",
        "date": "Order date",
        "product": "Product name",
        "sku": "Product SKU",
        "quantity": "Quantity",
        "unit_price": "Unit price",
    },
}

CURRENCIES = {
    "CNY (¥)": "¥",
    "USD ($)": "$",
    "EUR (€)": "€",
    "GBP (£)": "£",
}


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
    [data-testid="stAppDeployButton"] {
        display: none;
    }
    [data-testid="stToolbar"] {
        background: transparent;
    }
    [data-testid="stSidebarCollapseButton"] {
        visibility: visible !important;
    }
    [data-testid="stExpandSidebarButton"] {
        visibility: visible !important;
        margin: .45rem;
        padding: .35rem;
        border: 1px solid var(--line);
        border-radius: .65rem;
        background: rgba(255,255,255,.94);
        box-shadow: 0 6px 18px rgba(34,24,72,.08);
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
    section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] {
        gap: .35rem;
    }
    section[data-testid="stSidebar"] [data-testid="stRadio"] label {
        min-height: 2.75rem;
        padding: .68rem .85rem;
        border-radius: .7rem;
        color: var(--muted);
        transition: background .18s ease, color .18s ease;
    }
    section[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
        background: #f7f4ff;
        color: var(--brand-dark);
    }
    section[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
        background: var(--brand-soft);
        color: var(--brand-dark);
        font-weight: 750;
    }
    section[data-testid="stSidebar"] [data-testid="stRadio"] label[data-testid="stRadioOption"] > div > div:first-child {
        display: none;
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
    @media (max-width: 1100px) {
        .block-container { padding: 1.4rem 1.5rem 3rem; }
        [data-testid="stMetric"] { min-height: 7rem; padding: .9rem; }
        [data-testid="stMetricValue"] { font-size: 1.35rem; }
        [data-testid="stMetricDelta"] { font-size: .72rem; }
        div[data-testid="stHorizontalBlock"]:has([data-testid="stMetric"]) {
            flex-wrap: wrap;
            gap: .75rem;
        }
        div[data-testid="stHorizontalBlock"]:has([data-testid="stMetric"]) > div[data-testid="stColumn"] {
            flex: 1 1 calc(50% - .75rem);
            min-width: calc(50% - .75rem);
        }
    }
    @media (max-width: 800px) {
        .block-container { padding: 1.2rem 1rem 2.5rem; }
        .page-header { align-items: flex-start; flex-direction: column; }
        .status-pill { display: none; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


language_name = st.sidebar.selectbox(
    "界面语言 / Language",
    ["中文", "English"],
    index=0 if st.session_state.get("language", "zh") == "zh" else 1,
)
language = "zh" if language_name == "中文" else "en"
st.session_state["language"] = language


def t(key: str, **values: object) -> str:
    """Return localized interface copy."""
    return COPY[language][key].format(**values)


with st.sidebar:
    st.markdown(
        '<div class="brand"><span class="brand-mark">◈</span> REPORTLY</div>',
        unsafe_allow_html=True,
    )
    page = st.radio(
        "Navigation",
        options=["dashboard", "orders", "products", "reports"],
        format_func=lambda value: t(f"nav_{'export' if value == 'reports' else value}"),
        label_visibility="collapsed",
        key="active_page",
    )
    st.divider()
    st.caption(t("file_schema"))
    st.code(", ".join(REQUIRED_COLUMNS), language="text")
    st.markdown(
        f"""
        <div class="side-note">
            <b>{t("rules")}</b><br>
            {t("dedupe")}：{st.session_state.get("dedupe_summary", "order_id + sku")}<br>
            {t("currency")}：{st.session_state.get("currency_name", "CNY (¥)")}<br>
            {t("no_storage")}
        </div>
        """,
        unsafe_allow_html=True,
    )

page_copy = {
    "dashboard": (t("title"), t("subtitle")),
    "orders": (t("orders_title"), t("orders_subtitle")),
    "products": (t("products_title"), t("products_subtitle")),
    "reports": (t("reports_title"), t("reports_subtitle")),
}
page_title, page_subtitle = page_copy[page]

st.markdown(
    f"""
    <div class="page-header">
        <div>
            <div class="eyebrow">E-commerce intelligence</div>
            <div class="page-title">{page_title}</div>
            <div class="page-subtitle">{page_subtitle}</div>
        </div>
        <div class="status-pill">{t("session")}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

sample_path = Path(__file__).parent / "sample_data" / "orders_1.csv"
sample_paths = [
    Path(__file__).parent / "sample_data" / "orders_1.csv",
    Path(__file__).parent / "sample_data" / "orders_2.csv",
]

if st.query_params.get("demo") == "true":
    st.session_state["demo_mode"] = True

with st.expander(t("data_source"), expanded=not st.session_state.get("demo_mode", False)):
    action_col, upload_col = st.columns([0.34, 0.66], gap="large")
    with action_col:
        st.subheader(t("quick_start"))
        st.caption(t("quick_caption"))
        if st.button(
            t("use_demo"),
            help=t("demo_help"),
            width="stretch",
        ):
            st.session_state["demo_mode"] = True
        if sample_path.exists():
            st.download_button(
                t("download_sample"),
                data=sample_path.read_bytes(),
                file_name="sample_orders.csv",
                mime="text/csv",
                width="stretch",
            )
    with upload_col:
        st.subheader(t("import_orders"))
        uploaded_files = st.file_uploader(
            t("upload_label"),
            type=["csv", "xlsx"],
            accept_multiple_files=True,
            help=t("upload_help"),
            label_visibility="collapsed",
        )
        st.caption(t("upload_limit"))
        st.caption(t("privacy"))

files = sample_paths if st.session_state.get("demo_mode") else uploaded_files

if not files:
    st.markdown(
        f"""
        <div class="empty-state">
            <div style="font-size:1.7rem">✦</div>
            <h3>{t("empty_title")}</h3>
            <p>{t("empty_text")}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

try:
    available_columns = inspect_order_columns(files[0])
    suggested_mapping = suggest_column_mapping(available_columns)
except ValueError as exc:
    st.error(f"{t('processing_failed')}：{exc}")
    st.stop()

with st.expander(t("config_title"), expanded=not st.session_state.get("demo_mode", False)):
    st.caption(t("config_caption"))
    st.markdown(f"**{t('field_mapping')}**")
    mapping_columns = st.columns(3)
    column_mapping: dict[str, str | None] = {}
    mapping_options = [t("not_mapped"), *available_columns]
    for index, canonical in enumerate(REQUIRED_COLUMNS):
        suggested = suggested_mapping.get(canonical)
        default_index = mapping_options.index(suggested) if suggested in mapping_options else 0
        with mapping_columns[index % 3]:
            selected = st.selectbox(
                FIELD_LABELS[language][canonical],
                mapping_options,
                index=default_index,
                key=f"mapping_{canonical}_{language}",
            )
            column_mapping[canonical] = None if selected == t("not_mapped") else selected

    st.divider()
    rule_col, currency_col, name_col = st.columns([1.35, 0.75, 1])
    with rule_col:
        dedupe_columns = st.multiselect(
            t("dedupe_fields"),
            options=list(REQUIRED_COLUMNS),
            default=list(DEFAULT_DEDUPE_COLUMNS),
            format_func=lambda field: FIELD_LABELS[language][field],
            help=t("dedupe_help"),
        )
    with currency_col:
        currency_name = st.selectbox(t("currency_label"), list(CURRENCIES))
    with name_col:
        report_name = st.text_input(t("report_name"), value="ecommerce_sales_report")

currency_symbol = CURRENCIES[currency_name]
safe_report_name = "".join(
    character for character in report_name.strip() if character.isalnum() or character in ("-", "_")
) or "ecommerce_sales_report"
st.session_state["dedupe_summary"] = " + ".join(dedupe_columns) if dedupe_columns else "—"
st.session_state["currency_name"] = currency_name

try:
    result = process_orders_with_quality(
        files,
        column_mapping=column_mapping,
        dedupe_columns=dedupe_columns,
    )
    orders, daily, products, rejected, stats = (
        result.cleaned,
        result.daily,
        result.products,
        result.rejected,
        result.stats,
    )
except ValueError as exc:
    st.error(f"{t('processing_failed')}：{exc}")
    st.stop()
except Exception:
    st.error(t("unknown_error"))
    st.stop()

source_label = t("source_demo") if st.session_state.get("demo_mode") else t("source_upload")
st.success(t("processed", count=len(files), source=source_label))

average_order_value = (
    stats["total_sales"] / stats["total_orders"] if stats["total_orders"] else 0
)
active_days = int(daily["date"].nunique()) if not daily.empty else 0
average_daily_revenue = stats["total_sales"] / active_days if active_days else 0

chart_layout = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "font": {"family": "Inter, Segoe UI, sans-serif", "color": "#5f5a70"},
    "margin": {"l": 18, "r": 18, "t": 58, "b": 18},
    "hoverlabel": {"bgcolor": "#211b36", "font_color": "white"},
}


def order_table(frame):
    """Render a consistently formatted order table."""
    st.dataframe(
        frame,
        width="stretch",
        hide_index=True,
        column_config={
            "order_id": FIELD_LABELS[language]["order_id"],
            "date": st.column_config.DateColumn(t("date"), format="YYYY-MM-DD"),
            "product": t("product"),
            "sku": "SKU",
            "quantity": st.column_config.NumberColumn(FIELD_LABELS[language]["quantity"]),
            "unit_price": st.column_config.NumberColumn(
                FIELD_LABELS[language]["unit_price"], format=f"{currency_symbol} %.2f"
            ),
            "sales": st.column_config.NumberColumn(
                t("sales_amount"), format=f"{currency_symbol} %.2f"
            ),
        },
    )


def product_table(frame):
    """Render a consistently formatted product performance table."""
    max_sales = float(frame["sales"].max()) if len(frame) else 1
    st.dataframe(
        frame,
        width="stretch",
        hide_index=True,
        column_config={
            "sku": "SKU",
            "product": t("product"),
            "order_count": st.column_config.NumberColumn(t("order_count"), format="%d"),
            "units_sold": st.column_config.NumberColumn(t("sales_units")),
            "sales": st.column_config.ProgressColumn(
                t("sales_amount"),
                format=f"{currency_symbol} %.2f",
                min_value=0,
                max_value=max_sales,
            ),
        },
    )


if page == "dashboard":
    metric_1, metric_2, metric_3, metric_4 = st.columns(4)
    metric_1.metric(
        t("total_sales"),
        f"{currency_symbol}{stats['total_sales']:,.2f}",
        t("clean_revenue"),
    )
    metric_2.metric(
        t("avg_order"), f"{currency_symbol}{average_order_value:,.2f}", t("per_order")
    )
    metric_3.metric(
        t("valid_orders"),
        f"{stats['total_orders']:,}",
        t("details", count=stats["cleaned_rows"]),
    )
    metric_4.metric(
        t("daily_revenue"),
        f"{currency_symbol}{average_daily_revenue:,.2f}",
        t("active_days", count=active_days),
    )

    if stats["duplicates"] or stats["invalid_rows"]:
        st.caption(
            t(
                "quality_summary",
                original=stats["original_rows"],
                duplicates=stats["duplicates"],
                invalid=stats["invalid_rows"],
            )
        )

    trend_col, share_col = st.columns([0.66, 0.34], gap="large")
    with trend_col:
        with st.container(border=True):
            trend_figure = px.line(
                daily,
                x="date",
                y="sales",
                markers=True,
                labels={"date": t("date"), "sales": f"{t('sales_amount')} ({currency_symbol})"},
                title=t("sales_trend"),
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
                gridcolor="#eeeaf7", zeroline=False, title=None, tickprefix=currency_symbol
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
                        hovertemplate=f"%{{label}}<br>{currency_symbol}%{{value:,.2f}}<extra></extra>",
                    )
                ]
            )
            share_figure.update_layout(
                **chart_layout,
                title=t("product_share"),
                showlegend=True,
                legend={"orientation": "h", "y": -0.08, "x": 0.02},
                annotations=[
                    {
                        "text": f"{currency_symbol}{stats['total_sales']:,.0f}<br><span style='font-size:11px'>{t('total_sales')}</span>",
                        "x": 0.5,
                        "y": 0.5,
                        "showarrow": False,
                        "font": {"size": 17, "color": "#171526"},
                    }
                ],
            )
            st.plotly_chart(share_figure, width="stretch", config={"displayModeBar": False})

    with st.container(border=True):
        recent = orders.sort_values(["date", "order_id"], ascending=[False, False]).head(8)
        st.markdown(f"#### {t('recent_orders')}")
        st.caption(t("recent_caption", count=len(recent)))
        order_table(recent)

elif page == "orders":
    filter_col, product_col, date_col = st.columns([1.25, 1, 1], gap="medium")
    with filter_col:
        order_query = st.text_input(t("search_orders"), placeholder="ORD001 / SKU / Product")
    with product_col:
        selected_products = st.multiselect(
            t("filter_products"),
            sorted(orders["product"].dropna().unique().tolist()),
        )
    with date_col:
        if orders.empty:
            selected_dates = ()
            st.caption(t("date_range"))
        else:
            minimum_date = orders["date"].min().date()
            maximum_date = orders["date"].max().date()
            selected_dates = st.date_input(
                t("date_range"),
                value=(minimum_date, maximum_date),
                min_value=minimum_date,
                max_value=maximum_date,
            )

    filtered_orders = orders.copy()
    if order_query.strip():
        query = order_query.strip()
        search_columns = filtered_orders[["order_id", "product", "sku"]].astype(str)
        search_mask = search_columns.apply(
            lambda column: column.str.contains(query, case=False, regex=False)
        ).any(axis=1)
        filtered_orders = filtered_orders.loc[search_mask]
    if selected_products:
        filtered_orders = filtered_orders.loc[filtered_orders["product"].isin(selected_products)]
    if isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 2:
        start_date, end_date = selected_dates
        filtered_orders = filtered_orders.loc[
            filtered_orders["date"].dt.date.between(start_date, end_date)
        ]

    filtered_sales = float(filtered_orders["sales"].sum())
    filtered_order_count = int(filtered_orders["order_id"].nunique())
    filtered_units = float(filtered_orders["quantity"].sum())
    order_metric_1, order_metric_2, order_metric_3, order_metric_4 = st.columns(4)
    order_metric_1.metric(t("filtered_sales"), f"{currency_symbol}{filtered_sales:,.2f}")
    order_metric_2.metric(t("filtered_orders"), f"{filtered_order_count:,}")
    order_metric_3.metric(t("filtered_units"), f"{filtered_units:,.0f}")
    order_metric_4.metric(t("visible_rows"), f"{len(filtered_orders):,}")

    with st.container(border=True):
        st.markdown(f"#### {t('clean_orders')}")
        st.caption(t("rows_count", count=len(filtered_orders)))
        if filtered_orders.empty:
            st.info(t("no_orders"))
        else:
            order_table(filtered_orders.sort_values("date", ascending=False))

elif page == "products":
    product_query = st.text_input(t("search_products"), placeholder="SKU / Product")
    filtered_products = products.copy()
    if product_query.strip():
        query = product_query.strip()
        product_mask = (
            filtered_products["product"].astype(str).str.contains(query, case=False, regex=False)
            | filtered_products["sku"].astype(str).str.contains(query, case=False, regex=False)
        )
        filtered_products = filtered_products.loc[product_mask]

    top_row = products.sort_values("sales", ascending=False).iloc[0] if len(products) else None
    top_share_value = (
        float(top_row["sales"]) / stats["total_sales"] * 100
        if top_row is not None and stats["total_sales"]
        else 0
    )
    product_metric_1, product_metric_2, product_metric_3, product_metric_4 = st.columns(4)
    product_metric_1.metric(t("product_count"), f"{len(products):,}")
    product_metric_2.metric(t("top_product"), str(top_row["product"]) if top_row is not None else "—")
    product_metric_3.metric(t("top_sku"), str(top_row["sku"]) if top_row is not None else "—")
    product_metric_4.metric(t("top_share"), f"{top_share_value:.1f}%")

    if filtered_products.empty:
        st.info(t("no_products"))
    else:
        product_chart_col, product_share_col = st.columns([0.66, 0.34], gap="large")
        with product_chart_col:
            with st.container(border=True):
                ranking_figure = px.bar(
                    filtered_products.sort_values("sales"),
                    x="sales",
                    y="product",
                    orientation="h",
                    color="sales",
                    color_continuous_scale=["#dcd4fb", "#6c4ce8"],
                    labels={
                        "product": t("product"),
                        "sales": f"{t('sales_amount')} ({currency_symbol})",
                    },
                    title=t("product_ranking"),
                    text_auto=".2s",
                )
                ranking_figure.update_layout(**chart_layout, coloraxis_showscale=False)
                ranking_figure.update_xaxes(
                    gridcolor="#eeeaf7", title=None, tickprefix=currency_symbol
                )
                ranking_figure.update_yaxes(title=None)
                st.plotly_chart(
                    ranking_figure, width="stretch", config={"displayModeBar": False}
                )
        with product_share_col:
            with st.container(border=True):
                product_share_figure = go.Figure(
                    data=[
                        go.Pie(
                            labels=filtered_products["product"],
                            values=filtered_products["sales"],
                            hole=0.68,
                            marker_colors=["#5d3bd1", "#896cf0", "#c0b2f8", "#ded7fb"],
                            textinfo="percent",
                            hovertemplate=f"%{{label}}<br>{currency_symbol}%{{value:,.2f}}<extra></extra>",
                        )
                    ]
                )
                product_share_figure.update_layout(
                    **chart_layout,
                    title=t("product_share"),
                    showlegend=True,
                    legend={"orientation": "h", "y": -0.08, "x": 0.02},
                )
                st.plotly_chart(
                    product_share_figure, width="stretch", config={"displayModeBar": False}
                )

        with st.container(border=True):
            product_table(filtered_products.sort_values("sales", ascending=False))

elif page == "reports":
    report = export_report(orders, daily, products, rejected)
    with st.container(border=True):
        export_copy, export_action = st.columns([0.7, 0.3], gap="large")
        with export_copy:
            st.markdown(f"#### {t('export_center')}")
            st.caption(t("export_caption"))
        with export_action:
            st.download_button(
                t("download_excel"),
                data=report,
                file_name=f"{safe_report_name}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary",
                width="stretch",
            )

    st.markdown(f"### {t('quality_title')}")
    st.caption(t("quality_caption"))
    quality_1, quality_2, quality_3, quality_4 = st.columns(4)
    quality_1.metric(t("raw_rows"), f"{stats['original_rows']:,}")
    quality_2.metric(t("valid_rows"), f"{stats['cleaned_rows']:,}")
    quality_3.metric(t("duplicate_rows"), f"{stats['duplicates']:,}")
    quality_4.metric(t("invalid_rows"), f"{stats['invalid_rows']:,}")

    if rejected.empty:
        st.success(t("quality_passed"))
    else:
        with st.container(border=True):
            quality_head, quality_download = st.columns([0.72, 0.28])
            with quality_head:
                st.markdown(f"#### {t('rejected_title')}")
            with quality_download:
                st.download_button(
                    t("download_rejected"),
                    data=rejected.to_csv(index=False).encode("utf-8-sig"),
                    file_name=f"{safe_report_name}_rejected.csv",
                    mime="text/csv",
                    width="stretch",
                )
            st.dataframe(rejected, width="stretch", hide_index=True)
