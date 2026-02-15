import importlib.util


def test_ui_module_guarded_import() -> None:
    if importlib.util.find_spec("PySide6") is None:
        return
    import twod_to_threed_relief.ui.app  # noqa: F401
