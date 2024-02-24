import pytest
from click.testing import CliRunner

from inka2.cli import cli, get_notes_from_file
from inka2.environment import ROOT_DIR


@pytest.mark.integration
def test_hello():
    runner = CliRunner()
    result = runner.invoke(
        cli, ["collect", f"{ROOT_DIR}/tests/resources/test_inka_data.md"]
    )
    assert result.exit_code == 0
    print(result.output)
    # assert 'Hello, Test!' in result.output


def test_get_notes_from_file():
    notes = get_notes_from_file(f"{ROOT_DIR}/./tests/resources/test_inka_data.md")
    _ = None
