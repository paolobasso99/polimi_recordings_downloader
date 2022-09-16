from typer.testing import CliRunner
from typer import BadParameter

from prd.main import app

runner = CliRunner()

def test_app():
    result = runner.invoke(app, ["set-cookie", "lol", "lol"])
    assert result.exception