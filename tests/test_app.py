from streamlit.testing.v1 import AppTest


def test_app_renders_upload_state() -> None:
    app = AppTest.from_file("../app.py").run()

    assert not app.exception
    assert app.title[0].value == "📊 E-commerce Report Automator"
    assert app.info[0].value.startswith("请上传订单文件")
    assert app.get("file_uploader")


def test_demo_mode_renders_dashboard() -> None:
    app = AppTest.from_file("../app.py").run()
    app.button[0].click().run()

    assert not app.exception
    assert app.success[0].value == "已成功处理 2 个内置示例文件。"
    assert app.metric[0].value == "¥584.00"
    assert app.metric[1].value == "7"
    assert len(app.tabs) == 3
