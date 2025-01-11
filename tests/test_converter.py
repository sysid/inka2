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
    """BasicNote object with dummy data"""
    return BasicNote(front_md="dummy", back_md="dummy", tags=[], deck_name="")


convert_cloze_test_cases = {
    # SHORT IMPLICIT
    # one
    "Some {cloze question}": "Some {{c1::cloze question}}",
    # with hint
    "Some {cloze question::really helpful hint}": "Some {{c1::cloze question::really helpful hint}}",
    # two
    "Some {cloze question}\n\n{another} one": "Some {{c1::cloze question}}\n\n{{c2::another}} one",
    # around inline math
    r"math: {$\sqrt{2}$}": r"math: {{c1::$\sqrt{2}$}}",
    # around block math
    r"math: {$$\frac{\sqrt{2}}{15}$$}": r"math: {{c1::$$\frac{\sqrt{2}}{15}$$}}",
    # around inline code
    r"inline code: {`func() int { return {12} }`}": r"inline code: {{c1::`func() int { return {12} }`}}",
    # around block code
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
    ),
    # check order correctness with multiple cloze deletions around math and code
    (
        r"some math {$\sqrt{2}$}, code {`func() int`}, "
        r"more code {`defer resp.body.Close()`} and more math {$\frac{1}{5}$}"
    ): (
        r"some math {{c1::$\sqrt{2}$}}, code {{c2::`func() int`}},"
        r" more code {{c3::`defer resp.body.Close()`}} and more math {{c4::$\frac{1}{5}$}}"
    ),
    # inside inline math -> ignored
    r"math: $\sqrt{2}$": r"math: $\sqrt{2}$",
    # inside block math -> ignored
    r"math: $$\frac{\sqrt{2}}{15}$$": r"math: $$\frac{\sqrt{2}}{15}$$",
    # inside inline code -> ignored
    r"inline code: `func() int { return {12} }`": r"inline code: `func() int { return {12} }`",
    # inside code block -> ignored
    (
        "Code:\n"
        "```\n"
        "func main() {\n"
        '\tdefer func() { fmt.Println("exited") }\n'
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
        '\tdefer func() { fmt.Println("exited") }\n'
        '\tdatabase.DB, err := sql.Open("pgx", os.Getenv("POSTGRES_URL"))\n'
        "\tif err != nil {\n"
        "\t\tlog.Fatal(err)\n"
        "\t}\n"
        "}\n"
        "```\n"
    ),
    # SHORT EXPLICIT
    # one
    "Some {1::cloze question}": "Some {{c1::cloze question}}",
    # with hint
    "Some {1::cloze question::really helpful hint}": "Some {{c1::cloze question::really helpful hint}}",
    # with 'c'
    "Some {c1::cloze question}": "Some {{c1::cloze question}}",
    # two
    "Some {2::cloze question}\n\n{1::another} one": "Some {{c2::cloze question}}\n\n{{c1::another}} one",
    # around inline math
    r"math: {1::$\sqrt{2}$}": r"math: {{c1::$\sqrt{2}$}}",
    # around block math
    r"math: {1::$$\frac{\sqrt{2}}{15}$$}": r"math: {{c1::$$\frac{\sqrt{2}}{15}$$}}",
    # around inline code
    r"inline code: {1::`func() int { return {12} }`}": r"inline code: {{c1::`func() int { return {12} }`}}",
    # around block code
    (
        "Code:\n"
        "{1::\n"
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
    ),
    # inside inline math -> ignored
    r"math: $\sqrt{2::15}$": r"math: $\sqrt{2::15}$",
    # inside block math -> ignored
    r"math: $$\frac{1::\sqrt{2}}{12::15}$$": r"math: $$\frac{1::\sqrt{2}}{12::15}$$",
    # inside inline code -> ignored
    r"inline code: `func() int { return {1::12} }`": r"inline code: `func() int { return {1::12} }`",
    # inside code block -> ignored
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
    ),
    # ANKI FORMAT
    # one
    "Some {{c1::cloze question}}": "Some {{c1::cloze question}}",
    # with hint
    "Some {{c1::cloze question::really helpful hint}}": "Some {{c1::cloze question::really helpful hint}}",
    # two
    "Some {{c2::cloze question}}\n\n{{c1::another}} one": "Some {{c2::cloze question}}\n\n{{c1::another}} one",
    # inside inline math -> ignored
    r"math: $\sqrt{ {{c1::15}} } $": r"math: $\sqrt{ {{c1::15}} } $",
    # inside block math -> ignored
    r"math: $$\frac{ {{1::\sqrt{2}}} }{ {{c12::15}} }$$": r"math: $$\frac{ {{1::\sqrt{2}}} }{ {{c12::15}} }$$",
    # block math and inline math -> ignored
    (
        r"math: $\sqrt{ {{c1::15}} } $ $$\frac{ {{1::\sqrt{2}}} }{ {{c12::15}} }$$"
    ): r"math: $\sqrt{ {{c1::15}} } $ $$\frac{ {{1::\sqrt{2}}} }{ {{c12::15}} }$$",
    # inside inline code -> ignored
    r"inline code: `func() int { return {{c1::12}} }`": r"inline code: `func() int { return {{c1::12}} }`",
    # inside code block -> ignored
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
    ),
    # inline and block code -> ignored
    (
        "Code of `{simple} {{c2::function}}`:\n"
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
        "Code of `{simple} {{c2::function}}`:\n"
        "```\n"
        "func main() {\n"
        '\tdefer func() { fmt.Println("exited") }\n'
        '\tdatabase.DB, err := {{c1::sql.Open("pgx", os.Getenv("POSTGRES_URL"))}}\n'
        "\tif err != nil {\n"
        "\t\tlog.Fatal(err)\n"
        "\t}\n"
        "}\n"
        "```\n"
    ),
    # ALL THREE
    # random stuff
    (
        r"{Paris} is the capital and most populous city of {2::France},"
        r" with a estimated population of {2,148,271} residents"
    ): (
        r"{{c1::Paris}} is the capital and most populous city of {{c2::France}},"
        r" with a estimated population of {{c3::2,148,271}} residents"
    ),
    (
        r"{Paris} is the capital and most populous city of {3::France},"
        r" with a estimated population of {2,148,271} residents"
    ): (
        r"{{c1::Paris}} is the capital and most populous city of {{c3::France}},"
        r" with a estimated population of {{c3::2,148,271}} residents"
    ),
    (
        r"{c3::Paris} is the capital and most populous city of {3::France},"
        r" with a {{c1::estimated::my hint}} population of {2,148,271} residents"
    ): (
        r"{{c3::Paris}} is the capital and most populous city of {{c3::France}},"
        r" with a {{c1::estimated::my hint}} population of {{c4::2,148,271}} residents"
    ),
}

