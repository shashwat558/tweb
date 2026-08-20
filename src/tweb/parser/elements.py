from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Text:
    content: str
    bold: bool = False
    italic: bool = False
    underline: bool = False
    code: bool = False


@dataclass
class Link:
    url: str
    text: str
    index: int = 0


@dataclass
class Image:
    url: str
    alt: str


@dataclass
class ListItem:
    blocks: list[Block] = field(default_factory=list)


@dataclass
class List:
    ordered: bool
    items: list[ListItem] = field(default_factory=list)


@dataclass
class Heading:
    level: int
    text: str


@dataclass
class Paragraph:
    text: str
    parts: list[Text] = field(default_factory=list)


@dataclass
class CodeBlock:
    language: str
    code: str


@dataclass
class Preformatted:
    text: str


@dataclass
class HorizontalRule:
    pass


@dataclass
class TableCell:
    text: str
    header: bool = False


@dataclass
class TableRow:
    cells: list[TableCell] = field(default_factory=list)


@dataclass
class Table:
    rows: list[TableRow] = field(default_factory=list)


@dataclass
class FormField:
    name: str
    field_type: str = "text"
    value: str = ""
    label: str = ""
    placeholder: str = ""


@dataclass
class Form:
    action: str = ""
    method: str = "GET"
    fields: list[FormField] = field(default_factory=list)
    submit_text: str = "Submit"


@dataclass
class Blockquote:
    blocks: list = field(default_factory=list)


Block = (
    Heading
    | Paragraph
    | Link
    | Image
    | List
    | CodeBlock
    | Preformatted
    | HorizontalRule
    | Table
    | Form
    | Blockquote
)


@dataclass
class Document:
    title: str
    blocks: list[Block] = field(default_factory=list)
    links: list[Link] = field(default_factory=list)
