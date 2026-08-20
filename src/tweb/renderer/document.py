from __future__ import annotations

from rich.text import Text as RichText

from tweb.parser.elements import (
    Block,
    CodeBlock,
    Document,
    Heading,
    HorizontalRule,
    Image,
    Link,
    List,
    ListItem,
    Paragraph,
    Table,
)


class DocumentRenderer:
    def __init__(self, width: int = 80) -> None:
        self._width = width

    def set_width(self, width: int) -> None:
        self._width = width

    def render(self, document: Document) -> RichText:
        output = RichText()
        output.append(document.title, style="bold white on blue")
        output.append("\n\n")

        for block in document.blocks:
            output.append_text(self._render_block(block))
            output.append("\n")

        if document.links:
            output.append("\n")
            for link in document.links:
                output.append(f"[{link.index + 1}] ", style="bold cyan")
                output.append(link.text, style="underline blue")
                output.append("\n")

        return output

    def _render_block(self, block: Block) -> RichText:
        output = RichText()

        if isinstance(block, Heading):
            style = self._heading_style(block.level)
            output.append(block.text, style=style)
            output.append("\n")

        elif isinstance(block, Paragraph):
            if block.parts:
                for part in block.parts:
                    style = ""
                    if part.bold:
                        style += " bold"
                    if part.italic:
                        style += " italic"
                    if part.underline:
                        style += " underline"
                    if part.code:
                        style += " cyan"
                    output.append(part.content, style=style.strip() or None)
            else:
                output.append(block.text)
            output.append("\n")

        elif isinstance(block, Link):
            output.append(f"[{block.index + 1}] ", style="bold cyan")
            output.append(block.text, style="underline blue")
            output.append("\n")

        elif isinstance(block, Image):
            output.append(f"[Image: {block.alt}]", style="dim")
            output.append("\n")

        elif isinstance(block, List):
            output.append_text(self._render_list(block))

        elif isinstance(block, CodeBlock):
            output.append("─" * min(40, self._width))
            output.append("\n")
            output.append(block.code, style="cyan")
            output.append("\n")
            output.append("─" * min(40, self._width))
            output.append("\n")

        elif isinstance(block, HorizontalRule):
            output.append("─" * self._width, style="dim")
            output.append("\n")

        elif isinstance(block, Table):
            output.append_text(self._render_table(block))

        return output

    def _heading_style(self, level: int) -> str:
        styles = {
            1: "bold white on blue",
            2: "bold white",
            3: "bold",
            4: "bold cyan",
            5: "cyan",
            6: "dim cyan",
        }
        return styles.get(level, "bold")

    def _render_list(self, lst: List) -> RichText:
        output = RichText()
        for i, item in enumerate(lst.items):
            bullet = f"  {i + 1}." if lst.ordered else "  •"
            output.append(bullet, style="bold")
            output.append(" ")
            for block in item.blocks:
                if isinstance(block, Paragraph):
                    output.append(block.text)
                elif isinstance(block, Link):
                    output.append(f"[{block.index + 1}] ", style="bold cyan")
                    output.append(block.text, style="underline blue")
            output.append("\n")
        return output

    def _render_table(self, table: Table) -> RichText:
        output = RichText()
        if not table.rows:
            return output

        num_cols = max(len(row.cells) for row in table.rows)
        col_widths = [0] * num_cols
        for row in table.rows:
            for i, cell in enumerate(row.cells):
                col_widths[i] = max(col_widths[i], len(cell.text))

        for row in table.rows:
            parts = []
            for i, cell in enumerate(row.cells):
                width = col_widths[i] if i < len(col_widths) else 10
                text = cell.text.ljust(width)
                if cell.header:
                    parts.append(f" {text} ")
                else:
                    parts.append(f" {text} ")
            output.append("│".join(parts))
            output.append("\n")

        sep = "┼".join("─" * (w + 2) for w in col_widths)
        output.append(sep, style="dim")
        output.append("\n")

        return output
