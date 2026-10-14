from streamlit.testing.v1 import AppTest


def test_app_renders_upload_state() -> None:
    app = AppTest.from_file("../app.py").run()

    assert not app.exception
    assert any("销售运营仪表盘" in item.value for item in app.markdown)
    assert any("会话内处理" in item.value for item in app.markdown)
    assert any("请勿上传姓名、电话、地址等敏感信息" in item.value for item in app.caption)
    assert app.get("file_uploader")


def test_demo_mode_renders_dashboard() -> None:
    app = AppTest.from_file("../app.py").run()
    app.button[0].click().run()

    assert not app.exception
    assert app.success[0].value == "已成功处理 2 个内置示例文件。"
    assert app.metric[0].value == "¥584.00"
    assert app.metric[2].value == "7"
    assert app.metric[3].label == "日均净收入"
    assert app.metric[3].value == "¥146.00"
    assert len(app.radio) == 1


def test_sidebar_navigation_opens_order_product_and_report_pages() -> None:
    app = AppTest.from_file("../app.py").run()
    app.button[0].click().run()

    app.radio[0].set_value("orders").run()
    assert not app.exception
    assert any("订单中心" in item.value for item in app.markdown)
    assert app.metric[0].label == "筛选销售额"
    assert app.metric[1].value == "7"

    app.radio[0].set_value("products").run()
    assert not app.exception
    assert any("商品表现" in item.value for item in app.markdown)
    assert app.metric[0].label == "商品数量"
    assert app.metric[0].value == "3"

    app.radio[0].set_value("reports").run()
    assert not app.exception
    assert any("报表与数据质量" in item.value for item in app.markdown)
    assert app.metric[0].label == "原始记录"
    assert app.metric[0].value == "8"


def test_language_switch_renders_english_interface() -> None:
    app = AppTest.from_file("../app.py").run()
    app.selectbox[0].select("English").run()

    assert not app.exception
    assert any("Sales Operations Dashboard" in item.value for item in app.markdown)
    assert any("Use synthetic or de-identified data only" in item.value for item in app.caption)
