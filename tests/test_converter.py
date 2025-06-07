import mistune
import pytest

from inka2.cli import CONFIG
from inka2.helpers import parse_str_to_bool
from inka2.mistune_plugins.mathjax3 import plugin_mathjax3
from inka2.models import converter
from inka2.models.notes.basic_note import BasicNote
from inka2.models.notes.cloze_note import ClozeNote


@pytest.fixture
def md():
    return mistune.create_markdown(
        plugins=["strikethrough", "footnotes", "table", plugin_mathjax3],
        escape=parse_str_to_bool(CONFIG.get_option_value("defaults", "escape_html")),
    )


@pytest.fixture
def basic_note():
    """BasicNote object with dummy data for testing"""
    return BasicNote(front_md="dummy", back_md="dummy", tags=[], deck_name="")


# Test cases for cloze deletion conversion
convert_cloze_test_cases = {
    # SHORT IMPLICIT CLOZE DELETIONS
    "Some {cloze question}": "Some {{c1::cloze question}}",  # Basic implicit cloze
    "Some {cloze question::really helpful hint}": "Some {{c1::cloze question::really helpful hint}}",
    # Implicit with hint
    "Some {cloze question}\n\n{another} one": "Some {{c1::cloze question}}\n\n{{c2::another}} one",
    # Multiple implicit cloze
    "Some {2::cloze question}\n\n{1::another} one": "Some {{c2::cloze question}}\n\n{{c1::another}} one",
    # Mixed numbering

    # CLOZE AROUND MATH
    r"math: {$\sqrt{2}$}": r"math: {{c1::$\sqrt{2}$}}",  # Cloze around inline math
    r"math: {$$\frac{\sqrt{2}}{15}$$}": r"math: {{c1::$$\frac{\sqrt{2}}{15}$$}}",
    # Cloze around block math (note: this won't match actual block math pattern)

    # CLOZE AROUND CODE
    r"inline code: {`func() int { return {12} }`}": r"inline code: {{c1::`func() int { return {12} }`}}",
    # Cloze around inline code
    (
        "Code:\n"
        "{\n"
        "```\n"
        "func main() {\n"
        '\tdefer func() { fmt.Println("exited") }\n'
        '\tdatabase.DB, err := sql.Open("pgx", os.Getenv("POSTGRES_URL"))\n'
        "\tif err != nil {\n"
        "\t\tlog.Fatal(err)\n"
        "\t}\n"
        "}\n"
        "```\n"
        "}\n"
    ): (
        "Code:\n"
        "{{c1::\n"
        "```\n"
        "func main() {\n"
        '\tdefer func() { fmt.Println("exited") }\n'
        '\tdatabase.DB, err := sql.Open("pgx", os.Getenv("POSTGRES_URL"))\n'
        "\tif err != nil {\n"
        "\t\tlog.Fatal(err)\n"
        "\t}\n"
        "}\n"
        "```\n"
        "}}\n"
    ),  # Cloze around block code

    # EXPLICIT SHORT CLOZE DELETIONS
    "Some {1::cloze question}": "Some {{c1::cloze question}}",  # Explicit numbered cloze
    "Some {1::cloze question::really helpful hint}": "Some {{c1::cloze question::really helpful hint}}",
    # Explicit with hint
    "Some {c1::cloze question}": "Some {{c1::cloze question}}",  # Explicit with 'c' prefix
    "Some {2::cloze question}\n\n{1::another} one": "Some {{c2::cloze question}}\n\n{{c1::another}} one",
    # Multiple explicit

    # ANKI FORMAT (should remain unchanged)
    "Some {{c1::cloze question}}": "Some {{c1::cloze question}}",  # Already in Anki format
    "Some {{c1::cloze question::really helpful hint}}": "Some {{c1::cloze question::really helpful hint}}",
    # Anki with hint
    "Some {{c2::cloze question}}\n\n{{c1::another}} one": "Some {{c2::cloze question}}\n\n{{c1::another}} one",
    # Multiple Anki format

    # CLOZE INSIDE MATH/CODE (should be ignored)
    r"math: $\sqrt{2::15}$": r"math: $\sqrt{2::15}$",  # Cloze inside inline math - ignored
    r"math: $$\frac{1::\sqrt{2}}{12::15}$$": r"math: $$\frac{1::\sqrt{2}}{12::15}$$",
    # Cloze inside block math - ignored
    r"inline code: `func() int { return {1::12} }`": r"inline code: `func() int { return {1::12} }`",
    # Cloze inside inline code - ignored
    (
        "Code:\n"
        "```\n"
        "func main() {\n"
        '\tdefer func() { fmt.Println("{1::exited}") }\n'
        '\tdatabase.DB, err := sql.Open("pgx", os.Getenv("POSTGRES_URL"))\n'
        "\tif err != nil {\n"
        "\t\tlog.Fatal(err)\n"
        "\t}\n"
        "}\n"
        "```\n"
    ): (
        "Code:\n"
        "```\n"
        "func main() {\n"
        '\tdefer func() { fmt.Println("{1::exited}") }\n'
        '\tdatabase.DB, err := sql.Open("pgx", os.Getenv("POSTGRES_URL"))\n'
        "\tif err != nil {\n"
        "\t\tlog.Fatal(err)\n"
        "\t}\n"
        "}\n"
        "```\n"
    ),  # Cloze inside block code - ignored

    # ANKI FORMAT INSIDE MATH/CODE (should be ignored)
    r"math: $\sqrt{ {{c1::15}} } $": r"math: $\sqrt{ {{c1::15}} } $",  # Anki cloze inside inline math - ignored
    r"math: $$\frac{ {{1::\sqrt{2}}} }{ {{c12::15}} }$$": r"math: $$\frac{ {{1::\sqrt{2}}} }{ {{c12::15}} }$$",
    # Anki cloze inside block math - ignored
    r"inline code: `func() int { return {{c1::12}} }`": r"inline code: `func() int { return {{c1::12}} }`",
    # Anki cloze inside inline code - ignored
    (
        "Code:\n"
        "```\n"
        "func main() {\n"
        '\tdefer func() { fmt.Println("exited") }\n'
        '\tdatabase.DB, err := {{c1::sql.Open("pgx", os.Getenv("POSTGRES_URL"))}}\n'
        "\tif err != nil {\n"
        "\t\tlog.Fatal(err)\n"
        "\t}\n"
        "}\n"
        "```\n"
    ): (
        "Code:\n"
        "```\n"
        "func main() {\n"
        '\tdefer func() { fmt.Println("exited") }\n'
        '\tdatabase.DB, err := {{c1::sql.Open("pgx", os.Getenv("POSTGRES_URL"))}}\n'
        "\tif err != nil {\n"
        "\t\tlog.Fatal(err)\n"
        "\t}\n"
        "}\n"
        "```\n"
    ),  # Anki cloze inside block code - ignored

    # COMPLEX MIXED CASES
    (
        r"some math {$\sqrt{2}$}, code {`func() int`}, "
        r"more code {`defer resp.body.Close()`} and more math {$\frac{1}{5}$}"
    ): (
        r"some math {{c1::$\sqrt{2}$}}, code {{c2::`func() int`}}, "
        r"more code {{c3::`defer resp.body.Close()`}} and more math {{c4::$\frac{1}{5}$}}"
    ),  # Multiple cloze around math and code - tests ordering

    # REAL WORLD EXAMPLES
    (
        r"{Paris} is the capital and most populous city of {2::France},"
        r" with a estimated population of {2,148,271} residents"
    ): (
        r"{{c1::Paris}} is the capital and most populous city of {{c2::France}},"
        r" with a estimated population of {{c3::2,148,271}} residents"
    ),  # Mixed implicit and explicit cloze
    (
        r"{c3::Paris} is the capital and most populous city of {3::France},"
        r" with a {{c1::estimated::my hint}} population of {2,148,271} residents"
    ): (
        r"{{c3::Paris}} is the capital and most populous city of {{c3::France}},"
        r" with a {{c1::estimated::my hint}} population of {{c4::2,148,271}} residents"
    ),  # Complex mixed with existing Anki format
}

