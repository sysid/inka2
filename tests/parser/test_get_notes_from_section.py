import pytest

from inka2.models.notes.basic_note import BasicNote
from inka2.models.notes.cloze_note import ClozeNote
from inka2.models.parser import Parser


def test_get_notes_from_section_with_filename(config_add_filename):
    parser = Parser(config_add_filename, "file_doesnt_exist.md", "")
    section = "Deck: Abraham\n" "\n" "1. Some question?\n" "\n" "> Answer"
    expected = BasicNote(
        front_md="Some question?",
        back_md='Answer\n\n<span style="font-size: 9pt;">File: file_doesnt_exist.md</span>',
        tags=[],
        deck_name="Abraham",
    )
    cards = parser._get_notes_from_section(section)

    assert cards[0] == expected


test_cases = {
    "Deck: Abraham\n": [],
    ("Deck: Abraham\n" "Tags: some tags here"): [],
    ("Deck: Abraham\n" "\n" "1. Some question?\n" "\n" "> Answer"): [
        BasicNote(
            front_md="Some question?", back_md="Answer", tags=[], deck_name="Abraham"
        )
    ],
    (
        "Deck: Abraham\n"
        "\n"
        "Tags: one two-three\n"
        "\n"
        "1. Some question?\n"
        "\n"
        "> Answer"
    ): [
        BasicNote(
            front_md="Some question?",
            back_md="Answer",
            tags=["one", "two-three"],
            deck_name="Abraham",
        )
    ],
    (
        "Deck: Abraham\n"
        "\n"
        "1. Some question?\n"
        "\n"
        "> Answer\n"
        "\n"
        "2. Q\n"
        "\n"
        "> A"
    ): [
        BasicNote(
            front_md="Some question?", back_md="Answer", tags=[], deck_name="Abraham"
        ),
        BasicNote(front_md="Q", back_md="A", tags=[], deck_name="Abraham"),
    ],
    (
        "Deck: Abraham\n"
        "\n"
        "Tags: one two-three\n"
        "\n"
        "1. Some question?\n"
        "\n"
        "> Answer\n"
        "\n"
        "2. Q\n"
        "\n"
        "> A"
    ): [
        BasicNote(
            front_md="Some question?",
            back_md="Answer",
            tags=["one", "two-three"],
            deck_name="Abraham",
        ),
        BasicNote(
            front_md="Q", back_md="A", tags=["one", "two-three"], deck_name="Abraham"
        ),
    ],
    # cloze note
    (
        "Deck: Abraham\n"
        "\n"
        "Tags: one two-three\n"
        "\n"
        "1. Some {question} here?\n"
        "\n"
    ): [
        ClozeNote(
            text_md="Some {question} here?",
            tags=["one", "two-three"],
            deck_name="Abraham",
        )
    ],
    # cloze note with ID
    (
        "Deck: Abraham\n"
        "\n"
        "Tags: one two-three\n"
        "\n"
        "<!--ID:123456-->\n"
        "1. Some {question} here?\n"
        "\n"
        "More info on question.\n"
        "\n"
        "And even more!\n"
        "\n"
    ): [
        ClozeNote(
            text_md="Some {question} here?\n\nMore info on question.\n\nAnd even more!",
            tags=["one", "two-three"],
            deck_name="Abraham",
            anki_id=123456,
        )
    ],
    # multiple cloze notes
    (
        "Deck: Abraham\n"
        "\n"
        "Tags: one two-three\n"
        "\n"
        "1. Some {question} here?\n"
        "\n"
        "More info on question.\n"
        "\n"
        "And even more!"
        "\n"
        "2. {1::another} here?\n"
        "\n"
    ): [
        ClozeNote(
            text_md="Some {question} here?\n\nMore info on question.\n\nAnd even more!",
            tags=["one", "two-three"],
            deck_name="Abraham",
        ),
        ClozeNote(
            text_md="{1::another} here?", tags=["one", "two-three"], deck_name="Abraham"
        ),
    ],
    # multiple cloze notes with IDs
    (
        "Deck: Abraham\n"
        "\n"
        "Tags: one two-three\n"
        "\n"
        "<!--ID:1612509025074-->\n"
        "1. Some {question} here?\n"
        "\n"
        "More info on question.\n"
        "\n"
        "And even more!"
        "\n"
        "<!--ID:1612509015034-->\n"
        "2. {1::another} here?\n"
        "\n"
    ): [
        ClozeNote(
            text_md="Some {question} here?\n\nMore info on question.\n\nAnd even more!",
            tags=["one", "two-three"],
            deck_name="Abraham",
            anki_id=1612509025074,
        ),
        ClozeNote(
            text_md="{1::another} here?",
            tags=["one", "two-three"],
            deck_name="Abraham",
            anki_id=1612509015034,
        ),
    ],
    # basic and cloze notes with IDs
    (
        "Deck: Abraham\n"
        "\n"
        "Tags: one two-three\n"
        "\n"
        "1. Some {question} here?\n"
        "\n"
        "More info on question.\n"
        "\n"
        "And even more!"
        "\n"
        "2. Some question?\n"
        "\n"
        "> Answer\n"
        "\n"
        "3. {1::another} here?\n"
        "\n"
    ): [
        ClozeNote(
            text_md="Some {question} here?\n\nMore info on question.\n\nAnd even more!",
            tags=["one", "two-three"],
            deck_name="Abraham",
        ),
        BasicNote(
            front_md="Some question?",
            back_md="Answer",
            tags=["one", "two-three"],
            deck_name="Abraham",
        ),
        ClozeNote(
            text_md="{1::another} here?", tags=["one", "two-three"], deck_name="Abraham"
        ),
    ],
    (
        "Deck: Abraham\n"
        "\n"
        "Tags: one two-three\n"
        "\n"
        "1. Some question?\n"
        "\n"
        "> Answer\n"
        "\n"
        "2. Some {question} here?\n"
        "\n"
        "More info on question.\n"
        "\n"
        "And even more!"
        "\n"
        "3. Question?\n"
        "\n"
        "More info on question.\n"
        "\n"
        "And even more!\n"
        "\n"
        "> Answer\n"
        "> \n"
        "> Additional info\n"
        "> And more to it\n"
        "\n"
        "4. Where am I?\n"
        "\n"
    ): [
        BasicNote(
            front_md="Some question?",
            back_md="Answer",
            tags=["one", "two-three"],
            deck_name="Abraham",
        ),
        ClozeNote(
            text_md="Some {question} here?\n\nMore info on question.\n\nAnd even more!",
            tags=["one", "two-three"],
            deck_name="Abraham",
        ),
        BasicNote(
            front_md="Question?\n\nMore info on question.\n\nAnd even more!",
            back_md="Answer\n\nAdditional info\nAnd more to it",
            tags=["one", "two-three"],
            deck_name="Abraham",
        ),
    ],
    # should not collect empty basic note
    ("Deck: Abraham\n" "\n" "1. \n" "\n" "> "): [],
    ("Deck: Abraham\n" "\n" "1. not empty \n" "\n" "> "): [],
    # should not collect empty basic note
    ("Deck: Abraham\n" "\n" "1. \n" "\n" "> not empty"): [],
    # should not collect empty question
    ("Deck: Abraham\n" "\n" "1. \n"): [],
}


@pytest.mark.parametrize("section, expected", test_cases.items())
def test_get_notes_from_section(fake_parser, section, expected):
    cards = fake_parser._get_notes_from_section(section)

    assert cards == expected
