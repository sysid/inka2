# inka2

[![Downloads](https://static.pepy.tech/badge/inka2)](https://pepy.tech/project/inka2)
[![PyPi](https://img.shields.io/pypi/v/inka2)](https://pypi.org/project/inka2)
[![Tests CI](https://img.shields.io/github/actions/workflow/status/sysid/inka2/test.yml?branch=main)](https://github.com/sysid/inka2/actions/workflows/test.yml)
[![Codecov](https://codecov.io/gh/sysid/inka2/branch/main/graph/badge.svg?token=8IL9MN4FK5)](https://codecov.io/gh/sysid/inka2)

Automatically extract flashcards from Markdown to [Anki](https://apps.ankiweb.net/).
> too useful to let it be unsupported :-)

- [Installation](#installation)
    - [Requirements](#requirements)
- [Why](#why)
- [Features](#features)
- [Usage](#usage)
    - [Creating Cards](#creating-cards)
    - [Adding Cards to Anki](#adding-cards-to-anki)

## Installation

Install **inka2**:

```shell
python3 -m pip install inka2 --upgrade
```

### Requirements

- [Anki](https://apps.ankiweb.net/) >= 2.1.54
- [Python](https://www.python.org/) >= 3.10

## Why

I've been using Anki for a long time, and at some point my notes turned into just lists of question/answer pairs, from
which I then created Anki cards. The process of creating flashcards in Anki took a long time, so I decided to write a
Python script to automate it. With more and more features added, the script has evolved into the command-line tool you
can see now.

**inka2** allows you to use full power of Markdown when creating flashcards. The program is also extensively tested.

## Features

- Cards are automatically added to your Anki deck
- [Basic and Cloze note types support](https://github.com/sysid/inka2/wiki/Creating-cards#frontback-notes)
- [Synchronization of changes with Anki](https://github.com/sysid/inka2/wiki/Synchronization-with-Anki)
- [Configuration via config file](https://github.com/sysid/inka2/wiki/Config)
- [Images support](https://github.com/sysid/inka2/wiki/Creating-cards#images)
- [MathJax support](https://github.com/sysid/inka2/wiki/Mathjax)
- [Code highlight](https://github.com/sysid/inka2/wiki/Code-highlight)
- [Hashing (for better performance)](https://github.com/sysid/inka2/wiki/Hashing)

## Usage

### Creating Cards

In order for the program to be able to separate cards from all the rest of the text in the file, you need to enclose
them between two `---`:

```markdown
---

Deck: Life Questions

Tags: learning life-questions

1. What is the answer to the Ultimate Question of Life, the Universe, and Everything?

> 42

2. If it {{c1::looks like a duck, swims like a duck, and quacks like a duck}}, then it is a {{c2::duck}}.

---
```

You can create any number of such sections in the file.

> :warning: This means that you should avoid using the `---` syntax anywhere else in the file for **inka2** to work correctly.
> There are exceptions, and you can read about them in [documentation](https://github.com/sysid/inka2/wiki/Creating-cards#i-want-to-use-----for-other-purposes).

Inside the section, you can specify the name of the deck to which the cards will be added, and tags for the cards. If
deck name isn't specified, then the one from the [config](https://github.com/sysid/inka2/wiki/Config) is
used (`Default` by default). The deck name is written after `Deck:`, and tags for all cards after `Tags:` with spaces
between each tag.

Two types of notes are supported:

- **Front/Back**: every question starts with number followed by period (e.g. `1.`, `2.` - Markdown ordered list syntax)
  and every line of the answer starts with `>` (Markdown quote syntax). Question and answer can span multiple lines.
- **Cloze**: same as Front/Back notes, Cloze notes start with number followed by period (Markdown ordered list syntax).
  **inka2** supports three versions of syntax for cloze deletions:
    - Anki syntax: `{{c1::hidden text}}`
    - Short explicit syntax: `{1::hidden text}` or `{c1::hidden text}`
    - Short implicit syntax: `{hidden text}`

More info and examples on the [creating cards](https://github.com/sysid/inka2/wiki/Creating-cards) documentation
page.

### Adding Cards to Anki

**inka2** will create custom note types for **Front/Back** and **Cloze** notes. If you want to use different ones, you
can change note types in the [config](https://github.com/sysid/inka2/wiki/Config).

Add cards from the file:

```commandline
inka2 collect path/to/cards.md
```

Or from all *Markdown* files in a directory:

```commandline
inka2 collect path/to/directory
```

You can also pass multiple paths at once:

```commandline
inka2 collect path/to/cards.md path/to/folder
```

You can find more information on the [documentation page](https://github.com/sysid/inka2/wiki/Adding-cards-to-Anki).
