
from html import escape
from html.parser import HTMLParser

import emoji
import markdown2


TWEMOJI_BASE_URL = (
    "https://cdn.jsdelivr.net/gh/jdecked/twemoji@17.0.3/assets/72x72/"
)


class EmojiHTMLRenderer(HTMLParser):
    """Sostituisce le emoji nell'HTML con immagini Twemoji."""

    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.parts = []
        self._protected_tags = []

    def handle_starttag(self, tag, attrs):
        self.parts.append(self.get_starttag_text() or f"<{tag}>")
        if tag.lower() in ("script", "style"):
            self._protected_tags.append(tag.lower())

    def handle_startendtag(self, tag, attrs):
        self.parts.append(self.get_starttag_text() or f"<{tag} />")

    def handle_endtag(self, tag):
        self.parts.append(f"</{tag}>")
        tag = tag.lower()

        if tag in self._protected_tags:
            for index in range(
                len(self._protected_tags) - 1, -1, -1
            ):
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

            codepoints = "-".join(
                f"{ord(char):x}"
                for char in character
                if char not in ("\ufe0e", "\ufe0f")
            )

            if codepoints:
                label = escape(character, quote=True)
                src = f"{TWEMOJI_BASE_URL}{codepoints}.png"

                self.parts.append(
                    f'<img class="emoji" src="{src}" '
                    f'alt="{label}" title="{label}">'
                )
            else:
                self.parts.append(character)

            cursor = end

        self.parts.append(data[cursor:])

    def handle_entityref(self, name):
        self.parts.append(f"&{name};")

    def handle_charref(self, name):
        self.parts.append(f"&#{name};")

    def handle_comment(self, data):
        self.parts.append(f"<!--{data}-->")

    def handle_decl(self, decl):
        self.parts.append(f"<!{decl}>")

    def handle_pi(self, data):
        self.parts.append(f"<?{data}>")

    def get_html(self):
        return "".join(self.parts)


def render_emojis_in_html(html_text):
    """Restituisce l'HTML con le emoji trasformate in immagini."""
    parser = EmojiHTMLRenderer()
    parser.feed(html_text)
    parser.close()
    return parser.get_html()


def markdown_to_html(markdown_text):
    """Converte il testo Markdown in HTML e rende le emoji."""
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
