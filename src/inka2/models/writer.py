import re
from pathlib import Path
from typing import Iterable, List, Optional, Union

from ..helpers import print_sub_warning
from .notes.basic_note import BasicNote
from .notes.cloze_note import ClozeNote
from .notes.note import Note
from .parser import Parser


class Writer:
    """Class for editing file with notes"""

    def __init__(self, file_path: Union[str, Path], notes: Iterable[Note]):
        self._file_path = file_path
        self._notes = notes

        with open(self._file_path, mode="rt", encoding="utf-8") as f:
            self._file_content = f.read()
        self._note_strings = Parser.get_note_strings(self._file_content)

    def update_note_ids(self):
        """Update lines with IDs of the notes from the file"""
        for note in self._notes:
            # Find note's question in file string
            note_question = note.get_raw_question_field()

            all_occurrences = self.find_all_occurrences(note_question)
            if len(all_occurrences) > 1:
                print_sub_warning(
                    f"Warning: more than one occurrence of '{note_question}' found in {self._file_path}"
                )
                print_sub_warning("Can cause undefined behavior. Please fix.")

            question_string_start = self._file_content.find(
                note_question
            )  # TODO: make unambiguous
            if question_string_start == -1:
                continue

            matches = re.finditer(
                r"(<!--ID:\S+-->)?(\n\d+\.\s*)",
                self._file_content[:question_string_start],
                re.MULTILINE,
            )
            if not matches:
                # Note may not be found cause it was deleted
                continue

            # Search for existing line with ID
            question_match = list(matches)[-1]
            existing_id = Parser.get_id(question_match.group(0))

            # Skip if ID hasn't changed
            if existing_id == note.anki_id:
                continue

            id_string = f"<!--ID:{note.anki_id}-->\n"
            if not note.anki_id:
                # Delete ID from note in file if note object has no ID
                id_string = ""

            # index of newline character that comes before question
            newline_index = question_match.start(2)

            if existing_id is None:
                # Add line with ID after newline
                self._file_content = (
                    self._file_content[: newline_index + 1]
                    + id_string
                    + self._file_content[newline_index + 1 :]
                )
            else:
                # Substitute existing ID with the new one
                self._file_content = self._file_content.replace(
                    f"<!--ID:{existing_id}-->\n", id_string
                )

        self._save()

    def find_all_occurrences(self, note_question: str) -> List[int]:
        start = 0
        all_occurrences = []
        while True:
            start = self._file_content.find(note_question, start)
            if start == -1:  # No more occurrences
                break
            all_occurrences.append(start)
            start += len(note_question)  # Move past the current match
        return all_occurrences

    def update_fields_of_basic_notes(self):
        """Update question and answer fields in notes in file"""
        for note in self._notes:
            if not isinstance(note, BasicNote):
                continue

            if not note.changed:
                continue

            # Find string with this note by its ID
            note_string = self._get_note_string_by_id(note.anki_id)

            # Substitute question field
            current_question = Parser.get_question(note_string)
            self._file_content = self._file_content.replace(
                current_question, note.raw_front_md
            )

            # Create new answer field (with '>')
            current_answer = Parser.get_answer(note_string).rstrip()
            # lines = note.raw_back_md.replace("\n\n", "\n").splitlines()
            lines = note.raw_back_md.splitlines()
            new_answer = "\n".join(map(lambda line: f"> {line}", lines))

            # Substitute answer field
            self._file_content = self._file_content.replace(current_answer, new_answer)

        self._save()

    def delete_notes(self):
        """Delete notes marked for deletion from the file"""
        for note in self._notes:
            if not note.to_delete:
                continue

            # Find string with this note by its ID
            note_string = self._get_note_string_by_id(note.anki_id)

            # Delete note text from file
            self._file_content = self._file_content.replace(note_string, "")

        self._save()

    def update_cloze_notes(self):
        """Updates all cloze notes with the values from updated_text_md field"""
        for note in self._notes:
            if not isinstance(note, ClozeNote):
                continue

            self._file_content = self._file_content.replace(
                note.raw_text_md, note.updated_text_md, 1
            )
            note.raw_text_md = note.updated_text_md  # update info about raw text

        self._save()

    def _save(self):
        """Save file state into the file system"""
        with open(self._file_path, mode="wt", encoding="utf-8") as f:
            f.write(self._file_content)
        self._note_strings = Parser.get_note_strings(self._file_content)

    def _get_note_string_by_id(self, note_id: int) -> Optional[str]:
        """Gets note string from the file by its ID. If note wasn't found returns None"""
        for string in self._note_strings:
            if string.find(str(note_id)) != -1:
                return string
        return None

    def __repr__(self):
        return f"{type(self).__name__}(file_path={self._file_path!r}, notes={self._notes!r})"
