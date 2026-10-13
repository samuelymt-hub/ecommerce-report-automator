from streamlit.testing.v1 import AppTest


def test_app_renders_upload_state() -> None:
    app = AppTest.from_file("../app.py").run()

    assert not app.exception
    assert app.title[0].value == "📊 E-commerce Report Automator"
    assert app.info[0].value.startswith("请上传订单文件")
    assert app.get("file_uploader")
