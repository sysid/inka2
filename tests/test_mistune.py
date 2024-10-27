import mistune
import pytest

from inka2.cli import CONFIG
from inka2.helpers import parse_str_to_bool
from inka2.mistune_plugins.mathjax3 import plugin_mathjax3

MD = mistune.create_markdown(
    plugins=["strikethrough", "footnotes", "table", plugin_mathjax3],
    escape=parse_str_to_bool(CONFIG.get_option_value("defaults", "escape_html")),
)

text = """
$$
\operatorname{ker} f=\{g\in G:f(g)=e_{H}\}{\mbox{.}}
$$

| First Header  | Second Header |
| ------------- | ------- |
| Content Cell  | Content Cell  |
| Content Cell  | Content Cell  |

"""

text2 = """
For manual tests

data directory: '/Users/Q187392/Library/Application Support/Anki2'

```bash
sqlite3 prefs21.db .dump > prefs21_dump.sql
```

inside $\sqrt{2}$ text

This is inline math: $E=mc^2$ and block math:

$$

E = mc^2

$$



$$

\operatorname{ker} f=\{g\in G:f(g)=e_{H}\}{\mbox{.}}

$$



| First Header  | Second Header |

| ------------- | ------------- |

| Content Cell  | Content Cell  |

| Content Cell  | Content Cell  |
"""


# @pytest.mark.skip(reason="manual experimentation")
def test_mistune():
    print(MD(text2))
