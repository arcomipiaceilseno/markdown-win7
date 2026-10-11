
import os
import tkinter as tk
from tkinter import filedialog, messagebox


class FileManager:
    """Gestisce i file Markdown dell'applicazione."""

    def __init__(self, app):
        self.app = app

    def new_file(self):
        if not self.app.confirm_discard_changes():
            return

        app = self.app
        app.current_filepath = None
        app._loading = True

        app.text_editor.delete("1.0", tk.END)
        app.text_editor.edit_modified(False)

        app._loading = False
        app.is_modified = False

        app.update_window_title()
        app.update_preview_now()
        app.update_status()

    def open_file(self):
        filepath = filedialog.askopenfilename(
            title=self.app.t("open_title"),
            filetypes=[
                (self.app.t("markdown_files"), "*.md *.markdown *.mdown *.mkd"),
                (self.app.t("all_files"), "*.*"),
            ],
        )
        if filepath:
            self.open_path(filepath)

    def open_path(self, filepath, ask_before_discard=True):
        """Carica un percorso ricevuto dal sistema operativo o dal menu File."""
        if not filepath or not os.path.isfile(filepath):
            messagebox.showerror(
                self.app.t("open_error"),
                self.app.t("read_error") + "\n\n" + str(filepath),
                parent=self.app.root,
            )
            return False

        app = self.app
        if ask_before_discard and not app.confirm_discard_changes():
            return False

        try:
            with open(filepath, "r", encoding="utf-8-sig") as file:
                content = file.read()
            app._loading = True
            try:
                app.text_editor.delete("1.0", tk.END)
                app.text_editor.insert("1.0", content)
                app.text_editor.edit_modified(False)
            finally:
                app._loading = False

            app.current_filepath = os.path.abspath(filepath)
            app.is_modified = False
            app._cancel_preview_timer()
            app.update_window_title()
            app.update_preview_now()
            app.update_status()
            return True
        except (OSError, UnicodeError) as exc:
            app._loading = False
            messagebox.showerror(
                app.t("open_error"),
                f"{app.t('read_error')}\n\n{exc}",
                parent=app.root,
            )
            return False

    def save_file(self):
        return self._save_to_path(self.app.current_filepath)

    def save_file_as(self):
        return self._save_to_path(None)

    def _save_to_path(self, filepath):
        app = self.app

        if not filepath:
            filepath = filedialog.asksaveasfilename(
                title=app.t("save_title"),
                defaultextension=".md",
                filetypes=[
                    (app.t("markdown_files"), "*.md"),
                    (self.app.t("all_files"), "*.*"),
                ],
                initialfile=(
                    os.path.basename(app.current_filepath)
                    if app.current_filepath
                    else ("document.md" if app.language == "en" else "documento.md")
                ),
            )

            if not filepath:
                return False

        content = app.text_editor.get("1.0", "end-1c")

        try:
            with open(
                filepath, "w", encoding="utf-8", newline=""
            ) as file:
                file.write(content)

        except OSError as exc:
            messagebox.showerror(
                app.t("save_error"),
                f"{app.t('write_error')}\n\n{exc}",
                parent=app.root,
            )
            return False

        app.current_filepath = filepath
        app.is_modified = False
        app.text_editor.edit_modified(False)

        app.update_window_title()
        app.update_status()

        messagebox.showinfo(
            app.t("saved_title"),
            app.t("saved_message"),
            parent=app.root,
        )

        return True
