
"""Dialogo di ricerca per Markdown Win7."""

import tkinter as tk
from tkinter import ttk


class SearchDialog:
    """Finestra di ricerca collegata a un widget tkinter.Text."""

    ALL_TAG = "markdown_win7_search_all"
    CURRENT_TAG = "markdown_win7_search_current"

    def __init__(self, parent, text_widget, app=None):
        self.parent = parent
        self.text_widget = text_widget
        self.app = app

        self.matches = []
        self.current_match = None
        self._trace_id = None

        self.dialog = tk.Toplevel(parent)
        self.dialog.title(self.t("search_title"))
        self.dialog.transient(parent)
        self.dialog.resizable(False, False)

        self.query_var = tk.StringVar(master=self.dialog)
        self.case_var = tk.BooleanVar(master=self.dialog, value=False)
        self.status_var = tk.StringVar(
            master=self.dialog,
            value=self.t("search_prompt"),
        )

        self._build_ui()
        self._bind_events()
        self._center_dialog()

        self.dialog.protocol("WM_DELETE_WINDOW", self.close)

        # Se nell'editor c'è una selezione, la usa come ricerca iniziale.
        try:
            selected_text = self.text_widget.get("sel.first", "sel.last")
            if selected_text:
                self.query_var.set(selected_text)
                self.entry.select_range(0, tk.END)
        except tk.TclError:
            pass

        self.entry.focus_set()
        self.refresh_matches()

        # Mantiene il dialogo davanti alla finestra principale.
        self.dialog.lift()

    def t(self, key, *args):
        return self.app.t(key, *args) if self.app else key

    def _build_ui(self):
        """Crea i controlli del dialogo."""

        frame = ttk.Frame(self.dialog, padding=12)
        frame.grid(row=0, column=0, sticky="nsew")

        ttk.Label(
            frame,
            text=self.t("search_label"),
        ).grid(
            row=0,
            column=0,
            columnspan=3,
            sticky="w",
            pady=(0, 5),
        )

        self.entry = ttk.Entry(
            frame,
            textvariable=self.query_var,
            width=36,
        )
        self.entry.grid(
            row=1,
            column=0,
            columnspan=3,
            sticky="ew",
            pady=(0, 8),
        )

        self.case_check = ttk.Checkbutton(
            frame,
            text=self.t("case_sensitive"),
            variable=self.case_var,
            command=self.refresh_matches,
        )
        self.case_check.grid(
            row=2,
            column=0,
            columnspan=3,
            sticky="w",
            pady=(0, 10),
        )

        self.previous_button = ttk.Button(
            frame,
            text=self.t("previous"),
            command=self.find_previous,
        )
        self.previous_button.grid(
            row=3,
            column=0,
            sticky="ew",
            padx=(0, 4),
        )

        self.next_button = ttk.Button(
            frame,
            text=self.t("next"),
            command=self.find_next,
        )
        self.next_button.grid(
            row=3,
            column=1,
            sticky="ew",
            padx=4,
        )

        self.close_button = ttk.Button(
            frame,
            text=self.t("close"),
            command=self.close,
        )
        self.close_button.grid(
            row=3,
            column=2,
            sticky="ew",
            padx=(4, 0),
        )

        self.status_label = ttk.Label(
            frame,
            textvariable=self.status_var,
            anchor="w",
        )
        self.status_label.grid(
            row=4,
            column=0,
            columnspan=3,
            sticky="ew",
            pady=(10, 0),
        )

        for column in range(3):
            frame.columnconfigure(column, weight=1)

    def _bind_events(self):
        """Registra gli eventi da tastiera."""

        self.entry.bind("<Return>", self._find_next_event)
        self.entry.bind("<Shift-Return>", self._find_previous_event)
        self.dialog.bind("<Escape>", self._close_event)

        self._trace_id = self.query_var.trace_add(
            "write",
            self._query_changed,
        )

    def _center_dialog(self):
        """Centra il dialogo sulla finestra principale."""

        self.dialog.update_idletasks()

        width = self.dialog.winfo_reqwidth()
        height = self.dialog.winfo_reqheight()

        self.parent.update_idletasks()

        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()

        x = parent_x + max(0, (parent_width - width) // 2)
        y = parent_y + max(0, (parent_height - height) // 2)

        self.dialog.geometry(
            "{}x{}+{}+{}".format(width, height, x, y)
        )

    def _query_changed(self, *_args):
        """Aggiorna i risultati mentre l'utente digita."""

        if self.dialog.winfo_exists():
            self.refresh_matches()

    def refresh_matches(self):
        """Trova ed evidenzia tutte le occorrenze."""

        self.matches = []
        self.current_match = None

        self.text_widget.tag_remove(
            self.ALL_TAG, "1.0", "end"
        )
        self.text_widget.tag_remove(
            self.CURRENT_TAG, "1.0", "end"
        )

        query = self.query_var.get()

        if not query:
            self.status_var.set(self.t("search_prompt"))
            return

        start = "1.0"
        stop = "end-1c"
        nocase = not self.case_var.get()

        while True:
            found = self.text_widget.search(
                query,
                start,
                stopindex=stop,
                nocase=nocase,
            )

            if not found:
                break

            end = "{}+{}c".format(found, len(query))
            self.matches.append((found, end))
            self.text_widget.tag_add(self.ALL_TAG, found, end)

            # Avanza fino alla fine dell'occorrenza trovata.
            start = end

        self.text_widget.tag_configure(
            self.ALL_TAG,
            background="#FFF2A8",
            foreground="#000000",
        )
        self.text_widget.tag_configure(
            self.CURRENT_TAG,
            background="#FFB347",
            foreground="#000000",
            underline=True,
        )

        self.text_widget.tag_raise(self.ALL_TAG)
        self.text_widget.tag_raise(self.CURRENT_TAG)

        count = len(self.matches)

        if count == 0:
            self.status_var.set(self.t("no_matches"))
        else:
            self.status_var.set(self.t("matches", count))

    def _select_match(self, position):
        """Evidenzia e porta a schermo un risultato."""

        if not self.matches:
            self.current_match = None
            self.status_var.set(self.t("no_matches"))
            return

        # Ricerca circolare: gli indici vengono riportati nell'intervallo.
        position %= len(self.matches)

        start, end = self.matches[position]
        self.current_match = position

        self.text_widget.tag_remove(
            self.CURRENT_TAG, "1.0", "end"
        )
        self.text_widget.tag_add(
            self.CURRENT_TAG, start, end
        )

        self.text_widget.mark_set("insert", end)
        self.text_widget.see(start)

        self.status_var.set(self.t("result", position + 1, len(self.matches)))

    def find_next(self):
        """Seleziona il risultato successivo, tornando all'inizio se serve."""

        if not self.matches:
            self.refresh_matches()

        if not self.matches:
            return

        if self.current_match is not None:
            position = self.current_match + 1
        else:
            cursor = self.text_widget.index("insert")

            position = next(
                (
                    i
                    for i, (start, _end) in enumerate(self.matches)
                    if self.text_widget.compare(start, ">=", cursor)
                ),
                0,
            )

        self._select_match(position)

    def find_previous(self):
        """Seleziona il risultato precedente, tornando alla fine se serve."""

        if not self.matches:
            self.refresh_matches()

        if not self.matches:
            return

        if self.current_match is not None:
            position = self.current_match - 1
        else:
            cursor = self.text_widget.index("insert")

            position = next(
                (
                    i
                    for i in range(len(self.matches) - 1, -1, -1)
                    if self.text_widget.compare(
                        self.matches[i][0], "<", cursor
                    )
                ),
                len(self.matches) - 1,
            )

        self._select_match(position)

    def _find_next_event(self, _event=None):
        self.find_next()
        return "break"

    def _find_previous_event(self, _event=None):
        self.find_previous()
        return "break"

    def _close_event(self, _event=None):
        self.close()
        return "break"

    def close(self):
        """Rimuove le evidenziazioni e chiude il dialogo."""

        try:
            self.text_widget.tag_remove(
                self.ALL_TAG, "1.0", "end"
            )
            self.text_widget.tag_remove(
                self.CURRENT_TAG, "1.0", "end"
            )
        except tk.TclError:
            pass

        if self._trace_id is not None:
            try:
                self.query_var.trace_remove(
                    "write",
                    self._trace_id,
                )
            except (tk.TclError, AttributeError):
                pass

            self._trace_id = None

        try:
            self.dialog.destroy()
        except tk.TclError:
            pass


def open_search_dialog(parent, text_widget, app=None):
    """Crea e restituisce il dialogo di ricerca."""

    return SearchDialog(parent, text_widget, app)
