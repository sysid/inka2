# Development


# Testing
Testing requires some re-design, but for now this workflow works:

- running anki (cmd+enter Anki) creates "User 1" profile if not existing (as per default behavior)
- running anki via Makefile uses pre-defined location: tests/resources/anki_data. Currently not really used.
- test_profile in `Library/Application Support/Anki2` created by `conftest.py` (AnkiMedia)

## integration test workflow:
test `test_create_notes_from_files`: creates anki card from `tests/resources/test_inka_data_init.md` in default Anki location
check correct rendering with: cmd+enter Anki -> browse -> preview
reset with: `make init`
