from __future__ import annotations

from rich.text import Text
from textual import on
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Button, Checkbox, Input, Select, Static, TextArea

from tweb.parser.elements import Form, FormField


class FormFieldWidget(Widget):
    can_focus = True
    can_focus_children = True

    def __init__(self, field: FormField, **kwargs) -> None:
        super().__init__(**kwargs)
        self.field = field

    def compose(self) -> ComposeResult:
        label = self.field.name or self.field.field_type
        if self.field.label:
            label = self.field.label

        if self.field.field_type in ("text", "search", "email", "password", "url", "number"):
            yield Static(f"  {label}:", classes="form-label")
            yield Input(
                placeholder=self.field.placeholder or label,
                value=self.field.value,
                id=f"field-{self.field.name}",
                classes="form-input",
            )
        elif self.field.field_type == "textarea":
            yield Static(f"  {label}:", classes="form-label")
            yield TextArea(id=f"field-{self.field.name}", classes="form-textarea")
        elif self.field.field_type == "select":
            yield Static(f"  {label}:", classes="form-label")
            options = [(opt, opt) for opt in self.field.options]
            if options:
                yield Select(options, id=f"field-{self.field.name}", classes="form-select")
        elif self.field.field_type == "checkbox":
            yield Checkbox(
                label,
                value=self.field.checked,
                id=f"field-{self.field.name}",
                classes="form-checkbox",
            )
        elif self.field.field_type == "radio":
            yield Static(f"  {label}: [{self.field.value}]", classes="form-label")
        else:
            yield Static(f"  {label}: [{self.field.value}]", classes="form-label")


class FormSubmitButton(Widget):
    can_focus = True
    can_focus_children = False

    class Submitted(Message):
        def __init__(self, form_id: int) -> None:
            super().__init__()
            self.form_id = form_id

    def __init__(self, form_id: int, label: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.form_id = form_id
        self.label_text = label

    def compose(self) -> ComposeResult:
        yield Button(self.label_text, id=f"submit-{self.form_id}", variant="primary", classes="form-submit")

    @on(Button.Pressed)
    def _on_button_pressed(self, event: Button.Pressed) -> None:
        self.post_message(self.Submitted(self.form_id))


class FormContainer(Vertical):
    can_focus = False
    can_focus_children = True

    def __init__(self, form: Form, fields: list, submit_id: int, submit_text: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.form = form
        self._fields = fields
        self._submit_id = submit_id
        self._submit_text = submit_text

    def compose(self) -> ComposeResult:
        for field in self._fields:
            yield FormFieldWidget(field)
        yield FormSubmitButton(self._submit_id, self._submit_text)


class ContentView(Widget):
    can_focus = True
    can_focus_children = True

    class FocusRequested(Message):
        pass

    class LinkClicked(Message):
        def __init__(self, url: str) -> None:
            super().__init__()
            self.url = url

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._content = ""
        self._rich_content: Text | None = None
        self._link_positions: list[tuple[int, int, str]] = []

    def compose(self) -> ComposeResult:
        with Vertical(id="content-inner"):
            yield Static(self._content, id="content-text")

    def set_content(self, content: str | Text) -> None:
        if isinstance(content, Text):
            self._rich_content = content
            self._content = content.plain
        else:
            self._content = content
            self._rich_content = None
        static = self.query_one("#content-text", Static)
        if self._rich_content:
            static.update(self._rich_content)
        else:
            static.update(content)

    def set_widgets(self, widgets: list) -> None:
        container = self.query_one("#content-inner")
        container.remove_children()
        for w in widgets:
            container.mount(w)

    def get_content(self) -> str:
        return self._content


class StatusBar(Static):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._status = "Ready"

    def compose(self) -> ComposeResult:
        yield Static(self._status, id="status-text")

    def set_status(self, status: str) -> None:
        self._status = status
        self.query_one("#status-text", Static).update(status)
