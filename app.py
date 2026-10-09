import os
import re
import tkinter as tk
from html.parser import HTMLParser
from html import escape
from tkinter import filedialog, messagebox, ttk

import emoji
import markdown2
from tkinterweb import HtmlFrame


# Twemoji images make emojis readable even on systems without an emoji font,
# such as some Windows 7 installations. Images are loaded via Internet.
TWEMOJI_BASE_URL = (
    "https://cdn.jsdelivr.net/gh/jdecked/twemoji@17.0.3/assets/72x72/"
)


class EmojiHTMLRenderer(HTMLParser):
    """Replaces emoji characters with Twemoji images in the rendered HTML."""

    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.parts = []
        self._protected_tags = []

    def handle_starttag(self, tag, attrs):
        self.parts.append(self.get_starttag_text() or "<{}>".format(tag))
        if tag.lower() in ("script", "style"):
            self._protected_tags.append(tag.lower())

    def handle_startendtag(self, tag, attrs):
        self.parts.append(self.get_starttag_text() or "<{} />".format(tag))

    def handle_endtag(self, tag):
        self.parts.append("</{}>".format(tag))
        tag = tag.lower()
        if tag in self._protected_tags:
            # Removes the most recent opening of the same element.
            for index in range(len(self._protected_tags) - 1, -1, -1):
                if self._protected_tags[index] == tag:
                    del self._protected_tags[index]
                    break

    def handle_data(self, data):
        if self._protected_tags:
            self.parts.append(data)
            return

        matches = emoji.emoji_list(data)
        if not matches:
            self.parts.append(data)
            return

        cursor = 0
        for match in matches:
            start = match["match_start"]
            end = match["match_end"]
            character = match["emoji"]
            self.parts.append(data[cursor:start])

            # Twemoji omits FE0E/FE0F from PNG filenames.
            codepoints = "-".join(
                "{:x}".format(ord(char))
                for char in character
                if char not in ("\ufe0e", "\ufe0f")
            )
            if codepoints:
                label = escape(character, quote=True)
                src = TWEMOJI_BASE_URL + codepoints + ".png"
                self.parts.append(
                    '<img class="emoji" src="{}" alt="{}" title="{}">'.format(
                        src, label, label
                    )
                )
            else:
                self.parts.append(character)
            cursor = end

        self.parts.append(data[cursor:])

    def handle_entityref(self, name):
        self.parts.append("&{};".format(name))

    def handle_charref(self, name):
        self.parts.append("&#{};".format(name))

    def handle_comment(self, data):
        self.parts.append("<!--{}-->".format(data))

    def handle_decl(self, decl):
        self.parts.append("<!{}>".format(decl))

    def handle_pi(self, data):
        self.parts.append("<?{}>".format(data))

    def get_html(self):
        return "".join(self.parts)


def render_emojis_in_html(html_text):
    """Returns HTML with emojis as images, leaving Markdown unchanged."""
    parser = EmojiHTMLRenderer()
    parser.feed(html_text)
    parser.close()
    return parser.get_html()


