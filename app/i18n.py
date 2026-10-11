"""Traduzioni dell'interfaccia. Per aggiungere una lingua, aggiungere un dizionario."""

TRANSLATIONS = {
    "it": {
        "language": "Lingua", "italian": "Italiano", "english": "English",
        "file": "File", "new": "Nuovo", "open": "Apri file .md...", "save": "Salva",
        "save_as": "Salva con nome...", "export": "Esporta", "export_html": "Come HTML...", "export_pdf": "Come PDF...",
        "export_html_title": "Esporta documento in HTML", "export_pdf_title": "Esporta documento in PDF",
        "export_error_title": "Errore di esportazione", "export_error_message": "Impossibile esportare il documento.",
        "export_done_title": "Esportazione completata", "export_html_done": "File HTML esportato correttamente.",
        "export_pdf_done": "File PDF esportato correttamente.",
        "pdf_dependency_missing": "Per esportare in PDF installa la dipendenza reportlab con: py -m pip install reportlab",
        "exit": "Esci", "edit": "Modifica", "search": "Cerca...",
        "bold": "Grassetto", "italic": "Corsivo", "link": "Link", "undo": "Annulla", "redo": "Ripeti",
        "functions": "Funzioni", "sync_scroll": "Scroll sincronizzato", "source": "Sorgente Markdown",
        "preview": "Anteprima formattata", "new_document": "Nuovo documento", "saved": "Salvato",
        "unsaved": "Modifiche non salvate", "row": "Riga", "column": "colonna",
        "discard_title": "Modifiche non salvate", "discard_prompt": "Vuoi salvare le modifiche prima di continuare?",
        "open_title": "Apri un file Markdown", "markdown_files": "File Markdown", "all_files": "Tutti i file",
        "open_error": "Errore di apertura", "read_error": "Non riesco a leggere il file.",
        "save_title": "Salva il documento Markdown", "save_error": "Errore di salvataggio",
        "write_error": "Non riesco a salvare il file.", "saved_title": "Salvataggio", "saved_message": "File salvato correttamente.",
        "bold_placeholder": "testo in grassetto", "italic_placeholder": "testo in corsivo", "strike_placeholder": "testo barrato",
        "code_placeholder": "codice", "block_code": "Blocco codice", "quote": "❝ Citazione", "list": "• Elenco",
        "numbered_list": "1. Elenco", "image": "Immagine", "separator": "— Separatore", "search_title": "Cerca",
        "search_prompt": "Inserisci il testo da cercare.", "search_label": "Testo da cercare:",
        "case_sensitive": "Distingui maiuscole/minuscole", "previous": "Precedente", "next": "Successivo", "close": "Chiudi",
        "no_matches": "Nessuna corrispondenza trovata.", "matches": "{} corrispondenza/e trovata/e.", "result": "Risultato {} di {}.",
        "image_desc": "descrizione immagine", "link_text": "testo del link", "example_url": "https://esempio.com",
    },
    "en": {
        "language": "Language", "italian": "Italiano", "english": "English",
        "file": "File", "new": "New", "open": "Open .md file...", "save": "Save",
        "save_as": "Save as...", "export": "Export", "export_html": "As HTML...", "export_pdf": "As PDF...",
        "export_html_title": "Export document to HTML", "export_pdf_title": "Export document to PDF",
        "export_error_title": "Export error", "export_error_message": "Unable to export the document.",
        "export_done_title": "Export complete", "export_html_done": "HTML file exported successfully.",
        "export_pdf_done": "PDF file exported successfully.",
        "pdf_dependency_missing": "To export to PDF, install the reportlab dependency with: py -m pip install reportlab",
        "exit": "Exit", "edit": "Edit", "search": "Find...",
        "bold": "Bold", "italic": "Italic", "link": "Link", "undo": "Undo", "redo": "Redo",
        "functions": "Tools", "sync_scroll": "Synchronized scrolling", "source": "Markdown source",
        "preview": "Formatted preview", "new_document": "New document", "saved": "Saved",
        "unsaved": "Unsaved changes", "row": "Line", "column": "column",
        "discard_title": "Unsaved changes", "discard_prompt": "Do you want to save changes before continuing?",
        "open_title": "Open a Markdown file", "markdown_files": "Markdown files", "all_files": "All files",
        "open_error": "Open error", "read_error": "Unable to read the file.",
        "save_title": "Save Markdown document", "save_error": "Save error",
        "write_error": "Unable to save the file.", "saved_title": "Saved", "saved_message": "File saved successfully.",
        "bold_placeholder": "bold text", "italic_placeholder": "italic text", "strike_placeholder": "strikethrough text",
        "code_placeholder": "code", "block_code": "Code block", "quote": "❝ Quote", "list": "• List",
        "numbered_list": "1. List", "image": "Image", "separator": "— Horizontal rule", "search_title": "Find",
        "search_prompt": "Enter text to find.", "search_label": "Text to find:",
        "case_sensitive": "Match case", "previous": "Previous", "next": "Next", "close": "Close",
        "no_matches": "No matches found.", "matches": "{} match(es) found.", "result": "Result {} of {}.",
        "image_desc": "image description", "link_text": "link text", "example_url": "https://example.com",
    },
}


def translate(language, key, *args):
    """Restituisce la traduzione richiesta; le chiavi mancanti ricadono sull'italiano."""
    text = TRANSLATIONS.get(language, TRANSLATIONS["it"]).get(
        key, TRANSLATIONS["it"].get(key, key)
    )
    return text.format(*args) if args else text
