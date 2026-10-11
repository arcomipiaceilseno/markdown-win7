import re
import tkinter as tk
from tkinter import ttk


class _Tooltip:
    """Piccolo tooltip nativo, senza dipendenze aggiuntive."""

    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.window = None
        widget.bind("<Enter>", self.show, add="+")
        widget.bind("<Leave>", self.hide, add="+")
        widget.bind("<ButtonPress>", self.hide, add="+")

    def show(self, _event=None):
        if self.window or not self.text:
            return
        try:
            x = self.widget.winfo_rootx() + self.widget.winfo_width() // 2
            y = self.widget.winfo_rooty() + self.widget.winfo_height() + 4
            self.window = tk.Toplevel(self.widget)
            self.window.wm_overrideredirect(True)
            self.window.wm_geometry(f"+{x}+{y}")
            label = tk.Label(
                self.window,
                text=self.text,
                background="#fff8d8",
                foreground="#202020",
                relief=tk.SOLID,
                borderwidth=1,
                padx=5,
                pady=2,
                font=("Segoe UI", 9),
            )
            label.pack()
        except tk.TclError:
            self.window = None

    def hide(self, _event=None):
        if self.window:
            try:
                self.window.destroy()
            except tk.TclError:
                pass
            self.window = None


class Toolbar:
    """Barra Markdown compatta con pulsanti quadrati e icone tipografiche."""

    def __init__(self, editor, on_status_update, app=None):
        self.editor = editor
        self.on_status_update = on_status_update
        self.app = app

    def t(self, key):
        return self.app.t(key) if self.app else key

    def create(self, parent):
        if hasattr(self, "toolbar") and self.toolbar.winfo_exists():
            self.toolbar.destroy()

        # Usiamo i pulsanti ttk standard: su Windows adottano il tema nativo
        # disponibile (ad esempio Vista/xpnative), invece di un aspetto custom.
        toolbar = ttk.Frame(parent)
        self.toolbar = toolbar
        toolbar.pack(fill=tk.X, padx=6, pady=(4, 4))

        groups = [
            [
                ("B", self.make_bold, self.t("bold"), "bold"),
                ("I", self.make_italic, self.t("italic"), "italic"),
                ("S̶", self.make_strikethrough, "Testo barrato" if self._is_italian() else "Strikethrough", "normal"),
            ],
            [
                ("H1", lambda: self.apply_line_prefix("# "), "Titolo 1" if self._is_italian() else "Heading 1", "bold"),
                ("H2", lambda: self.apply_line_prefix("## "), "Titolo 2" if self._is_italian() else "Heading 2", "bold"),
                ("❝", lambda: self.apply_line_prefix("> "), self.t("quote"), "normal"),
            ],
            [
                ("<>" , self.make_inline_code, "Codice inline" if self._is_italian() else "Inline code", "normal"),
                ("{ }", self.make_code_block, self.t("block_code"), "normal"),
            ],
            [
                ("•", lambda: self.apply_line_prefix("- "), self.t("list"), "bold"),
                ("1.", lambda: self.apply_line_prefix("1. "), self.t("numbered_list"), "bold"),
            ],
            [
                ("↗", self.insert_link, self.t("link"), "normal"),
                ("▧", self.insert_image, self.t("image"), "normal"),
                ("―", self.insert_horizontal_rule, self.t("separator"), "normal"),
            ],
        ]

        # Larghezza fissa in caratteri e font comune: tutti i pulsanti hanno
        # dimensioni uniformi, senza allungarsi quando la finestra è grande.
        for group_index, group in enumerate(groups):
            group_frame = ttk.Frame(toolbar)
            group_frame.pack(side=tk.LEFT, anchor="w")

            for icon_text, command, tooltip_text, font_weight in group:
                style_name = {
                    "bold": "MarkdownToolbar.Bold.TButton",
                    "italic": "MarkdownToolbar.Italic.TButton",
                }.get(font_weight, "MarkdownToolbar.TButton")
                button = ttk.Button(
                    group_frame,
                    text=icon_text,
                    command=command,
                    width=4,
                    takefocus=True,
                    style=style_name,
                )
                button.pack(side=tk.LEFT, padx=2, pady=1, ipadx=0, ipady=1)
                _Tooltip(button, tooltip_text)

            if group_index < len(groups) - 1:
                ttk.Separator(toolbar, orient=tk.VERTICAL).pack(
                    side=tk.LEFT, fill=tk.Y, padx=5, pady=4
                )

        # Un unico stile e una sola misura del font per evitare pulsanti con
        # altezze differenti. I caratteri B/I restano riconoscibili dal simbolo.
        style = ttk.Style(toolbar)
        style.configure("MarkdownToolbar.TButton", font=("Segoe UI", 9), padding=(4, 3))
        style.configure("MarkdownToolbar.Bold.TButton", font=("Segoe UI", 9, "bold"), padding=(4, 3))
        style.configure("MarkdownToolbar.Italic.TButton", font=("Segoe UI", 9, "italic"), padding=(4, 3))

    def _is_italian(self):
        return not self.app or getattr(self.app, "language", "it") == "it"

    def wrap_selection(self, prefix, suffix=None, placeholder="testo"):
        if suffix is None:
            suffix = prefix

        try:
            start = self.editor.index("sel.first")
            end = self.editor.index("sel.last")
            selected = self.editor.get(start, end)

            self.editor.delete(start, end)
            self.editor.insert(start, prefix + selected + suffix)

            inner_start = f"{start}+{len(prefix)}c"
            inner_end = f"{inner_start}+{len(selected)}c"

        except tk.TclError:
            start = self.editor.index(tk.INSERT)
            self.editor.insert(start, prefix + placeholder + suffix)

            inner_start = f"{start}+{len(prefix)}c"
            inner_end = f"{inner_start}+{len(placeholder)}c"

        self.editor.tag_remove("sel", "1.0", tk.END)
        self.editor.tag_add("sel", inner_start, inner_end)
        self.editor.mark_set(tk.INSERT, inner_end)
        self.editor.focus_set()
        self.on_status_update()

    def make_bold(self):
        self.wrap_selection("**", "**", self.t("bold_placeholder"))

    def make_italic(self):
        self.wrap_selection("*", "*", self.t("italic_placeholder"))

    def make_strikethrough(self):
        self.wrap_selection("~~", "~~", self.t("strike_placeholder"))

    def make_inline_code(self):
        self.wrap_selection("`", "`", self.t("code_placeholder"))

    def apply_line_prefix(self, prefix):
        try:
            start = self.editor.index("sel.first linestart")
            selection_end = self.editor.index("sel.last")

            if selection_end.endswith(".0") and selection_end != start:
                previous_char = self.editor.index(f"{selection_end}-1c")
                end = self.editor.index(f"{previous_char} lineend")
            else:
                end = self.editor.index("sel.last lineend")

        except tk.TclError:
            start = self.editor.index("insert linestart")
            end = self.editor.index("insert lineend")

        original = self.editor.get(start, end)
        lines = original.splitlines() or [""]
        transformed = []

        for line in lines:
            if prefix.startswith("#"):
                line = re.sub(r"^\s{0,3}#{1,6}\s+", "", line)
                transformed.append(prefix + line)
            elif prefix == "> ":
                transformed.append(line[2:] if line.startswith("> ") else prefix + line)
            elif prefix in ("- ", "1. "):
                line = re.sub(r"^\s*(?:[-*+]\s+|\d+\.\s+)", "", line)
                transformed.append(prefix + line)
            else:
                transformed.append(prefix + line)

        replacement = "\n".join(transformed)
        self.editor.delete(start, end)
        self.editor.insert(start, replacement)
        self.editor.tag_remove("sel", "1.0", tk.END)
        self.editor.tag_add("sel", start, f"{start}+{len(replacement)}c")
        self.editor.mark_set(tk.INSERT, f"{start}+{len(replacement)}c")
        self.editor.focus_set()
        self.on_status_update()

    def make_code_block(self):
        try:
            start = self.editor.index("sel.first")
            end = self.editor.index("sel.last")
            selected = self.editor.get(start, end)
        except tk.TclError:
            start = self.editor.index(tk.INSERT)
            selected = self.t("code_placeholder")

        replacement = "```\n" + selected + "\n```"
        if self.editor.tag_ranges("sel"):
            self.editor.delete("sel.first", "sel.last")
        self.editor.insert(start, replacement)

        code_start = f"{start}+4c"
        code_end = f"{code_start}+{len(selected)}c"
        self.editor.tag_remove("sel", "1.0", tk.END)
        self.editor.tag_add("sel", code_start, code_end)
        self.editor.mark_set(tk.INSERT, code_end)
        self.editor.focus_set()
        self.on_status_update()

    def insert_link(self):
        try:
            start = self.editor.index("sel.first")
            end = self.editor.index("sel.last")
            selected = self.editor.get(start, end)
            replacement = f"[{selected}](https://)"
            self.editor.delete(start, end)
            self.editor.insert(start, replacement)
            url_start = f"{start}+{len(selected) + 3}c"
            url_length = 8
        except tk.TclError:
            start = self.editor.index(tk.INSERT)
            label = self.t("link_text")
            url = self.t("example_url")
            self.editor.insert(start, f"[{label}]({url})")
            url_start = f"{start}+{len(label) + 3}c"
            url_length = len(url)

        self.editor.tag_remove("sel", "1.0", tk.END)
        self.editor.tag_add("sel", url_start, f"{url_start}+{url_length}c")
        self.editor.mark_set(tk.INSERT, f"{url_start}+{url_length}c")
        self.editor.focus_set()
        self.on_status_update()

    def insert_image(self):
        self.wrap_selection("![", "](https://esempio.com/immagine.png)", self.t("image_desc"))

    def insert_horizontal_rule(self):
        insert_at = self.editor.index(tk.INSERT)
        line_start = self.editor.index("insert linestart")
        line_end = self.editor.index("insert lineend")
        line_content = self.editor.get(line_start, line_end)
        prefix = "" if not line_content.strip() else "\n"
        suffix = "" if insert_at == "1.0" else "\n"
        self.editor.insert(insert_at, prefix + "---" + suffix)
        self.editor.focus_set()
        self.on_status_update()