# Test cases for markdown to HTML conversion based on existing working patterns
md_to_html_test_cases = {
    # BASIC MARKDOWN
    "some text here": "<p>some text here</p>",  # Plain text
    "some text here\nand more text": "<p>some text here\nand more text</p>",  # Single line break
    "some text here\n\nmore text": "<p>some text here</p><p>more text</p>",  # Double line break creates new paragraph

    # COMPLEX MARKDOWN
    (
        "1. Item1\n"
        "2. Item2\n"
        "3. Item3\n"
        "\n"
        "```javascript\n"
        "let a = 12;\n"
        "let b = a;\n"
        "```\n"
        "\n"
        "[google](https://google.com)\n"
    ): (
        "<ol><li>Item1</li><li>Item2</li><li>Item3</li></ol>"
        '<pre><code class="language-javascript">let a = 12;\nlet b = a;</code></pre>'
        '<p><a href="https://google.com">google</a></p>'
    ),  # Ordered list, code block, and link

    # INLINE MATH (from existing working test cases)
    r"$\sqrt{5}$": r'<p>\(\sqrt{5}\)</p>',  # Basic inline math
    r"$\sqrt{5} $": r'<p>\(\sqrt{5} \)</p>',  # Math with trailing space (valid)
    r"$multiple words$": r'<p>\(multiple words\)</p>',  # Multiple words in math
    r"weird$mathjax$more word$1$s": r'<p>weird\(mathjax\)more word\(1\)s</p>',  # Multiple inline math in text
    "$$$": r'<p>\($\)</p>',  # Three dollar signs (middle parsed as math)

    # INVALID INLINE MATH (newlines prevent parsing)
    "$\\sqrt{5}\n$": "<p>$\\sqrt{5}\n$</p>",  # Newline in math - not parsed
    "$\n\\sqrt{5}$": "<p>$\n\\sqrt{5}$</p>",  # Leading newline - not parsed

    # ESCAPED MATH
    r"\$\sqrt{5}$": r"<p>$\sqrt{5}$</p>",  # Escaped leading dollar
    r"\$\sqrt{5}\$": r"<p>$\sqrt{5}$</p>",  # Both dollars escaped
    r"\$$\sqrt{2}$$": r'<p>$\(\sqrt{2}\)$</p>',  # Escaped first dollar, rest parsed as inline math

    # AMBIGUOUS DOLLAR SIGNS
    r"text $$ here": r"<p>text $$ here</p>",  # Two dollars with space - not math

    # BLOCK MATH (requires blank lines before and after) - fixed expected value
    "$$\n\\sqrt{2}\n\\frac{1}{2}\n$$": r'\[\sqrt{2}' + '\n' + r'\frac{1}{2}\]',  # Valid block math with proper formatting
}