class MarkdownViewerApp:
    """Markdown editor with toolbar and updated preview without reloading the page."""

    PREVIEW_CSS = r"""
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
            padding: 15px 22px;
            line-height: 1.65;
            color: #24292e;
            background: #ffffff;
            overflow-wrap: anywhere;
        }
        h1, h2, h3, h4, h5, h6 {
            border-bottom: 1px solid #eaecef;
            padding-bottom: .3em;
            margin-top: 1.4em;
        }
        h1:first-child, h2:first-child, h3:first-child { margin-top: .2em; }
        a { color: #0969da; }
        code {
            background: #f6f8fa;
            padding: .15em .35em;
            border-radius: 4px;
            font-family: Consolas, "Liberation Mono", monospace;
        }
        pre {
            background: #f6f8fa;
            padding: 12px 14px;
            overflow: auto;
            border: 1px solid #d8dee4;
            border-radius: 6px;
        }
        pre code { background: transparent; padding: 0; }
        blockquote {
            color: #57606a;
            border-left: 4px solid #d0d7de;
            padding: 2px 0 2px 14px;
            margin-left: 0;
        }
        table { border-collapse: collapse; width: 100%; margin: 16px 0; }
        th, td { border: 1px solid #d0d7de; padding: 6px 12px; }
        tr:nth-child(even) { background: #f6f8fa; }
        img { max-width: 100%; height: auto; }
        img.emoji {
            display: inline;
            width: 1.2em;
            height: 1.2em;
            max-width: 1.2em;
            vertical-align: -0.2em;
            border: 0;
        }
        hr { border: 0; border-top: 1px solid #d8dee4; margin: 24px 0; }
        li { margin: 3px 0; }
    """

    def __init__(self, root):
        self.root = root
        self.root.geometry("1250x780")
        self.root.minsize(900, 600)

        self.current_filepath = None
        self.is_modified = False
        self._loading = False
        self._preview_ready = False
        self._debounce_timer = None

        self.create_menu()
        self.create_layout()
        self.bind_shortcuts()

        self.root.protocol("WM_DELETE_WINDOW", self.exit_app)
        self.update_window_title()
        self.update_status()
        self.update_preview()

    # ------------------------------------------------------------------
    # Interface
    # ------------------------------------------------------------------
    def create_menu(self):
        menubar = tk.Menu(self.root)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Nuovo", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Apri file .md...", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Salva", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Salva con nome...", command=self.save_file_as, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Esci", command=self.exit_app)
        menubar.add_cascade(label="File", menu=file_menu)

        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Grassetto", command=self.make_bold, accelerator="Ctrl+B")
        edit_menu.add_command(label="Corsivo", command=self.make_italic, accelerator="Ctrl+I")
        edit_menu.add_command(label="Link", command=self.insert_link, accelerator="Ctrl+K")
        edit_menu.add_separator()
        edit_menu.add_command(label="Annulla", command=lambda: self.text_editor.event_generate("<<Undo>>"), accelerator="Ctrl+Z")
        edit_menu.add_command(label="Ripeti", command=lambda: self.text_editor.event_generate("<<Redo>>"), accelerator="Ctrl+Y")
        menubar.add_cascade(label="Modifica", menu=edit_menu)

        self.root.config(menu=menubar)

    def create_layout(self):
        self.paned_window = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True, padx=6, pady=(6, 2))

        # Left panel: Markdown source
        left_frame = ttk.Frame(self.paned_window, padding=4)
        self.paned_window.add(left_frame, weight=1)

        ttk.Label(left_frame, text="Sorgente Markdown", font=("Arial", 11, "bold")).pack(
            anchor="w", padx=4, pady=(2, 5)
        )
        self.create_toolbar(left_frame)

        editor_frame = ttk.Frame(left_frame)
        editor_frame.pack(fill=tk.BOTH, expand=True)

        self.text_editor = tk.Text(
            editor_frame,
            wrap=tk.WORD,
            font=("Consolas", 10),
            undo=True,
            maxundo=-1,
            autoseparators=True,
            padx=8,
            pady=8,
        )
        editor_scroll_y = ttk.Scrollbar(editor_frame, orient=tk.VERTICAL, command=self.text_editor.yview)
        editor_scroll_x = ttk.Scrollbar(editor_frame, orient=tk.HORIZONTAL, command=self.text_editor.xview)
        self.text_editor.configure(yscrollcommand=editor_scroll_y.set, xscrollcommand=editor_scroll_x.set)
        self.text_editor.grid(row=0, column=0, sticky="nsew")
        editor_scroll_y.grid(row=0, column=1, sticky="ns")
        editor_scroll_x.grid(row=1, column=0, sticky="ew")
        editor_frame.rowconfigure(0, weight=1)
        editor_frame.columnconfigure(0, weight=1)

        self.text_editor.bind("<<Modified>>", self.on_text_modified)
        self.text_editor.bind("<KeyRelease>", self.on_cursor_activity, add="+")
        self.text_editor.bind("<ButtonRelease-1>", self.on_cursor_activity, add="+")

        # Right panel: Persistent HTML preview
        right_frame = ttk.Frame(self.paned_window, padding=4)
        self.paned_window.add(right_frame, weight=1)
        ttk.Label(right_frame, text="Anteprima formattata", font=("Arial", 11, "bold")).pack(
            anchor="w", padx=4, pady=(2, 5)
        )
        self.html_view = HtmlFrame(
            right_frame,
            messages_enabled=False,
            images_enabled=True,
            caches_enabled=True,
        )
        self.html_view.pack(fill=tk.BOTH, expand=True)

        self.status_label = ttk.Label(self.root, text="", anchor="w", relief=tk.SUNKEN, padding=(7, 3))
        self.status_label.pack(fill=tk.X, side=tk.BOTTOM, padx=6, pady=(2, 6))

    def create_toolbar(self, parent):
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, padx=2, pady=(0, 6))

        commands = [
            ("** B **", self.make_bold),
            ("* I *", self.make_italic),
            ("~~ S ~~", self.make_strikethrough),
            ("H1", lambda: self.apply_line_prefix("# ")),
            ("H2", lambda: self.apply_line_prefix("## ")),
            ("❝ Citazione", lambda: self.apply_line_prefix("> ")),
            ("` Codice `", self.make_inline_code),
            ("Blocco codice", self.make_code_block),
            ("• Elenco", lambda: self.apply_line_prefix("- ")),
            ("1. Elenco", lambda: self.apply_line_prefix("1. ")),
            ("Link", self.insert_link),
            ("Immagine", self.insert_image),
            ("— Separatore", self.insert_horizontal_rule),
        ]
        columns = 4
        for column in range(columns):
            toolbar.columnconfigure(column, weight=1)
        for index, (label, command) in enumerate(commands):
            button = ttk.Button(toolbar, text=label, command=command)
            button.grid(row=index // columns, column=index % columns, sticky="ew", padx=2, pady=2)

    def bind_shortcuts(self):
        # Bindings on the text widget take precedence over standard Tk bindings
        # (for example Ctrl+B, which could otherwise move the cursor).
        editor_shortcuts = {
            "<Control-n>": self.new_file,
            "<Control-o>": self.open_file,
            "<Control-s>": self.save_file,
            "<Control-Shift-S>": self.save_file_as,
            "<Control-b>": self.make_bold,
            "<Control-i>": self.make_italic,
            "<Control-k>": self.insert_link,
            "<Control-Shift-c>": self.make_code_block,
        }
        for sequence, command in editor_shortcuts.items():
            self.text_editor.bind(sequence, lambda _event, cmd=command: self.run_shortcut(cmd))

        self.root.bind_all("<Control-n>", lambda _event: self.run_shortcut(self.new_file))
        self.root.bind_all("<Control-o>", lambda _event: self.run_shortcut(self.open_file))
        self.root.bind_all("<Control-s>", lambda _event: self.run_shortcut(self.save_file))
        self.root.bind_all("<Control-Shift-S>", lambda _event: self.run_shortcut(self.save_file_as))
        self.root.bind_all("<Control-b>", lambda _event: self.run_shortcut(self.make_bold))
        self.root.bind_all("<Control-i>", lambda _event: self.run_shortcut(self.make_italic))
        self.root.bind_all("<Control-k>", lambda _event: self.run_shortcut(self.insert_link))
        self.root.bind_all("<Control-Shift-c>", lambda _event: self.run_shortcut(self.make_code_block))

    @staticmethod
    def run_shortcut(command):
        command()
        return "break"

    # ------------------------------------------------------------------
    # Markdown text editing
    # ------------------------------------------------------------------
    def selected_text(self):
        try:
            return self.text_editor.get("sel.first", "sel.last")
        except tk.TclError:
            return ""

    def wrap_selection(self, prefix, suffix=None, placeholder="testo"):
        """Wraps the selection in Markdown markers or inserts a selected example."""
        if suffix is None:
            suffix = prefix
        try:
            start = self.text_editor.index("sel.first")
            end = self.text_editor.index("sel.last")
            selected = self.text_editor.get(start, end)
            replacement = prefix + selected + suffix
            self.text_editor.delete(start, end)
            self.text_editor.insert(start, replacement)
            inner_start = f"{start}+{len(prefix)}c"
            inner_end = f"{inner_start}+{len(selected)}c"
            self.text_editor.tag_remove("sel", "1.0", tk.END)
            self.text_editor.tag_add("sel", inner_start, inner_end)
            self.text_editor.mark_set(tk.INSERT, inner_end)
        except tk.TclError:
            start = self.text_editor.index(tk.INSERT)
            replacement = prefix + placeholder + suffix
            self.text_editor.insert(start, replacement)
            inner_start = f"{start}+{len(prefix)}c"
            inner_end = f"{inner_start}+{len(placeholder)}c"
            self.text_editor.tag_remove("sel", "1.0", tk.END)
            self.text_editor.tag_add("sel", inner_start, inner_end)
            self.text_editor.mark_set(tk.INSERT, inner_end)
        self.text_editor.focus_set()
        self.update_status()

    def make_bold(self):
        self.wrap_selection("**", "**", "testo in grassetto")

    def make_italic(self):
        self.wrap_selection("*", "*", "testo in corsivo")

    def make_strikethrough(self):
        self.wrap_selection("~~", "~~", "testo barrato")

    def make_inline_code(self):
        self.wrap_selection("`", "`", "codice")

    def apply_line_prefix(self, prefix):
        """Adds the prefix to selected lines, or to the current line."""
        try:
            start = self.text_editor.index("sel.first linestart")
            selection_end = self.text_editor.index("sel.last")
            # If selection ends at the start of a line, do not include that empty line.
            if selection_end.endswith(".0") and selection_end != start:
                previous_char = self.text_editor.index(f"{selection_end}-1c")
                end = self.text_editor.index(f"{previous_char} lineend")
            else:
                end = self.text_editor.index("sel.last lineend")
        except tk.TclError:
            start = self.text_editor.index("insert linestart")
            end = self.text_editor.index("insert lineend")

        original = self.text_editor.get(start, end)
        lines = original.splitlines()
        if not lines:
            lines = [""]

        transformed = []
        for line in lines:
            if prefix.startswith("#"):
                # Replaces the heading level already present, instead of accumulating #.
                line = re.sub(r"^\s{0,3}#{1,6}\s+", "", line)
                transformed.append(prefix + line)
            elif prefix == "> ":
                transformed.append(line[2:] if line.startswith("> ") else prefix + line)
            elif prefix in ("- ", "1. "):
                transformed.append(prefix + re.sub(r"^\s*(?:[-*+]\s+|\d+\.\s+)", "", line))
            else:
                transformed.append(prefix + line)

        replacement = "\n".join(transformed)
        self.text_editor.delete(start, end)
        self.text_editor.insert(start, replacement)
        self.text_editor.tag_remove("sel", "1.0", tk.END)
        self.text_editor.tag_add("sel", start, f"{start}+{len(replacement)}c")
        self.text_editor.mark_set(tk.INSERT, f"{start}+{len(replacement)}c")
        self.text_editor.focus_set()
        self.update_status()

    def make_code_block(self):
        try:
            start = self.text_editor.index("sel.first")
            end = self.text_editor.index("sel.last")
            selected = self.text_editor.get(start, end)
            replacement = "```\n" + selected + "\n```"
            self.text_editor.delete(start, end)
            self.text_editor.insert(start, replacement)
            code_start = f"{start}+4c"
            code_end = f"{code_start}+{len(selected)}c"
            self.text_editor.tag_remove("sel", "1.0", tk.END)
            self.text_editor.tag_add("sel", code_start, code_end)
            self.text_editor.mark_set(tk.INSERT, code_end)
        except tk.TclError:
            start = self.text_editor.index(tk.INSERT)
            sample = "scrivi qui il codice"
            replacement = "```\n" + sample + "\n```"
            self.text_editor.insert(start, replacement)
            self.text_editor.tag_remove("sel", "1.0", tk.END)
            self.text_editor.tag_add("sel", f"{start}+4c", f"{start}+{4 + len(sample)}c")
            self.text_editor.mark_set(tk.INSERT, f"{start}+{4 + len(sample)}c")
        self.text_editor.focus_set()
        self.update_status()

    def insert_link(self):
        try:
            start = self.text_editor.index("sel.first")
            end = self.text_editor.index("sel.last")
            selected = self.text_editor.get(start, end)
            replacement = f"[{selected}](https://)"
            self.text_editor.delete(start, end)
            self.text_editor.insert(start, replacement)
            url_start = f"{start}+{len(selected) + 3}c"
            self.text_editor.tag_remove("sel", "1.0", tk.END)
            self.text_editor.tag_add("sel", url_start, f"{url_start}+8c")
            self.text_editor.mark_set(tk.INSERT, f"{url_start}+8c")
        except tk.TclError:
            start = self.text_editor.index(tk.INSERT)
            label = "testo del link"
            url = "https://esempio.com"
            replacement = f"[{label}]({url})"
            self.text_editor.insert(start, replacement)
            url_start = f"{start}+{len(label) + 3}c"
            self.text_editor.tag_remove("sel", "1.0", tk.END)
            self.text_editor.tag_add("sel", url_start, f"{url_start}+{len(url)}c")
            self.text_editor.mark_set(tk.INSERT, f"{url_start}+{len(url)}c")
        self.text_editor.focus_set()
        self.update_status()

    def insert_image(self):
        self.wrap_selection("![", "](https://esempio.com/immagine.png)", "descrizione immagine")

    def insert_horizontal_rule(self):
        insert_at = self.text_editor.index(tk.INSERT)
        line_start = self.text_editor.index("insert linestart")
        line_end = self.text_editor.index("insert lineend")
        line_content = self.text_editor.get(line_start, line_end)
        prefix = "" if not line_content.strip() else "\n"
        suffix = "" if insert_at == "1.0" else "\n"
        self.text_editor.insert(insert_at, prefix + "---" + suffix)
        self.text_editor.focus_set()
        self.update_status()

    # ------------------------------------------------------------------
    # File: new, open, save
    # ------------------------------------------------------------------
    def new_file(self):
        if not self.confirm_discard_changes():
            return
        self.current_filepath = None
        self._loading = True
        self.text_editor.delete("1.0", tk.END)
        self.text_editor.edit_modified(False)
        self._loading = False
        self.is_modified = False
        self.update_window_title()
        self.update_preview_now()
        self.update_status()

    def open_file(self):
        filepath = filedialog.askopenfilename(
            title="Apri un file Markdown",
            filetypes=[("File Markdown", "*.md *.markdown *.mdown *.mkd"), ("Tutti i file", "*.*")],
        )
        if not filepath:
            return
        if not self.confirm_discard_changes():
            return

        try:
            with open(filepath, "r", encoding="utf-8-sig") as file:
                content = file.read()
            self._loading = True
            self.text_editor.delete("1.0", tk.END)
            self.text_editor.insert("1.0", content)
            self.text_editor.edit_modified(False)
            self._loading = False

            self.current_filepath = filepath
            self.is_modified = False
            self._cancel_preview_timer()
            self.update_window_title()
            self.update_preview_now()
            self.update_status()
        except (OSError, UnicodeError) as exc:
            self._loading = False
            messagebox.showerror("Errore di apertura", f"Non riesco a leggere il file.\n\n{exc}", parent=self.root)

    def save_file(self):
        return self._save_to_path(self.current_filepath)

    def save_file_as(self):
        return self._save_to_path(None)

    def _save_to_path(self, filepath):
        if not filepath:
            filepath = filedialog.asksaveasfilename(
                title="Salva il documento Markdown",
                defaultextension=".md",
                filetypes=[("File Markdown", "*.md"), ("Tutti i file", "*.*")],
                initialfile=os.path.basename(self.current_filepath) if self.current_filepath else "documento.md",
            )
            if not filepath:
                return False

        content = self.text_editor.get("1.0", "end-1c")
        try:
            with open(filepath, "w", encoding="utf-8", newline="") as file:
                file.write(content)
        except OSError as exc:
            messagebox.showerror("Errore di salvataggio", f"Non riesco a salvare il file.\n\n{exc}", parent=self.root)
            return False

        self.current_filepath = filepath
        self.is_modified = False
        self.text_editor.edit_modified(False)
        self.update_window_title()
        self.update_status()
        messagebox.showinfo("Salvataggio", "File salvato correttamente.", parent=self.root)
        return True

    def confirm_discard_changes(self):
        if not self.is_modified:
            return True
        answer = messagebox.askyesnocancel(
            "Modifiche non salvate",
            "Vuoi salvare le modifiche prima di continuare?",
            parent=self.root,
        )
        if answer is None:
            return False
        if answer is True:
            return self.save_file()
        return True

    def exit_app(self):
        if self.confirm_discard_changes():
            if self._debounce_timer is not None:
                try:
                    self.root.after_cancel(self._debounce_timer)
                except tk.TclError:
                    pass
            self.root.destroy()

    # ------------------------------------------------------------------
    # Preview: load document once, then change content only
    # ------------------------------------------------------------------
    def on_text_modified(self, _event=None):
        if not self.text_editor.edit_modified():
            return
        self.text_editor.edit_modified(False)
        if self._loading:
            return
        self.is_modified = True
        self.update_window_title()
        self.update_status()
        self.schedule_preview_update()

    def on_cursor_activity(self, _event=None):
        self.update_status()

    def schedule_preview_update(self):
        self._cancel_preview_timer()
        self._debounce_timer = self.root.after(250, self.update_preview)

    def _cancel_preview_timer(self):
        if self._debounce_timer is not None:
            try:
                self.root.after_cancel(self._debounce_timer)
            except tk.TclError:
                pass
            self._debounce_timer = None

    def update_preview_now(self):
        self._cancel_preview_timer()
        self.update_preview()

    def markdown_to_html(self):
        markdown_text = self.text_editor.get("1.0", "end-1c")
        html_body = markdown2.markdown(
            markdown_text,
            extras=[
                "fenced-code-blocks",
                "tables",
                "strike",
                "task_list",
                "code-friendly",
                "header-ids",
                "footnotes",
            ],
        )
        return render_emojis_in_html(html_body)

    def _full_preview_html(self, html_body):
        return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<!-- Twemoji Emojis: graphics released under CC BY 4.0 license: https://github.com/jdecked/twemoji -->
<style>{self.PREVIEW_CSS}</style>
</head>
<body><main id="markdown-content">{html_body}</main></body>
</html>"""

    def update_preview(self):
        self._debounce_timer = None
        html_body = self.markdown_to_html()
        scroll_pos = self._get_preview_scroll()

        if not self._preview_ready:
            self.html_view.load_html(self._full_preview_html(html_body))
            self._preview_ready = True
            return

        # This modification only updates the central node: the page and its CSS
        # remain loaded, so scrolling is not reset on every keystroke.
        try:
            content_node = self.html_view.document.getElementById("markdown-content")
            content_node.innerHTML = html_body
            if scroll_pos is not None:
                self.root.after_idle(lambda pos=scroll_pos: self._restore_preview_scroll(pos))
        except Exception:
            # Fallback compatibility with older versions of TkinterWeb:
            # reloads HTML while still trying to restore scroll position.
            self.html_view.load_html(self._full_preview_html(html_body))
            if scroll_pos is not None:
                self.root.after(60, lambda pos=scroll_pos: self._restore_preview_scroll(pos))

    def _get_preview_scroll(self):
        try:
            return self.html_view.html.yview()
        except Exception:
            return None

    def _restore_preview_scroll(self, position):
        try:
            if position:
                self.html_view.html.yview_moveto(position[0])
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Window state and status bar
    # ------------------------------------------------------------------
    def update_window_title(self):
        filename = self.current_filepath if self.current_filepath else "Nuovo documento"
        modified_mark = " *" if self.is_modified else ""
        self.root.title(f"Markdown Editor — {filename}{modified_mark}")

    def update_status(self):
        try:
            line, column = self.text_editor.index(tk.INSERT).split(".")
        except Exception:
            line, column = "1", "0"
        state = "Modifiche non salvate" if self.is_modified else "Salvato"
        filename = os.path.basename(self.current_filepath) if self.current_filepath else "Nuovo documento"
        self.status_label.configure(text=f"{filename}  |  Riga {line}, colonna {int(column) + 1}  |  {state}")


if __name__ == "__main__":
    root = tk.Tk()
    app = MarkdownViewerApp(root)
    root.mainloop()