"""
refactoring of mathjax3.py results in the following edge case differences.
I am not aware of a clear specification what is correct.
mathjax3.py basically takes the builtin "math" plugin and changes only the delimiters.
"""
md_to_html_test_cases = {
    "some text here": "<p>some text here</p>",
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
    ),
    "some text here\n" "and more text": "<p>some text here\nand more text</p>",
    "some text here\n" "\n" "more text": "<p>some text here</p><p>more text</p>",
    # # inline mathjax
    r"$\sqrt{5}$": r'<p><span class="math">\(\sqrt{5}\)</span></p>',
    r"$\sqrt{5} $": r'<p><span class="math">\(\sqrt{5} \)</span></p>',
    # r"$ \sqrt{5}$": r"<p>\( \sqrt{5}\)</p>",  # TODO: fix this
    r"$multiple words$": r'<p><span class="math">\(multiple words\)</span></p>',
    r"weird$mathjax$more word$1$s": r'<p>weird<span class="math">\(mathjax\)</span>more word<span class="math">\(1\)</span>s</p>',
    "$\\sqrt{5}\n$": "<p>$\\sqrt{5}\n$</p>",
    "$\n\\sqrt{5}$": "<p>$\n\\sqrt{5}$</p>",
    r"\$\sqrt{5}$": r"<p>$\sqrt{5}$</p>",
    # r"$\sqrt{5}\$": r"<p>$\sqrt{5}$</p>",  # TODO: fix this
    r"\$\sqrt{5}\$": r"<p>$\sqrt{5}$</p>",
    r"text $$ here": r"<p>text $$ here</p>",
    # r"\$$$$": r"<p>$\(\)$</p>",  # TODO: fix this
    r"\$$\sqrt{2}$$": r'<p>$<span class="math">\(\sqrt{2}\)</span>$</p>',
    # r"$\$\sqrt{2}$$": r"<p>\(\$\sqrt{2}\)$</p>",  # TODO: fix this
    # r"$$\sqrt{2}\$$": r"<p>\(\)\sqrt{2}$$</p>",  # TODO: fix this
    # r"$$\sqrt{2}$\$": r"<p>\(\)\sqrt{2}$$</p>",  # TODO: fix this
    # r"\$\$\sqrt{2}$$": r"<p>$$\sqrt{2}\(\)</p>",  # TODO: fix this
    # r"$$\sqrt{2}\$\$": r"<p>\(\)\sqrt{2}$$</p>",  # TODO: fix this
    "$$$": r'<p><span class="math">\($\)</span></p>',
    # block mathjax
    # "$$$$": r"<p>\[\]</p>",  # TODO: wrong?
    # r"$$\sqrt{2}$$": r"<p>\[\sqrt{2}\]</p>",  # TODO: wrong?
    # r"inside $$\sqrt{2}$$ text": r"<p>inside \[\sqrt{2}\] text</p>",  # TODO: wrong?
    # r"$$ text here $$": r"<p>\[ text here \]</p>",  # TODO: wrong?
    # "$$multi\nline$$": "<p>\\[multi\nline\\]</p>",  # TODO: wrong?
    "$$\n\\sqrt{2}\n\\frac{1}{2}\n$$": '<div class="math">\\[\n\\sqrt{2}\n\\frac{1}{2}\n\\]</div>',
    # "$$\\sqrt{2}$$ some text in between $$\n\\sqrt{2}\n\\frac{1}{2}\n$$": (
    #     "<p>\\[\\sqrt{2}\\] some text in between \\[\n\\sqrt{2}\n\\frac{1}{2}\n\\]</p>"
    # ),  # TODO: unclear what should be correct
    # both inline and block mathjax
    # "$$\\sqrt{2}$$ some text $\\sqrt{6}$ in between $$\n\\sqrt{2}\n\\frac{1}{2}\n$$": (
    #     "<p>\\[\\sqrt{2}\\] some text \\(\\sqrt{6}\\) in between \\[\n\\sqrt{2}\n\\frac{1}{2}\n\\]</p>"
    # ),
}