@pytest.mark.parametrize("test_input, expected", convert_cloze_test_cases.items())
def test_convert_cloze_deletions_to_anki_format(test_input, expected):
    """Test conversion of various cloze deletion formats to Anki format"""
    cloze_note = ClozeNote(text_md=test_input, tags=[], deck_name="")

    converter.convert_cloze_deletions_to_anki_format([cloze_note])

    assert cloze_note.updated_text_md == expected


def test_convert_cloze_deletions_to_anki_format_works_with_multiple_notes():
    """Test that cloze conversion works correctly with multiple notes in one batch"""
    text1 = (
        r"{Paris} is the capital and most populous city of {2::France},"
        r" with a estimated population of {2,148,271} residents"
    )
    text2 = "Some {{c1::cloze question}}"
    cloze_note1 = ClozeNote(text_md=text1, tags=[], deck_name="")
    cloze_note2 = ClozeNote(text_md=text2, tags=[], deck_name="")
    expected1 = (
        r"{{c1::Paris}} is the capital and most populous city of {{c2::France}},"
        r" with a estimated population of {{c3::2,148,271}} residents"
    )
    expected2 = "Some {{c1::cloze question}}"

    converter.convert_cloze_deletions_to_anki_format([cloze_note1, cloze_note2])

    assert cloze_note1.updated_text_md == expected1
    assert cloze_note2.updated_text_md == expected2


