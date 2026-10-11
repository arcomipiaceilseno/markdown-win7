import os
import sys
import tkinter as tk

from app import MarkdownViewerApp


def main():
    root = tk.Tk()
    app = MarkdownViewerApp(root)

    # Windows/macOS/Linux passano il percorso come argomento quando
    # un file viene aperto con un'applicazione associata.
    filepath = next(
        (arg for arg in sys.argv[1:] if os.path.isfile(arg)),
        None,
    )
    if filepath:
        root.after(0, lambda path=filepath: app.file_manager.open_path(path, ask_before_discard=False))

    root.mainloop()


if __name__ == "__main__":
    main()
