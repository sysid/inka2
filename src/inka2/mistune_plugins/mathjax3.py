"""
https://mistune.lepture.com/en/latest/advanced.html

# regex represents:
BLOCK_MATH_PATTERN = (
  r'^ {0,3}'  # line can startswith 0~3 spaces just like other block elements defined in commonmark
  r'\$\$'  # followed by $$
  r'[ \t]*\n'  # this line can contain extra spaces and tabs
  r'(?P<math_text>.+?)'  # this is the math content, MUST use named group
  r'\n\$\$[ \t]*$'  # endswith $$ + extra spaces and tabs
)

# regex represents:
INLINE_MATH_PATTERN = (
  r'\$'  # startswith $
  r'(?!\s)'  # not whitespace
  r'(?P<math_text>.+?)'  # content between `$`, MUST use named group
  r'(?!\s)'  # not whitespace
  r'\$'  # endswith $
)
"""
BLOCK_MATH = r'^ {0,3}\$\$[ \t]*\n(?P<math_text>[\s\S]+?)\n\$\$[ \t]*$'
INLINE_MATH = r'\$(?!\s)(?P<math_text>.+?)(?!\s)\$'


def parse_block_math(block, m, state):
    text = m.group('math_text')
    state.append_token({'type': 'block_math', 'raw': text})
    return m.end() + 1


def parse_inline_math(inline, m, state):
    text = m.group('math_text')
    state.append_token({'type': 'inline_math', 'raw': text})
    return m.end()


def render_block_math(renderer, text):
    """Render block math using MathJax delimiters recognized by Anki."""
    # return '<div class="math">\\[\n' + text + '\n\\]</div>\n'
    return r"\[" + text + r"\]"


def render_inline_math(renderer, text):
    """Render inline math using the same delimiters as the v2 plugin."""
    # return r'<span class="math">\(' + text + r'\)</span>'
    return r"\(" + text + r"\)"


def plugin_mathjax3(md):
    """A mistune plugin to support math. The syntax is used
    by many markdown extensions:

    .. code-block:: text

        Block math is surrounded by $$:

        $$
        f(a)=f(b)
        $$

        Inline math is surrounded by `$`, such as $f(a)=f(b)$

    :param md: Markdown instance
    """
    md.block.register('block_math', BLOCK_MATH, parse_block_math, before='list')
    md.inline.register('inline_math', INLINE_MATH, parse_inline_math, before='link')
    if md.renderer and md.renderer.NAME == 'html':
        md.renderer.register('block_math', render_block_math)
        md.renderer.register('inline_math', render_inline_math)


def math_in_quote(md):
    """Enable block math plugin in block quote."""
    md.block.insert_rule(md.block.block_quote_rules, 'block_math', before='list')


def math_in_list(md):
    """Enable block math plugin in list."""
    md.block.insert_rule(md.block.list_rules, 'block_math', before='list')