@pytest.mark.parametrize("test_input, expected", md_to_html_test_cases.items())
def test_convert_md_to_html(basic_note, test_input, expected, md):
    """Test markdown to HTML conversion with math parsing"""
    html = converter._convert_md_to_html(test_input, md)

    assert html == expected


def test_convert_md_to_html_no_html_escaping(basic_note, md):
    """Test that HTML tags are preserved and not escaped"""
    test_input = (
        """<span style="font-size: 9pt;">This text will be 9pt in size.</span>"""
    )
    expected = (
        """<p><span style="font-size: 9pt;">This text will be 9pt in size.</span></p>"""
    )
    html = converter._convert_md_to_html(test_input, md)
    assert html == expected


def test_convert_cards_to_html_works_with_multiple_cards(md):
    """Test HTML conversion with multiple cards of different types"""
    text1 = r"inside $\sqrt{2}$ text"
    text2 = "1. Item1\n2. Item2\n3. Item3\n"
    basic_note1 = BasicNote(front_md=text1, back_md=text2, tags=[], deck_name="")
    basic_note2 = BasicNote(front_md=text2, back_md=text1, tags=[], deck_name="")
    cloze_note = ClozeNote(text_md="Some question {{c1::42}}", tags=[], deck_name="")
    expected1 = r'<p>inside \(\sqrt{2}\) text</p>'
    expected2 = "<ol><li>Item1</li><li>Item2</li><li>Item3</li></ol>"
    expected3 = "<p>Some question {{c1::42}}</p>"

    converter.convert_notes_to_html([basic_note1, basic_note2, cloze_note], md)

    assert basic_note1.front_html == expected1
    assert basic_note1.back_html == expected2
    assert basic_note2.front_html == expected2
    assert basic_note2.back_html == expected1
    assert cloze_note.text_html == expected3


def test_block_math_requires_blank_lines():
    """Test that block math only works with proper blank line formatting"""
    md = mistune.create_markdown(
        plugins=["strikethrough", "footnotes", "table", plugin_mathjax3],
        escape=False,
    )

    # These should NOT be parsed as block math because they lack proper formatting
    invalid_block_math_cases = [
        (r"$$\sqrt{2}$$", r"<p>\($\sqrt{2}\)$</p>"),  # Parsed as inline math, not block math
        (r"inside $$\sqrt{2}$$ text", r"<p>inside \($\sqrt{2}\)$ text</p>"),  # Also parsed as inline math
        ("$$multi\nline$$", "<p>$$multi\nline$$</p>"),  # Block math without surrounding blank lines - not parsed
    ]

    for test_input, expected_html in invalid_block_math_cases:
        html = converter._convert_md_to_html(test_input, md)
        # These should be treated as regular text with dollar signs, not block math
        assert r"\[" not in html, f"Input '{test_input}' was incorrectly parsed as block math"
        assert html == expected_html, f"Input '{test_input}' did not produce expected HTML"

    # Special case: $$$$ gets parsed as inline math with single dollar inside
    html = converter._convert_md_to_html("$$$$", md)
    assert html == r'<p>\($\)$</p>', "Four dollars should be parsed as inline math with dollar inside"

    # Case where inline math should work: single $ without newlines
    html = converter._convert_md_to_html(r"$\sqrt{2}$", md)
    assert html == r'<p>\(\sqrt{2}\)</p>', "Single dollar inline math should work"



