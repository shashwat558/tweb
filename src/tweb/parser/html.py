from __future__ import annotations

from urllib.parse import urljoin

from bs4 import BeautifulSoup, NavigableString, Tag

from tweb.parser.elements import (
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

    def parse(self, html: str, base_url: str) -> Document:
        self._link_counter = 0
        self._links = []
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
                blocks.append(Heading(level=level, text=text))
            return blocks

        if tag == "p":
            text = element.get_text(strip=True)
            if text:
                parts = self._parse_inline(element, base_url)
                blocks.append(Paragraph(text=text, parts=parts))
            return blocks

        if tag == "a":
            href = element.get("href", "")
            text = element.get_text(strip=True)
            if href and text:
                url = urljoin(base_url, href)
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
            blocks.append(CodeBlock(language=lang, code=text))
            return blocks

        if tag == "blockquote":
            text = element.get_text(strip=True)
            if text:
                blocks.append(Paragraph(text=f"> {text}"))
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
                    parts.append(
                        Text(
                            content=text,
                            bold=child.name in ("strong", "b"),
                            italic=child.name in ("em", "i"),
                            underline=child.name == "u",
                            code=child.name == "code",
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

    def _parse_table(self, element: Tag, base_url: str) -> Table | None:
        rows: list[TableRow] = []
        for tr in element.find_all("tr"):
            cells: list[TableCell] = []
            for cell in tr.find_all(["td", "th"]):
                text = cell.get_text(strip=True)
                cells.append(TableCell(text=text, header=cell.name == "th"))
            if cells:
                rows.append(TableRow(cells=cells))
        return Table(rows=rows) if rows else None

    def _parse_form(self, element: Tag, base_url: str) -> Form | None:
        action = element.get("action", "")
        method = element.get("method", "GET").upper()
        if action:
            action = urljoin(base_url, action)

        fields: list[FormField] = []
        submit_text = "Submit"

        for input_tag in element.find_all("input"):
            name = input_tag.get("name", "")
            input_type = input_tag.get("type", "text").lower()
            value = input_tag.get("value", "")
            placeholder = input_tag.get("placeholder", "")
            if input_type in ("text", "search", "email", "password", "url", "number"):
                fields.append(FormField(
                    name=name,
                    field_type=input_type,
                    value=value,
                    placeholder=placeholder,
                ))
            elif input_type == "submit":
                submit_text = value or "Submit"

        for textarea in element.find_all("textarea"):
            name = textarea.get("name", "")
            placeholder = textarea.get("placeholder", "")
            fields.append(FormField(
                name=name,
                field_type="textarea",
                placeholder=placeholder,
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
        ) if fields else None
