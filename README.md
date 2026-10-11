# Markdown Editor --- Documentation (English)

[🇮🇹 Leggi in italiano](README.it.md)

A desktop Markdown editor written in Python with a Tkinter interface,
side-by-side Markdown editing and HTML preview, automatic preview
updates while typing, and tools for writing and navigating Markdown
documents.

> **Project note:** This software was *vibe-coded*: developed
> iteratively with the assistance of artificial intelligence through
> natural-language instructions, testing, and successive changes.

## Project Background and Goals

The project started from a practical need: a university professor
required course exercises to be written and submitted in Markdown
(`.md`). However, many Markdown editors did not run on Windows 7, and
available tools did not all offer the same ease of use or editing and
preview capabilities.

The goal is to provide a simple desktop editor with Markdown source and
formatted preview side by side, so users can write, edit, and review
documents in one application.

## Features

-   Open, edit, and save `.md` and `.markdown` files.
-   Open a Markdown file directly with the application by passing its
    path at startup or associating `.md` files with the app in Windows.
-   Edit Markdown source and view the HTML preview side by side.
-   Update the preview automatically after a short pause while typing.
-   Synchronize scrolling between the editor and preview.
-   Use the toolbar at the top of the window to apply Markdown
    formatting.
-   Search for text in the current document using a dedicated search
    window, with matching results highlighted.
-   Switch the interface language between English and Italian.
-   Use a centralized translation system designed to make adding more
    languages easier in the future.
-   Support Markdown elements such as headings, bold, italic,
    blockquotes, links, lists, tables, and code blocks, depending on the
    configured extensions.
-   Display emoji in the preview as images when Twemoji is enabled. An
    Internet connection is required to load remote images.

## Requirements

To run the application from source:

-   Python 3 compatible with your operating system.
-   The packages listed in `requirements.txt`.
-   Tkinter, usually included with Python distributions for Windows.
-   An Internet connection for remote emoji images, if enabled.

Compatibility depends on the installed versions of Python and its
libraries. Windows 7 is an unsupported operating system, and recent
Python versions or dependencies may not be compatible with it. Use
versions compatible with your system and download them only from trusted
sources.

## Installation and Launch

There are two ways to use Markdown Editor.

### Option 1 --- Windows executable

Open the repository's
[Releases](https://github.com/arcomipiaceilseno/markdown-win7/releases)
page and download one of the packages available for the release you
want:

-   **`markdown-win7-installer.exe`** --- installer version.
-   **`markdown-win7-portable.exe`** --- portable version, intended to
    run without a traditional installation procedure.

Package availability depends on the files attached to each release.

### Option 2 --- Run from source

1.  Download or clone the repository.

2.  Open a terminal in the project folder containing `main.py`.

3.  Install the dependencies if they are not already installed:

    ``` bash
    py -m pip install -r requirements.txt
    ```

4.  Launch the application:

    ``` bash
    py main.py
    ```

    If the `py` command is unavailable, try:

    ``` bash
    python main.py
    ```

To open a Markdown document by passing its path to the application, run:

``` bash
py main.py "C:\path\to\document.md"
```

Replace the example path with the actual file path. Opening `.md` files
by double-clicking them in File Explorer also requires Windows to be
configured to associate those files with the application.

## Usage

1.  Launch the application, or open an `.md` file directly with it.
2.  To open a document from within the application, select **File → Open
    .md File...**.
3.  Write or edit Markdown in the editor pane.
4.  View the result in the preview pane, which updates automatically
    after a short pause.
5.  Use the top toolbar to insert supported Markdown syntax.
6.  Use the search feature to find text in the current document.
7.  Select English or Italian from the language menu.
8.  Select **File → Save** to save your changes. For a new document,
    choose a path when prompted.

## Markdown Example

``` markdown
# My Document

This is **bold text** and this is *italic text*.

> A blockquote.

`inline code`
```

## Emoji and Windows 7

Windows 7 does not provide native support for many modern emoji. In
versions that convert emoji to Twemoji images, emoji may appear in the
preview even if the system font does not support them. Loading remote
images requires an Internet connection. Emoji rendering in the source
editor depends on the fonts available on the system.

## Technical Notes and Limitations

-   The HTML preview is generated from Markdown using `markdown2` and
    displayed with `tkinterweb`.
-   Delaying preview updates avoids rebuilding the preview after every
    keystroke.
-   Scroll synchronization also depends on the features supported by the
    installed version of `tkinterweb`.
-   The rendering of some Markdown features may vary depending on
    enabled extensions and library versions.
-   Direct file opening depends on the path passed at startup or on the
    file associations configured in Windows.
-   Compatibility with Windows 7 should be verified with the specific
    versions of the application, Python, and its dependencies.
-   Keep a backup before using the application with important documents.

## Documentation Languages

Two documentation files are available: `README.md` (English) and
`README.it.md` (Italian). The link at the top of each document lets you
switch to the other language.

## Contributing

Bug reports, corrections, and improvements are welcome. Before proposing
changes, test them on a copy of your document and include the operating
system and Python/dependency versions you used.

## License

MIT License

Copyright (c) 2026 Andrea Scarano

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