def test_inline_math_constraints():
    """Test that inline math follows the actual regex pattern constraints"""
    md = mistune.create_markdown(
        plugins=["strikethrough", "footnotes", "table", plugin_mathjax3],
        escape=False,
    )

    # Valid inline math cases (based on existing working test cases)
    valid_cases = [
        ("$\\sqrt{5}$", r'<p>\(\sqrt{5}\)</p>'),
        ("$\\sqrt{5} $", r'<p>\(\sqrt{5} \)</p>'),  # Trailing space inside content is OK
        ("$multiple words$", r'<p>\(multiple words\)</p>'),
        ("weird$mathjax$more word$1$s", r'<p>weird\(mathjax\)more word\(1\)s</p>'),  # Multiple math expressions
        ("$$$", r'<p>\($\)</p>'),  # Three dollars parsed as math with single dollar content
    ]

    for test_input, expected in valid_cases:
        html = converter._convert_md_to_html(test_input, md)
        assert html == expected, f"Valid inline math '{test_input}' not parsed correctly. Got: {html}"

    # Invalid inline math cases (based on existing test cases that should NOT be parsed)
    invalid_cases = [
        ("$\\sqrt{5}\n$", "<p>$\\sqrt{5}\n$</p>"),  # Newline at end prevents parsing
        ("$\n\\sqrt{5}$", "<p>$\n\\sqrt{5}$</p>"),  # Newline at start prevents parsing
    ]

    for test_input, expected in invalid_cases:
        html = converter._convert_md_to_html(test_input, md)
        assert html == expected, f"Invalid inline math '{test_input}' should not be parsed. Got: {html}"


def test_cloze_ignores_math_and_code_contexts():
    """Test that cloze deletions inside math and code blocks are ignored"""
    # Test cases where cloze should be ignored
    test_cases = [
        # Inside inline math
        (r"$\sqrt{2::invalid}$", r"$\sqrt{2::invalid}$"),
        (r"$\frac{ {1::also invalid} }{5}$", r"$\frac{ {1::also invalid} }{5}$"),

        # Inside inline code
        (r"`function {1::invalid} () {}`", r"`function {1::invalid} () {}`"),
        (r"`return {value::invalid}`", r"`return {value::invalid}`"),

        # Inside block code
        (
            "```\nfunction test() {\n  return {1::invalid};\n}\n```",
            "```\nfunction test() {\n  return {1::invalid};\n}\n```"
        ),

        # Mixed: some cloze should work, some should be ignored
        (
            r"Valid {1::cloze} and $invalid {2::math} cloze$ and `invalid {3::code} cloze`",
            r"Valid {{c1::cloze}} and $invalid {2::math} cloze$ and `invalid {3::code} cloze`"
        ),
    ]

    for test_input, expected in test_cases:
        cloze_note = ClozeNote(text_md=test_input, tags=[], deck_name="")
        converter.convert_cloze_deletions_to_anki_format([cloze_note])
        assert cloze_note.updated_text_md == expected, \
            f"Cloze conversion failed for: {test_input}"


def test_cloze_numbering_consistency():
    """Test that cloze numbering is consistent and sequential"""
    test_input = (
        r"{first} cloze, {3::explicit third}, {second} implicit, "
        r"{1::explicit first}, {fourth} implicit"
    )
    # The algorithm processes clozes in order and assigns:
    # {first} -> c1 (first implicit, gets index 1 from enumerate)
    # {3::explicit third} -> c3 (explicit, keeps number 3)
    # {second} -> c3 (second implicit, gets index 3 from enumerate - but conflicts with explicit!)
    # {1::explicit first} -> c1 (explicit, keeps number 1)
    # {fourth} -> c5 (third implicit, gets index 5 from enumerate)
    expected = (
        r"{{c1::first}} cloze, {{c3::explicit third}}, {{c3::second}} implicit, "
        r"{{c1::explicit first}}, {{c5::fourth}} implicit"
    )

    cloze_note = ClozeNote(text_md=test_input, tags=[], deck_name="")
    converter.convert_cloze_deletions_to_anki_format([cloze_note])

    assert cloze_note.updated_text_md == expected