@pytest.mark.parametrize("test_input, expected", convert_cloze_test_cases.items())
def test_convert_cloze_deletions_to_anki_format(test_input, expected):
    cloze_note = ClozeNote(text_md=test_input, tags=[], deck_name="")

    converter.convert_cloze_deletions_to_anki_format([cloze_note])

    assert cloze_note.updated_text_md == expected


def test_convert_cloze_deletions_to_anki_format_works_with_multiple_notes():
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
    html = converter._convert_md_to_html(test_input, md)

    assert html == expected


def test_convert_md_to_html_no_html_escaping(basic_note, md):
    test_input = (
        """<span style="font-size: 9pt;">This text will be 9pt in size.</span>"""
    )
    expected = (
        """<p><span style="font-size: 9pt;">This text will be 9pt in size.</span></p>"""
    )
    html = converter._convert_md_to_html(test_input, md)
    assert html == expected


def test_convert_cards_to_html_works_with_multiple_cards(md):
    text1 = r"inside $\sqrt{2}$ text"
    text2 = "1. Item1\n" "2. Item2\n" "3. Item3\n"
    basic_note1 = BasicNote(front_md=text1, back_md=text2, tags=[], deck_name="")
    basic_note2 = BasicNote(front_md=text2, back_md=text1, tags=[], deck_name="")
    cloze_note = ClozeNote(text_md="Some question {{c1::42}}", tags=[], deck_name="")
    expected1 = r'<p>inside <span class="math">\(\sqrt{2}\)</span> text</p>'
    expected2 = "<ol><li>Item1</li><li>Item2</li><li>Item3</li></ol>"
    expected3 = "<p>Some question {{c1::42}}</p>"

    converter.convert_notes_to_html([basic_note1, basic_note2, cloze_note], md)

    assert basic_note1.front_html == expected1
    assert basic_note1.back_html == expected2
    assert basic_note2.front_html == expected2
    assert basic_note2.back_html == expected1
    assert cloze_note.text_html == expected3
