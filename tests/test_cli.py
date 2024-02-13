from click.testing import CliRunner

from inka.cli import cli, get_notes_from_file


def test_hello():
    runner = CliRunner()
    result = runner.invoke(cli, ['collect', 'resources/spring_kafka.md'])
    assert result.exit_code == 0
    assert 'Hello, Test!' in result.output


def test_get_notes_from_file():
    notes = get_notes_from_file('/Users/Q187392/dev/s/forked/inka/tests/resources/spring_kafka.md')
    _ = None
