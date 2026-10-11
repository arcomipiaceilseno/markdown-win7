
import os
import tkinter as tk
from tkinter import messagebox, ttk

from tkinterweb import HtmlFrame

from .file_manager import FileManager
from .markdown_renderer import markdown_to_html
from .toolbar import Toolbar
from .search import open_search_dialog
from .i18n import translate


class MarkdownViewerApp:
    """Editor Markdown con anteprima HTML in tempo reale."""

    PREVIEW_CSS = r"""
        body {
            font-family: -apple-system, BlinkMacSystemFont,
                "Segoe UI", Helvetica, Arial, sans-serif;
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

        h1:first-child, h2:first-child, h3:first-child {
            margin-top: .2em;
        }

        a {
            color: #0969da;
        }

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

        pre code {
            background: transparent;
            padding: 0;
        }

        blockquote {
            color: #57606a;
            border-left: 4px solid #d0d7de;
            padding: 2px 0 2px 14px;
            margin-left: 0;
        }

        table {
            border-collapse: collapse;
            width: 100%;
            margin: 16px 0;
        }

        th, td {
            border: 1px solid #d0d7de;
            padding: 6px 12px;
        }

        tr:nth-child(even) {
            background: #f6f8fa;
        }

        img {
            max-width: 100%;
            height: auto;
        }

        img.emoji {
            display: inline;
            width: 1.2em;
            height: 1.2em;
            max-width: 1.2em;
            vertical-align: -0.2em;
            border: 0;
        }

        hr {
            border: 0;
            border-top: 1px solid #d8dee4;
            margin: 24px 0;
        }

        li {
            margin: 3px 0;
        }
    """

    def __init__(self, root):
        self.root = root
        self.root.geometry("1250x780")
        self.root.minsize(900, 600)

        self.language = "it"
        self.language_var = tk.StringVar(root, value="it")
        self.current_filepath = None
        self.is_modified = False
        self._loading = False
        self._preview_ready = False
        self._debounce_timer = None

        # Scroll sincronizzato.
        self.sync_scroll_enabled = tk.BooleanVar(value=False)
        self._syncing_scroll = False
        self._sync_scroll_bindings = {}

        self.file_manager = FileManager(self)
        self.toolbar = None

        self.create_layout()

        self.create_menu()
        self.bind_shortcuts()

        self.root.protocol("WM_DELETE_WINDOW", self.exit_app)

        self.update_window_title()
        self.update_status()
        self.update_preview()

    # ==========================================================
    # MENU
    # ==========================================================

    def t(self, key, *args):
        return translate(self.language, key, *args)

    def change_language(self, language):
        if language not in ("it", "en") or language == self.language:
            return
        self.language = language
        self.create_menu()
        self.toolbar.create(self.toolbar_frame)
        self.source_label.configure(text=self.t("source"))
        self.preview_label.configure(text=self.t("preview"))
        self.update_window_title()
        self.update_status()

    def create_menu(self):
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label=self.t("new"), command=self.file_manager.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label=self.t("open"), command=self.file_manager.open_file, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label=self.t("save"), command=self.file_manager.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label=self.t("save_as"), command=self.file_manager.save_file_as, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label=self.t("exit"), command=self.exit_app)
        menubar.add_cascade(label=self.t("file"), menu=file_menu)

        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label=self.t("search"), command=self.open_search, accelerator="Ctrl+F")
        edit_menu.add_separator()
        edit_menu.add_command(label=self.t("bold"), command=self.toolbar.make_bold, accelerator="Ctrl+B")
        edit_menu.add_command(label=self.t("italic"), command=self.toolbar.make_italic, accelerator="Ctrl+I")
        edit_menu.add_command(label=self.t("link"), command=self.toolbar.insert_link, accelerator="Ctrl+K")
        edit_menu.add_separator()
        edit_menu.add_command(label=self.t("undo"), command=lambda: self.text_editor.event_generate("<<Undo>>"), accelerator="Ctrl+Z")
        edit_menu.add_command(label=self.t("redo"), command=lambda: self.text_editor.event_generate("<<Redo>>"), accelerator="Ctrl+Y")
        menubar.add_cascade(label=self.t("edit"), menu=edit_menu)

        functions_menu = tk.Menu(menubar, tearoff=0)
        functions_menu.add_checkbutton(label=self.t("sync_scroll"), variable=self.sync_scroll_enabled, command=self.toggle_sync_scroll)
        menubar.add_cascade(label=self.t("functions"), menu=functions_menu)

        language_menu = tk.Menu(menubar, tearoff=0)
        language_menu.add_radiobutton(label=self.t("italian"), value="it", variable=self.language_var, command=lambda: self.change_language(self.language_var.get()))
        language_menu.add_radiobutton(label=self.t("english"), value="en", variable=self.language_var, command=lambda: self.change_language(self.language_var.get()))
        menubar.add_cascade(label=self.t("language"), menu=language_menu)
        self.root.config(menu=menubar)

    # ==========================================================
    # LAYOUT
    # ==========================================================

    def create_layout(self):
        self.toolbar_frame = ttk.Frame(self.root)
        self.toolbar_frame.pack(fill=tk.X, side=tk.TOP)
        self.toolbar = Toolbar(None, self.update_status, self)
        # The editor is assigned as soon as the left pane is created below.

        self.paned_window = ttk.PanedWindow(
            self.root,
            orient=tk.HORIZONTAL,
        )
        self.paned_window.pack(
            fill=tk.BOTH,
            expand=True,
            padx=6,
            pady=(6, 2),
        )

        self.left_frame = ttk.Frame(
            self.paned_window,
            padding=4,
        )
        self.paned_window.add(
            self.left_frame,
            weight=1,
        )

        self.source_label = ttk.Label(
            self.left_frame,
            text=self.t("source"),
            font=("Arial", 11, "bold"),
        )
        self.source_label.pack(
            anchor="w",
            padx=4,
            pady=(2, 5),
        )

        editor_frame = ttk.Frame(self.left_frame)
        editor_frame.pack(
            fill=tk.BOTH,
            expand=True,
        )

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
        self.toolbar.editor = self.text_editor
        self.toolbar.create(self.toolbar_frame)

        # Scrollbar verticale collegata al metodo personalizzato.
        # In questo modo rileviamo anche i movimenti della barra.
        editor_scroll_y = ttk.Scrollbar(
            editor_frame,
            orient=tk.VERTICAL,
            command=self._editor_scrollbar_command,
        )

        editor_scroll_x = ttk.Scrollbar(
            editor_frame,
            orient=tk.HORIZONTAL,
            command=self.text_editor.xview,
        )

        self.text_editor.configure(
            yscrollcommand=editor_scroll_y.set,
            xscrollcommand=editor_scroll_x.set,
        )

        self.text_editor.grid(
            row=0,
            column=0,
            sticky="nsew",
        )
        editor_scroll_y.grid(
            row=0,
            column=1,
            sticky="ns",
        )
        editor_scroll_x.grid(
            row=1,
            column=0,
            sticky="ew",
        )

        editor_frame.rowconfigure(0, weight=1)
        editor_frame.columnconfigure(0, weight=1)

        self.text_editor.bind(
            "<<Modified>>",
            self.on_text_modified,
        )
        self.text_editor.bind(
            "<KeyRelease>",
            self.on_cursor_activity,
            add="+",
        )
        self.text_editor.bind(
            "<ButtonRelease-1>",
            self.on_cursor_activity,
            add="+",
        )

        right_frame = ttk.Frame(
            self.paned_window,
            padding=4,
        )
        self.paned_window.add(
            right_frame,
            weight=1,
        )

        self.preview_label = ttk.Label(
            right_frame,
            text=self.t("preview"),
            font=("Arial", 11, "bold"),
        )
        self.preview_label.pack(
            anchor="w",
            padx=4,
            pady=(2, 5),
        )

        self.html_view = HtmlFrame(
            right_frame,
            messages_enabled=False,
            images_enabled=True,
            caches_enabled=True,
        )
        self.html_view.pack(
            fill=tk.BOTH,
            expand=True,
        )

        self.status_label = ttk.Label(
            self.root,
            text="",
            anchor="w",
            relief=tk.SUNKEN,
            padding=(7, 3),
        )
        self.status_label.pack(
            fill=tk.X,
            side=tk.BOTTOM,
            padx=6,
            pady=(2, 6),
        )

    # ==========================================================
    # RICERCA
    # ==========================================================

    def open_search(self, event=None):
        """Apre il dialogo di ricerca nell'editor Markdown."""

        open_search_dialog(self.root, self.text_editor, self)
        return "break"

    # ==========================================================
    # SCROLL SINCRONIZZATO
    # ==========================================================

    def toggle_sync_scroll(self):
        """Attiva o disattiva lo scroll sincronizzato."""

        sequences = (
            "<MouseWheel>",
            "<Button-4>",
            "<Button-5>",
        )

        if self.sync_scroll_enabled.get():
            # Evita di registrare più volte gli stessi binding.
            for sequence in sequences:
                if sequence not in self._sync_scroll_bindings:
                    funcid = self.text_editor.bind(
                        sequence,
                        self._on_editor_scroll,
                        add="+",
                    )
                    self._sync_scroll_bindings[sequence] = funcid

            # Allinea subito l'anteprima alla posizione corrente.
            self.root.after_idle(
                self._sync_preview_to_editor
            )

        else:
            # Rimuove solo i binding aggiunti per questa funzione.
            for sequence, funcid in list(
                self._sync_scroll_bindings.items()
            ):
                try:
                    if funcid:
                        self.text_editor.unbind(sequence, funcid)
                except tk.TclError:
                    pass

            self._sync_scroll_bindings.clear()
            self._syncing_scroll = False

    def _editor_scrollbar_command(self, *args):
        """
        Gestisce lo scroll della barra laterale.

        Intercetta sia il trascinamento della maniglia sia i click
        sulla barra, mantenendo invariato lo scroll dell'editor.
        """

        self.text_editor.yview(*args)

        if self.sync_scroll_enabled.get():
            self.root.after_idle(
                self._sync_preview_to_editor
            )

    def _on_editor_scroll(self, event):
        """Sincronizza l'anteprima quando si usa la rotellina."""

        if (
            not self.sync_scroll_enabled.get()
            or self._syncing_scroll
        ):
            return None

        self._syncing_scroll = True

        try:
            self.root.after_idle(
                self._sync_preview_to_editor
            )
        finally:
            self.root.after(
                20,
                self._reset_scroll_sync,
            )

        # Tkinter continua a gestire normalmente lo scroll.
        return None

    def _sync_preview_to_editor(self):
        """Allinea l'anteprima alla posizione relativa dell'editor."""

        if not self.sync_scroll_enabled.get():
            return

        try:
            first, _ = self.text_editor.yview()
            self._scroll_preview_to_fraction(first)
        except (tk.TclError, AttributeError):
            pass

    def _scroll_preview_to_fraction(self, fraction):
        """Scorre l'anteprima usando una posizione relativa 0..1."""

        try:
            html_widget = self.html_view.html

            if hasattr(html_widget, "yview_moveto"):
                html_widget.yview_moveto(fraction)
            elif hasattr(html_widget, "yview"):
                html_widget.yview("moveto", fraction)

        except (tk.TclError, AttributeError):
            pass

    def _reset_scroll_sync(self):
        """Permette una nuova sincronizzazione."""

        self._syncing_scroll = False

    # ==========================================================
    # SCORCIATOIE
    # ==========================================================

    def bind_shortcuts(self):
        shortcuts = {
            "<Control-n>": self.file_manager.new_file,
            "<Control-o>": self.file_manager.open_file,
            "<Control-s>": self.file_manager.save_file,
            "<Control-Shift-S>": self.file_manager.save_file_as,
            "<Control-b>": self.toolbar.make_bold,
            "<Control-i>": self.toolbar.make_italic,
            "<Control-k>": self.toolbar.insert_link,
            "<Control-Shift-c>": self.toolbar.make_code_block,
            "<Control-f>": self.open_search,
        }

        for sequence, command in shortcuts.items():
            callback = (
                lambda _event, cmd=command:
                self.run_shortcut(cmd)
            )
            self.text_editor.bind(sequence, callback)
            self.root.bind_all(sequence, callback)

    @staticmethod
    def run_shortcut(command):
        command()
        return "break"

    # ==========================================================
    # MODIFICHE E CHIUSURA
    # ==========================================================

    def confirm_discard_changes(self):
        if not self.is_modified:
            return True

        answer = messagebox.askyesnocancel(
            self.t("discard_title"),
            self.t("discard_prompt"),
            parent=self.root,
        )

        if answer is None:
            return False

        if answer is True:
            return self.file_manager.save_file()

        return True

    def exit_app(self):
        if not self.confirm_discard_changes():
            return

        self._cancel_preview_timer()
        self.root.destroy()

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

    # ==========================================================
    # ANTEPRIMA MARKDOWN
    # ==========================================================

    def schedule_preview_update(self):
        self._cancel_preview_timer()
        self._debounce_timer = self.root.after(
            250,
            self.update_preview,
        )

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

    def _full_preview_html(self, html_body):
        return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>{self.PREVIEW_CSS}</style>
