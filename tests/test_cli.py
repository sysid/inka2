from click.testing import CliRunner

from inka.cli import cli, get_notes_from_file


def test_hello():
    runner = CliRunner()
    result = runner.invoke(cli, ['collect', 'resources/test_inka_data.md'])
    assert result.exit_code == 0
    print(result.output)
    # assert 'Hello, Test!' in result.output


def test_get_notes_from_file():
    notes = get_notes_from_file('./tests/resources/test_inka_data.md')
    _ = None
