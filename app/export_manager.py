"""Esportazione dei documenti Markdown in HTML e PDF."""

import os
from html.parser import HTMLParser
from tkinter import filedialog, messagebox
from xml.sax.saxutils import escape, quoteattr

from .markdown_renderer import markdown_to_html


class _Node:
    def __init__(self, tag="root", attrs=None):
        self.tag = tag
        self.attrs = dict(attrs or [])
        self.children = []


class _HTMLTreeParser(HTMLParser):
    """Costruisce un albero HTML minimale, sufficiente per l'esportazione PDF."""

    VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = _Node()
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs):
        node = _Node(tag.lower(), attrs)
        self.stack[-1].children.append(node)
        if tag.lower() not in self.VOID_TAGS:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.stack[-1].children.append(_Node(tag.lower(), attrs))

    def handle_endtag(self, tag):
        tag = tag.lower()
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                break

    def handle_data(self, data):
        self.stack[-1].children.append(data)


def _plain_text(node):
    if isinstance(node, str):
        return node
    if node.tag == "br":
        return "\n"
    if node.tag == "img":
        return node.attrs.get("alt", "")
    return "".join(_plain_text(child) for child in node.children)


def _inline_markup(node):
    """Converte l'HTML inline in markup Paragraph di ReportLab."""
    if isinstance(node, str):
        return escape(node).replace("\n", " ")

    tag = node.tag
    if tag == "img":
        return escape(node.attrs.get("alt", ""))
    if tag == "br":
        return "<br/>"

    content = "".join(_inline_markup(child) for child in node.children)
    if tag in ("strong", "b"):
        return "<b>{}</b>".format(content)
    if tag in ("em", "i"):
        return "<i>{}</i>".format(content)
    if tag == "u":
        return "<u>{}</u>".format(content)
    if tag == "del" or tag == "s" or tag == "strike":
        return '<font color="#666666"><strike>{}</strike></font>'.format(content)
    if tag == "code":
        return '<font name="Courier">{}</font>'.format(content)
    if tag == "a":
        href = node.attrs.get("href", "")
        if href.startswith(("http://", "https://", "mailto:")):
            return '<link href={} color="#0969da">{}</link>'.format(quoteattr(href), content)
        return content
    return content


def _find_nodes(node, tag):
    return [child for child in node.children if not isinstance(child, str) and child.tag == tag]


def _find_descendants(node, tag):
    found = []
    for child in node.children:
        if isinstance(child, str):
            continue
        if child.tag == tag:
            found.append(child)
        found.extend(_find_descendants(child, tag))
    return found


def _register_fonts():
    """Usa un font TrueType con supporto Unicode se disponibile."""
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    candidates = [
        (
            r"C:\Windows\Fonts\arial.ttf",
            r"C:\Windows\Fonts\arialbd.ttf",
            r"C:\Windows\Fonts\ariali.ttf",
            r"C:\Windows\Fonts\arialbi.ttf",
        ),
        (
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf",
        ),
        (
            "/Library/Fonts/Arial.ttf",
            "/Library/Fonts/Arial Bold.ttf",
            "/Library/Fonts/Arial Italic.ttf",
            "/Library/Fonts/Arial Bold Italic.ttf",
        ),
    ]
    for regular, bold, italic, bold_italic in candidates:
        if os.path.isfile(regular):
            try:
                pdfmetrics.registerFont(TTFont("MarkdownUnicode", regular))
                pdfmetrics.registerFont(TTFont("MarkdownUnicode-Bold", bold if os.path.isfile(bold) else regular))
                pdfmetrics.registerFont(TTFont("MarkdownUnicode-Italic", italic if os.path.isfile(italic) else regular))
                pdfmetrics.registerFont(TTFont("MarkdownUnicode-BoldItalic", bold_italic if os.path.isfile(bold_italic) else regular))
                pdfmetrics.registerFontFamily(
                    "MarkdownUnicode",
                    normal="MarkdownUnicode",
                    bold="MarkdownUnicode-Bold",
                    italic="MarkdownUnicode-Italic",
                    boldItalic="MarkdownUnicode-BoldItalic",
                )
                return "MarkdownUnicode"
            except Exception:
                continue
    return "Helvetica"


