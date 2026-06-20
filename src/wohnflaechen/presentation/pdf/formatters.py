"""HTML-Formatierung für PDF-Templates."""

import re

from markupsafe import escape, Markup

_SECTION_TITLE_PATTERN = re.compile(r"^(\d+\.\s.+)$", re.MULTILINE)
_NUMBER_PATTERN = re.compile(r"\d+,\d+")


def _round_german_number(match: re.Match[str]) -> str:
    value = float(match.group(0).replace(",", "."))
    return f"{value:.2f}".replace(".", ",")


def round_calculation_text(text: str) -> str:
    """Rundet alle Dezimalzahlen in Berechnungswegen auf zwei Nachkommastellen."""
    return _NUMBER_PATTERN.sub(_round_german_number, text)


def calculation_html(text: str) -> Markup:
    """Berechnungsweg mit Zeilenumbrüchen und + für Folgezeilen."""
    if not text:
        return Markup("")

    text = round_calculation_text(text)
    html_lines: list[str] = []
    line_in_section = 0

    for raw_line in text.split("\n"):
        line = raw_line.strip()
        if not line:
            continue

        if line.startswith("Abzüge"):
            if html_lines:
                html_lines.append("<br/>")
            html_lines.append(str(escape(line)))
            line_in_section = 0
            continue

        if line.startswith("- ") or line.startswith("+ "):
            html_lines.append(str(escape(line)))
            line_in_section += 1
            continue

        if line_in_section == 0:
            html_lines.append(str(escape(line)))
        else:
            html_lines.append(str(escape(f"+ {line}")))

        line_in_section += 1

    return Markup("<br/>".join(html_lines))


def name_html(text: str) -> Markup:
    """Raumbezeichnung – Schrägstrich wird als Zeilenumbruch dargestellt."""
    if not text:
        return Markup("")
    if "/" in text:
        parts = [escape(part.strip()) for part in text.split("/") if part.strip()]
        return Markup("<br/>".join(parts))
    return Markup(str(escape(text)).replace("\n", "<br/>"))


def multiline_html(text: str) -> Markup:
    """Freitext mit Zeilenumbrüchen."""
    if not text:
        return Markup("")
    return Markup(str(escape(text)).replace("\n", "<br/>"))


def preface_content_html(text: str) -> Markup:
    """Vorbemerkungen mit fetten Abschnittstiteln (1.–6.)."""
    if not text.strip():
        return Markup("")

    blocks = [block.strip() for block in text.split("\n\n") if block.strip()]
    parts: list[str] = []

    for block in blocks:
        lines = block.split("\n", 1)
        title = lines[0].strip()
        body = lines[1].strip() if len(lines) > 1 else ""

        if re.match(r"^\d+\.\s", title):
            body_html = str(escape(body)).replace("\n", "<br/>") if body else ""
            if body_html:
                parts.append(f"<p><strong>{escape(title)}</strong><br/>{body_html}</p>")
            else:
                parts.append(f"<p><strong>{escape(title)}</strong></p>")
        else:
            parts.append(f"<p>{multiline_html(block)}</p>")

    return Markup("".join(parts))


def paragraphs_html(text: str) -> Markup:
    """Mehrere Absätze als HTML."""
    if not text:
        return Markup("")
    parts = [part.strip() for part in text.split("\n\n") if part.strip()]
    if not parts:
        return multiline_html(text)
    return Markup("".join(f"<p>{multiline_html(part)}</p>" for part in parts))
