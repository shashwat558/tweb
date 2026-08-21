from __future__ import annotations

from urllib.parse import urljoin

from bs4 import BeautifulSoup, NavigableString, Tag

from tweb.parser.css import (
    css_style_to_rich,
    get_element_default_color,
    get_element_default_style,
    merge_styles,
    parse_inline_style,
)
from tweb.parser.elements import (
    Blockquote,
    CodeBlock,
    Document,
    Form,
    FormField,
    Heading,
    HorizontalRule,
    Image,
    Link,
    List,
    ListItem,
    Paragraph,
    Preformatted,
    Table,
    TableCell,
    TableRow,
    Text,
)


class HTMLParser:
    def __init__(self) -> None:
        self._link_counter = 0
        self._links: list[Link] = []
        self._form_counter = 0

    def parse(self, html: str, base_url: str) -> Document:
        self._link_counter = 0
        self._links = []
        self._form_counter = 0
        soup = BeautifulSoup(html, "lxml")
        title = self._extract_title(soup)
        body = soup.find("body") or soup
        blocks = self._parse_element(body, base_url)
        return Document(title=title, blocks=blocks, links=list(self._links))

    def _extract_title(self, soup: BeautifulSoup) -> str:
        title_tag = soup.find("title")
        if title_tag and isinstance(title_tag.string, str):
            return title_tag.string.strip()
        h1 = soup.find("h1")
        if h1:
            return h1.get_text(strip=True)
        return "Untitled"

    def _get_element_style(self, element: Tag) -> str:
        inline = parse_inline_style(element.get("style", ""))
        inline_rich = css_style_to_rich(inline)

        default_style = get_element_default_style(element.name)
        default_color = get_element_default_color(element.name)

        final_style = merge_styles(default_style, inline_rich)

        if inline.color and not default_color:
            pass
        elif default_color and not inline.color:
            if "on " not in final_style:
                final_style = merge_styles(final_style, default_color)

        return final_style

    def _get_element_color(self, element: Tag) -> tuple[str | None, str | None]:
        inline = parse_inline_style(element.get("style", ""))
        default_color = get_element_default_color(element.name)

        color = inline.color or default_color
        bg_color = inline.bg_color

        return color, bg_color

    def _parse_element(self, element: Tag | NavigableString, base_url: str) -> list:
        blocks: list = []
        if isinstance(element, NavigableString):
            text = str(element).strip()
            if text:
                blocks.append(Paragraph(text=text))
            return blocks

        tag = element.name

        if tag in ("script", "style", "noscript", "head"):
            return blocks

        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            level = int(tag[1])
            text = element.get_text(strip=True)
            if text:
                rich_style = self._get_element_style(element)
                blocks.append(Heading(level=level, text=text, rich_style=rich_style))
            return blocks

        if tag == "p":
            text = element.get_text(strip=True)
            if text:
                parts = self._parse_inline(element, base_url)
                rich_style = self._get_element_style(element)
                blocks.append(Paragraph(text=text, parts=parts, rich_style=rich_style))
            return blocks

        if tag == "a":
            href = element.get("href", "")
            text = element.get_text(strip=True)
            if href and text:
                url = urljoin(base_url, href)
                rich_style = self._get_element_style(element)
                link = Link(url=url, text=text, index=self._link_counter)
                self._link_counter += 1
                self._links.append(link)
                blocks.append(link)
            return blocks

        if tag == "img":
            src = element.get("src", "")
            alt = element.get("alt", "image")
            url = urljoin(base_url, src) if src else ""
            blocks.append(Image(url=url, alt=alt or "image"))
            return blocks

        if tag in ("ul", "ol"):
            ordered = tag == "ol"
            items = self._parse_list_items(element, base_url)
            if items:
                blocks.append(List(ordered=ordered, items=items))
            return blocks

        if tag == "pre":
            code_tag = element.find("code")
            text = (code_tag or element).get_text()
            lang = ""
            if code_tag and code_tag.get("class"):
                for cls in code_tag["class"]:
                    if cls.startswith("language-"):
                        lang = cls[9:]
                        break
            rich_style = self._get_element_style(element)
            blocks.append(CodeBlock(language=lang, code=text, rich_style=rich_style))
            return blocks

        if tag == "blockquote":
            inner_blocks = []
            for child in element.children:
                inner_blocks.extend(self._parse_element(child, base_url))
            if inner_blocks:
                rich_style = self._get_element_style(element)
                blocks.append(Blockquote(blocks=inner_blocks, rich_style=rich_style))
            return blocks

        if tag == "hr":
            blocks.append(HorizontalRule())
            return blocks

        if tag == "table":
            table = self._parse_table(element, base_url)
            if table:
                blocks.append(table)
            return blocks

        if tag == "br":
            return blocks

        if tag == "form":
            form = self._parse_form(element, base_url)
            if form:
                blocks.append(form)
            return blocks

        if tag == "li":
            blocks.extend(self._parse_list_item(element, base_url))
            return blocks

        for child in element.children:
            blocks.extend(self._parse_element(child, base_url))

        return blocks

    def _parse_inline(self, element: Tag, base_url: str) -> list[Text]:
        parts: list[Text] = []
        for child in element.children:
            if isinstance(child, NavigableString):
                text = str(child)
                if text.strip():
                    parts.append(Text(content=text))
            elif isinstance(child, Tag):
                text = child.get_text()
                if text.strip():
                    inline_css = parse_inline_style(child.get("style", ""))
                    color, bg_color = self._get_element_color(child)

                    rich_parts: list[str] = []
                    if child.name in ("strong", "b"):
                        rich_parts.append("bold")
                    if child.name in ("em", "i"):
                        rich_parts.append("italic")
                    if child.name == "u":
                        rich_parts.append("underline")
                    if child.name == "code":
                        rich_parts.append("on grey11")
                    if child.name in ("del", "s"):
                        rich_parts.append("strike")

                    if inline_css.font_weight in ("bold", "bolder", "600", "700", "800", "900"):
                        rich_parts.append("bold")
                    if inline_css.font_style == "italic":
                        rich_parts.append("italic")
                    if inline_css.text_decoration and "underline" in inline_css.text_decoration:
                        rich_parts.append("underline")
                    if inline_css.text_decoration and "line-through" in inline_css.text_decoration:
                        rich_parts.append("strike")
                    if inline_css.opacity is not None and inline_css.opacity < 0.5:
                        rich_parts.append("dim")

                    if color:
                        rich_parts.append(color)
                    if bg_color:
                        rich_parts.append(f"on {bg_color}")

                    rich_style_str = " ".join(rich_parts)

                    parts.append(
                        Text(
                            content=text,
                            bold=child.name in ("strong", "b") or inline_css.font_weight in ("bold", "bolder"),
                            italic=child.name in ("em", "i") or inline_css.font_style == "italic",
                            underline=child.name == "u" or (inline_css.text_decoration and "underline" in inline_css.text_decoration),
                            code=child.name == "code",
                            color=color,
                            bg_color=bg_color,
                            strike=child.name in ("del", "s") or (inline_css.text_decoration and "line-through" in inline_css.text_decoration),
                            rich_style=rich_style_str,
                        )
                    )
        return parts

    def _parse_list_items(self, element: Tag, base_url: str) -> list[ListItem]:
        items: list[ListItem] = []
        for li in element.find_all("li", recursive=False):
            blocks: list = []
            for child in li.children:
                blocks.extend(self._parse_element(child, base_url))
            if blocks:
                items.append(ListItem(blocks=blocks))
        return items

    def _parse_list_item(self, element: Tag, base_url: str) -> list:
        blocks: list = []
        for child in element.children:
            blocks.extend(self._parse_element(child, base_url))
        return blocks

    def _parse_table(self, element: Tag, base_url: str) -> Table | None:
        rows: list[TableRow] = []
        for tr in element.find_all("tr"):
            cells: list[TableCell] = []
            for cell in tr.find_all(["td", "th"]):
                text = cell.get_text(strip=True)
                rich_style = self._get_element_style(cell)
                cells.append(TableCell(text=text, header=cell.name == "th", rich_style=rich_style))
            if cells:
                rows.append(TableRow(cells=cells))
        return Table(rows=rows) if rows else None

    def _parse_form(self, element: Tag, base_url: str) -> Form | None:
        action = element.get("action", "")
        method = element.get("method", "GET").upper()
        if action:
            action = urljoin(base_url, action)

        self._form_counter += 1
        form_id = self._form_counter
        fields: list[FormField] = []
        hidden_fields: dict[str, str] = {}
        submit_text = "Submit"

        for input_tag in element.find_all("input"):
            name = input_tag.get("name", "")
            input_type = input_tag.get("type", "text").lower()
            value = input_tag.get("value", "")
            placeholder = input_tag.get("placeholder", "")

            if input_type == "hidden":
                if name:
                    hidden_fields[name] = value
            elif input_type in ("text", "search", "email", "password", "url", "number"):
                fields.append(FormField(
                    name=name,
                    field_type=input_type,
                    value=value,
                    placeholder=placeholder,
                    form_id=form_id,
                ))
            elif input_type == "submit":
                submit_text = value or "Submit"
            elif input_type == "checkbox":
                checked = input_tag.get("checked") is not None
                fields.append(FormField(
                    name=name,
                    field_type="checkbox",
                    value=value or "on",
                    checked=checked,
                    form_id=form_id,
                ))
            elif input_type == "radio":
                checked = input_tag.get("checked") is not None
                fields.append(FormField(
                    name=name,
                    field_type="radio",
                    value=value,
                    checked=checked,
                    form_id=form_id,
                ))

        for select_tag in element.find_all("select"):
            name = select_tag.get("name", "")
            options: list[str] = []
            for option in select_tag.find_all("option"):
                opt_value = option.get("value", option.get_text(strip=True))
                if opt_value:
                    options.append(opt_value)
            if name:
                fields.append(FormField(
                    name=name,
                    field_type="select",
                    options=options,
                    form_id=form_id,
                ))

        for textarea in element.find_all("textarea"):
            name = textarea.get("name", "")
            placeholder = textarea.get("placeholder", "")
            fields.append(FormField(
                name=name,
                field_type="textarea",
                placeholder=placeholder,
                form_id=form_id,
            ))

        for button in element.find_all("button"):
            text = button.get_text(strip=True)
            if text:
                submit_text = text

        return Form(
            action=action,
            method=method,
            fields=fields,
            submit_text=submit_text,
            form_id=form_id,
            hidden_fields=hidden_fields,
        )
