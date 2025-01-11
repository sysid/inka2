# Development

## Editable Install
- !! make sure the correct config is in src folder (make install-edit)


# Testing
Testing requires some re-design, but for now this workflow works:

- running anki (cmd+enter Anki) creates "User 1" profile if not existing (as per default behavior)
- running anki via Makefile uses pre-defined location: tests/resources/anki_data. Currently not really used.
- test_profile in `Library/Application Support/Anki2` created by `conftest.py` (AnkiMedia)

## integration test workflow:
make sure to have default configuration

make .PHONY: test_interactive_create_notes_from_files:
    creates anki card from `tests/resources/test_inka_data_init.md` in default Anki location

check correct rendering with: cmd+enter Anki -> browse -> preview
reset with: `make init`


# Bugs
This does not work (numbering), requires a newline before the math block:
> 1. Check in BM25 ranking:
> $$
> \text{score} = \text{bm25_weight} \times \frac{1}{\text{index} + 1}
> $$
> 
looks like it is a paragraph issue

This does work (without numbering):
> Check in BM25 ranking:
> $$
> \text{score} = \text{bm25_weight} \times \frac{1}{\text{index} + 1}
> $$



## aqt
https://forums.ankiweb.net/t/pip-install-aqt-leads-to-x86-architecture-error-upon-import/43051
