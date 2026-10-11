
import re
import tkinter as tk
from tkinter import ttk


class Toolbar:
    """Barra degli strumenti per formattare il Markdown."""

    def __init__(self, editor, on_status_update, app=None):
        self.editor = editor
        self.on_status_update = on_status_update
        self.app = app

    def t(self, key):
        return self.app.t(key) if self.app else key

    def create(self, parent):
        if hasattr(self, "toolbar") and self.toolbar.winfo_exists():
            self.toolbar.destroy()
        toolbar = ttk.Frame(parent)
        self.toolbar = toolbar
        toolbar.pack(fill=tk.X, padx=6, pady=(5, 4))

        commands = [
            ("** B **", self.make_bold),
            ("* I *", self.make_italic),
            ("~~ S ~~", self.make_strikethrough),
            ("H1", lambda: self.apply_line_prefix("# ")),
            ("H2", lambda: self.apply_line_prefix("## ")),
            (self.t("quote"), lambda: self.apply_line_prefix("> ")),
            ("` Code `" if self.app and self.app.language == "en" else "` Codice `", self.make_inline_code),
            (self.t("block_code"), self.make_code_block),
            (self.t("list"), lambda: self.apply_line_prefix("- ")),
            (self.t("numbered_list"), lambda: self.apply_line_prefix("1. ")),
            (self.t("link"), self.insert_link),
            (self.t("image"), self.insert_image),
            (self.t("separator"), self.insert_horizontal_rule),
        ]

        columns = 7

        for column in range(columns):
            toolbar.columnconfigure(column, weight=1)

        for index, (label, command) in enumerate(commands):
            ttk.Button(
                toolbar,
                text=label,
                command=command,
            ).grid(
                row=index // columns,
                column=index % columns,
                sticky="ew",
                padx=2,
                pady=2,
            )

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
                previous_char = self.editor.index(
                    f"{selection_end}-1c"
                )
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
                transformed.append(
                    line[2:] if line.startswith("> ")
                    else prefix + line
                )

            elif prefix in ("- ", "1. "):
                line = re.sub(
                    r"^\s*(?:[-*+]\s+|\d+\.\s+)",
                    "",
                    line,
                )
                transformed.append(prefix + line)

            else:
                transformed.append(prefix + line)

        replacement = "\n".join(transformed)

        self.editor.delete(start, end)
        self.editor.insert(start, replacement)
        self.editor.tag_remove("sel", "1.0", tk.END)
        self.editor.tag_add(
            "sel", start, f"{start}+{len(replacement)}c"
        )
        self.editor.mark_set(
            tk.INSERT, f"{start}+{len(replacement)}c"
        )
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
        self.editor.tag_add(
            "sel", url_start, f"{url_start}+{url_length}c"
        )
        self.editor.mark_set(
            tk.INSERT, f"{url_start}+{url_length}c"
        )
        self.editor.focus_set()
        self.on_status_update()

    def insert_image(self):
        self.wrap_selection(
            "![",
            "](https://esempio.com/immagine.png)",
            self.t("image_desc"),
        )

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