def _pdf_story(markdown_text):
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        HRFlowable, ListFlowable, ListItem, Paragraph, Preformatted,
        Spacer, Table, TableStyle,
    )

    html = markdown_to_html(markdown_text)
    parser = _HTMLTreeParser()
    parser.feed(html)
    parser.close()
    font_name = _register_fonts()

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="MarkdownBody", parent=styles["BodyText"], fontName=font_name,
        fontSize=10, leading=14, spaceAfter=7, alignment=TA_LEFT,
        wordWrap="CJK",
    ))
    for level in range(1, 7):
        base_size = max(12, 23 - (level - 1) * 2)
        styles.add(ParagraphStyle(
            name="MarkdownH{}".format(level), parent=styles["Heading1"],
            fontName=font_name, fontSize=base_size,
            leading=base_size + 3, spaceBefore=12 if level == 1 else 8,
            spaceAfter=7, keepWithNext=True,
        ))
    styles.add(ParagraphStyle(
        name="MarkdownQuote", parent=styles["MarkdownBody"],
        leftIndent=12, borderColor=colors.HexColor("#b8c2cc"),
        borderWidth=1, borderPadding=6, textColor=colors.HexColor("#555555"),
    ))
    styles.add(ParagraphStyle(
        name="MarkdownCell", parent=styles["MarkdownBody"],
        fontSize=8.5, leading=11, spaceAfter=0,
    ))
    styles.add(ParagraphStyle(
        name="MarkdownCode", parent=styles["Code"],
        fontName="Courier", fontSize=8.5, leading=11,
        leftIndent=6, rightIndent=6, spaceBefore=4, spaceAfter=9,
        backColor=colors.HexColor("#f3f5f7"), borderPadding=6,
    ))

    story = []

    def add_blocks(parent):
        for node in parent.children:
            if isinstance(node, str):
                if node.strip():
                    story.append(Paragraph(escape(node.strip()), styles["MarkdownBody"]))
                continue
            tag = node.tag
            if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
                level = int(tag[1])
                story.append(Paragraph(_inline_markup(node), styles["MarkdownH{}".format(level)]))
            elif tag == "p":
                markup = _inline_markup(node).strip()
                if markup:
                    story.append(Paragraph(markup, styles["MarkdownBody"]))
            elif tag == "pre":
                code_text = _plain_text(node).rstrip("\n")
                story.append(Preformatted(code_text, styles["MarkdownCode"]))
                story.append(Spacer(1, 5))
            elif tag in ("ul", "ol"):
                items = []
                for item in _find_nodes(node, "li"):
                    item_flowables = []
                    item_markup = _inline_markup(item).strip()
                    if item_markup:
                        item_flowables.append(Paragraph(item_markup, styles["MarkdownBody"]))
                    items.append(ListItem(item_flowables or [Paragraph(" ", styles["MarkdownBody"])], leftIndent=12))
                if items:
                    story.append(ListFlowable(
                        items, bulletType="bullet" if tag == "ul" else "1",
                        start="1", leftIndent=18, bulletFontName=font_name,
                    ))
                    story.append(Spacer(1, 5))
            elif tag == "blockquote":
                markup = "<br/>".join(_inline_markup(child) for child in node.children).strip()
                if markup:
                    story.append(Paragraph(markup, styles["MarkdownQuote"]))
            elif tag == "hr":
                story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#b8c2cc"), spaceBefore=6, spaceAfter=10))
            elif tag == "table":
                rows = []
                for tr in _find_descendants(node, "tr"):
                    cells = []
                    for cell in tr.children:
                        if not isinstance(cell, str) and cell.tag in ("th", "td"):
                            cell_markup = _inline_markup(cell).strip() or " "
                            cells.append(Paragraph(cell_markup, styles["MarkdownCell"]))
                    if cells:
                        rows.append(cells)
                if rows:
                    col_count = max(len(row) for row in rows)
                    for row in rows:
                        while len(row) < col_count:
                            row.append(Paragraph(" ", styles["MarkdownCell"]))
                    table = Table(rows, repeatRows=1, hAlign="LEFT")
                    table.setStyle(TableStyle([
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#b8c2cc")),
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#edf1f5")),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 5),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                        ("TOPPADDING", (0, 0), (-1, -1), 4),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ]))
                    story.extend([table, Spacer(1, 8)])
            elif tag in ("div", "section", "main", "body"):
                add_blocks(node)
            elif tag == "img":
                alt = node.attrs.get("alt", "")
                if alt:
                    story.append(Paragraph(escape(alt), styles["MarkdownBody"]))
            else:
                # Per tag HTML non previsti, conserva il testo invece di perderlo.
                if node.children:
                    add_blocks(node)

    add_blocks(parser.root)
    if not story:
        story.append(Paragraph(" ", styles["MarkdownBody"]))
    return story


class ExportManager:
    """Gestisce l'esportazione senza modificare il documento Markdown aperto."""

    def __init__(self, app):
        self.app = app

    def _suggested_name(self, extension):
        path = self.app.current_filepath
        if path:
            return os.path.splitext(os.path.basename(path))[0] + extension
        return ("document" if self.app.language == "en" else "documento") + extension

    def export_html(self):
        app = self.app
        path = filedialog.asksaveasfilename(
            parent=app.root,
            title=app.t("export_html_title"),
            defaultextension=".html",
            initialfile=self._suggested_name(".html"),
            filetypes=[("HTML", "*.html *.htm"), (app.t("all_files"), "*.*")],
        )
        if not path:
            return False

        try:
            markdown_text = app.text_editor.get("1.0", "end-1c")
            html_body = markdown_to_html(markdown_text)
            title = escape(os.path.splitext(os.path.basename(path))[0])
            document = """<!DOCTYPE html>
<html lang="{language}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
{css}
body {{ max-width: 960px; margin: 0 auto; }}
</style>
</head>
<body><main id="markdown-content">{body}</main></body>
</html>
""".format(language="it" if app.language == "it" else "en", title=title, css=app.PREVIEW_CSS, body=html_body)
            with open(path, "w", encoding="utf-8", newline="\n") as file:
                file.write(document)
        except (OSError, UnicodeError, ValueError) as exc:
            messagebox.showerror(app.t("export_error_title"), "{}\n\n{}".format(app.t("export_error_message"), exc), parent=app.root)
            return False

        messagebox.showinfo(app.t("export_done_title"), app.t("export_html_done"), parent=app.root)
        return True

    def export_pdf(self):
        app = self.app
        path = filedialog.asksaveasfilename(
            parent=app.root,
            title=app.t("export_pdf_title"),
            defaultextension=".pdf",
            initialfile=self._suggested_name(".pdf"),
            filetypes=[("PDF", "*.pdf"), (app.t("all_files"), "*.*")],
        )
        if not path:
            return False

        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.units import mm
            from reportlab.platypus import SimpleDocTemplate, Preformatted

            markdown_text = app.text_editor.get("1.0", "end-1c")
            story = _pdf_story(markdown_text)
            doc = SimpleDocTemplate(
                path, pagesize=A4,
                rightMargin=18 * mm, leftMargin=18 * mm,
                topMargin=18 * mm, bottomMargin=18 * mm,
                title=os.path.splitext(os.path.basename(path))[0],
                author="Markdown Editor",
            )

            def draw_page(canvas, document):
                canvas.saveState()
                canvas.setStrokeColor(colors.HexColor("#d0d7de"))
                canvas.line(18 * mm, 13 * mm, A4[0] - 18 * mm, 13 * mm)
                canvas.setFont("Helvetica", 8)
                canvas.setFillColor(colors.HexColor("#666666"))
                canvas.drawRightString(A4[0] - 18 * mm, 8 * mm, str(document.page))
                canvas.restoreState()

            doc.build(story, onFirstPage=draw_page, onLaterPages=draw_page)
        except ImportError:
            messagebox.showerror(
                app.t("export_error_title"),
                app.t("pdf_dependency_missing"),
                parent=app.root,
            )
            return False
        except Exception as exc:
            messagebox.showerror(
                app.t("export_error_title"),
                "{}\n\n{}".format(app.t("export_error_message"), exc),
                parent=app.root,
            )
            return False

        messagebox.showinfo(app.t("export_done_title"), app.t("export_pdf_done"), parent=app.root)
        return True