</head>
<body><main id="markdown-content">{html_body}</main></body>
</html>"""

    def update_preview(self):
        self._debounce_timer = None

        markdown_text = self.text_editor.get(
            "1.0",
            "end-1c",
        )
        html_body = markdown_to_html(markdown_text)
        scroll_pos = self._get_preview_scroll()

        if not self._preview_ready:
            self.html_view.load_html(
                self._full_preview_html(html_body)
            )
            self._preview_ready = True

            if self.sync_scroll_enabled.get():
                self.root.after(
                    100,
                    self._sync_preview_to_editor,
                )
            return

        try:
            content_node = (
                self.html_view.document.getElementById(
                    "markdown-content"
                )
            )
            content_node.innerHTML = html_body

            if scroll_pos is not None:
                self.root.after_idle(
                    lambda pos=scroll_pos:
                    self._restore_preview_scroll(pos)
                )

            if self.sync_scroll_enabled.get():
                self.root.after_idle(
                    self._sync_preview_to_editor
                )

        except Exception:
            self.html_view.load_html(
                self._full_preview_html(html_body)
            )

            if scroll_pos is not None:
                self.root.after(
                    60,
                    lambda pos=scroll_pos:
                    self._restore_preview_scroll(pos),
                )

            if self.sync_scroll_enabled.get():
                self.root.after(
                    100,
                    self._sync_preview_to_editor,
                )

    def _get_preview_scroll(self):
        try:
            return self.html_view.html.yview()
        except Exception:
            return None

    def _restore_preview_scroll(self, position):
        try:
            if position:
                self.html_view.html.yview_moveto(
                    position[0]
                )
        except Exception:
            pass

    # ==========================================================
    # TITOLO E STATO
    # ==========================================================

    def update_window_title(self):
        filename = (
            self.current_filepath
            if self.current_filepath
            else self.t("new_document")
        )
        modified_mark = " *" if self.is_modified else ""

        self.root.title(
            f"Markdown Editor — {filename}{modified_mark}"
        )

    def update_status(self):
        try:
            line, column = self.text_editor.index(
                tk.INSERT
            ).split(".")
        except Exception:
            line, column = "1", "0"

        state = self.t("unsaved") if self.is_modified else self.t("saved")
        filename = (
            os.path.basename(self.current_filepath)
            if self.current_filepath
            else self.t("new_document")
        )

        if hasattr(self, "status_label"):
            self.status_label.configure(
                text=(
                    f"{filename}  |  {self.t('row')} {line}, "
                    f"{self.t('column')} {int(column) + 1}  |  {state}"
                )
            )
