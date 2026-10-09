# Markdown Editor — Documentation (English)

A desktop Markdown editor built with Python and Tkinter, featuring a side-by-side HTML preview that updates as you type.

> **About this project:** this software was *vibe-coded*: developed iteratively with AI assistance, using natural-language prompts, testing, and follow-up changes. The code can be reviewed, adapted, and improved. Choose and add an explicit license to the repository before stating reuse or redistribution terms.

## Background and project goals

This project started with a practical need: a university professor asked for course exercises to be written and submitted in Markdown (`.md`) format. A difficulty quickly became apparent: many Markdown editors did not run on Windows 7, which was still used in some environments, and the available tools did not all offer the same ease of use or the same editing and preview features.

The goal is to provide a straightforward desktop editor with the Markdown source and formatted preview side by side, making it easier to write, edit, and review files without having to learn different tools or rely on an editor that may not be compatible with the operating system.

## Features

- Open, edit, and save `.md` and `.markdown` files.
- Edit the Markdown source and view the formatted result side by side.
- Refresh the preview automatically after a short pause while typing.
- Use the available formatting toolbar to insert Markdown syntax.
- Support common Markdown elements such as headings, bold, italics, blockquotes, links, lists, tables, and code blocks, depending on the configured extensions.
- Preserve the preview's scroll position as far as the HTML component allows.
- Display emoji as images in the preview on systems with limited emoji-font support, if the configured version uses Twemoji. An Internet connection is then required to load the images.

## Requirements

- Python 3.
- The packages listed in `requirements.txt`.
- Tkinter, usually included with Python distributions for Windows.
- An Internet connection for remote emoji images, if enabled.

Compatibility depends on the installed Python and library versions. Windows 7 is end-of-life, and recent Python or dependency releases may not install on it. Use versions compatible with your operating system and obtain them only from trusted sources.

## Installation and launch

There are two ways to run the application:

### Option 1 — Download the executable

Open the repository's GitHub **Releases** section and download the executable for the desired version, if one is available. This lets you launch the application without manually running the Python script. Follow any instructions included with the release.

### Option 2 — Run the program with Python

1. Download or clone the repository.
2. Open a terminal in the project directory containing `app.py`.
3. Install dependencies if they are not already installed:

   ```bash
   python -m pip install -r requirements.txt
   ```

4. Launch the application:

   ```bash
   py app.py
   ```

   Alternatively, if the `py` command is unavailable:

   ```bash
   python app.py
   ```

The executable is available only if a build has been published in the repository's Releases section. Running from source requires Python and the necessary dependencies.

## How to use it

1. Start the application.
2. Choose **File → Open .md file...** to open an existing document.
3. Write or edit Markdown in the left pane.
4. Review the result in the right pane. The preview updates automatically after a short pause.
5. Use the toolbar to insert supported Markdown syntax.
6. Choose **File → Save** to save your changes. For a new document, select a destination when prompted.

### Markdown example

```markdown
# My document

This text is **bold** and this text is *italic*.

> A blockquote.

`inline code`

```python
def greet():
    print("Hello!")
```

- First item
- Second item
```

## Emoji and Windows 7

Windows 7 does not provide native support for many modern emoji. In versions that convert emoji to Twemoji images, they can appear in the preview even when the system font does not support them. Loading remote images requires an Internet connection. Emoji rendering in the source editor still depends on the fonts available on the system.

## Technical notes and limitations

- HTML preview is generated from Markdown using `markdown2` and displayed with `tkinterweb`.
- A short update delay avoids rebuilding the preview for every keystroke.
- Scroll preservation depends on the features supported by the installed `tkinterweb` version.
- Rendering of some Markdown features may vary with enabled extensions and library versions.
- Keep a backup before editing important documents.

## Switching documentation languages

Two documentation files are provided: `README.md` (English) and `README.it.md` (Italian). Open whichever language you prefer. On GitHub, you can use the English README as the repository's main page and link to the Italian version near the top, or do the reverse.

## Contributing

Bug reports, corrections, and improvements are welcome. Test changes on a copy of the document and include your operating system and Python/dependency versions when reporting an issue.

## License

Add a license here (for example, MIT) only after deciding which license applies to the project.
