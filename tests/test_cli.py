import pytest
from click.testing import CliRunner

from inka2.cli import ROOT_DIR, cli, get_notes_from_file

# Collection of manual test cases


@pytest.mark.integration
def test_hello():
    UNDER_TEST = f"{ROOT_DIR}/tests/resources/test_inka_data.md"
    runner = CliRunner()
    result = runner.invoke(cli, ["collect", "-u", UNDER_TEST])
    assert result.exit_code == 0
    print(result.output)
    # assert 'Hello, Test!' in result.output


def test_duplicate_question_string_should_fail():
    UNDER_TEST = f"{ROOT_DIR}/tests/resources/index_out_of_range.md"
    runner = CliRunner()
    result = runner.invoke(cli, ["collect", "-u", UNDER_TEST])
    assert result.exit_code == 1


@pytest.mark.integration
def test_get_notes_from_file():
    notes = get_notes_from_file(f"{ROOT_DIR}/./tests/resources/test_inka_data.md")  # noqa
    _ = None


@pytest.mark.integration
def test_create_notes_from_files():
    """
    make init
    """
    UNDER_TEST = f"{ROOT_DIR}/tests/resources/test_inka_data.md"
    runner = CliRunner()
    result = runner.invoke(cli, ["-v", "collect", UNDER_TEST])
    assert result.exit_code == 0
    print(result.output)
    _ = None
