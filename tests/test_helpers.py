from inka2.helpers import parse_str_to_bool


def test_parse_str_to_bool():
    assert parse_str_to_bool("True") is True
    assert parse_str_to_bool("False") is False
    assert parse_str_to_bool("true") is True
    assert parse_str_to_bool("false") is False
    assert parse_str_to_bool("True ") is True
    assert parse_str_to_bool(" False") is False
    assert parse_str_to_bool("true ") is True
    assert parse_str_to_bool("false ") is False
    assert parse_str_to_bool(" True") is True
    assert parse_str_to_bool(" False") is False
    assert parse_str_to_bool(" true") is True
    assert parse_str_to_bool(" false") is False
    assert parse_str_to_bool("True") is True
    assert parse_str_to_bool("False") is False
    assert parse_str_to_bool("true") is True
    assert parse_str_to_bool("false") is False
    assert parse_str_to_bool("True ") is True
    assert parse_str_to_bool(" False") is False
    assert parse_str_to_bool("true ") is True
    assert parse_str_to_bool("false ") is False
    assert parse_str_to_bool(" True") is True
    assert parse_str_to_bool(" False") is False
    assert parse_str_to_bool(" true") is True
    assert parse_str_to_bool(" false") is False
    assert parse_str_to_bool("True") is True
    assert parse_str_to_bool("False") is False
    assert parse_str_to_bool("true") is True
    assert parse_str_to_bool("false") is False
    assert parse_str_to_bool("True ") is True
    assert parse_str_to_bool(" False") is False
    assert parse_str_to_bool("true ") is True
    assert parse_str_to_bool("false ") is False
    assert parse_str_to_bool(" True") is True
    assert parse_str_to_bool(" False") is False
    assert parse_str_to_bool(" true") is True
    assert parse_str_to_bool(" false") is False
    assert parse_str_to_bool("True") is True
    assert parse_str_to_bool("False") is False
    assert parse_str_to_bool("true") is True
    assert parse_str_to_bool("false") is False
    assert parse_str_to_bool("True ") is True
