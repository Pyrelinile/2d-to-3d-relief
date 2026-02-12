from pathlib import Path

from typer.testing import CliRunner

from twod_to_threed_relief.cli import app


def test_cli_inspect(tmp_path: Path) -> None:
    p = tmp_path / "palette.txt"
    p.write_text("#000000,#ffffff")
    runner = CliRunner()
    res = runner.invoke(app, ["inspect", "--palette", str(p)])
    assert res.exit_code == 0
    assert "Palette entries" in res.stdout
