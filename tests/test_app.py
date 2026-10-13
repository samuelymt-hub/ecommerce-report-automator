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
    assert len(app.tabs) == 4
    assert app.metric[4].value == "8"
    assert app.metric[5].value == "7"


def test_language_switch_renders_english_interface() -> None:
    app = AppTest.from_file("../app.py").run()
    app.selectbox[0].select("English").run()

    assert not app.exception
    assert any("Sales Operations Dashboard" in item.value for item in app.markdown)
    assert any("Use synthetic or de-identified data only" in item.value for item in app.caption)
