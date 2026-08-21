from tweb.parser.html import HTMLParser
from tweb.parser.elements import Form, FormField


class TestFormParsing:
    def setup_method(self) -> None:
        self.parser = HTMLParser()

    def test_parse_simple_form(self) -> None:
        html = """<html><body>
        <form action="/search" method="GET">
            <input type="text" name="q" placeholder="Search">
            <input type="submit" value="Go">
        </form>
        </body></html>"""
        doc = self.parser.parse(html, "https://example.com")
        assert len(doc.blocks) == 1
        assert isinstance(doc.blocks[0], Form)
        form = doc.blocks[0]
        assert form.action == "https://example.com/search"
        assert form.method == "GET"
        assert len(form.fields) == 1
        assert form.fields[0].name == "q"
        assert form.fields[0].field_type == "text"
        assert form.submit_text == "Go"

    def test_parse_hidden_fields(self) -> None:
        html = """<html><body>
        <form action="/submit">
            <input type="hidden" name="token" value="abc123">
            <input type="hidden" name="user_id" value="42">
            <input type="text" name="comment">
            <input type="submit" value="Post">
        </form>
        </body></html>"""
        doc = self.parser.parse(html, "https://example.com")
        form = doc.blocks[0]
        assert isinstance(form, Form)
        assert form.hidden_fields == {"token": "abc123", "user_id": "42"}
        assert len(form.fields) == 1
        assert form.fields[0].name == "comment"

    def test_parse_select_field(self) -> None:
        html = """<html><body>
        <form action="/go">
            <select name="color">
                <option value="red">Red</option>
                <option value="blue">Blue</option>
                <option value="green">Green</option>
            </select>
            <input type="submit" value="Pick">
        </form>
        </body></html>"""
        doc = self.parser.parse(html, "https://example.com")
        form = doc.blocks[0]
        assert isinstance(form, Form)
        assert len(form.fields) == 1
        field = form.fields[0]
        assert field.name == "color"
        assert field.field_type == "select"
        assert field.options == ["red", "blue", "green"]

    def test_parse_checkbox(self) -> None:
        html = """<html><body>
        <form action="/save">
            <input type="checkbox" name="agree" value="yes">
            <input type="submit" value="Save">
        </form>
        </body></html>"""
        doc = self.parser.parse(html, "https://example.com")
        form = doc.blocks[0]
        assert isinstance(form, Form)
        field = form.fields[0]
        assert field.name == "agree"
        assert field.field_type == "checkbox"
        assert field.value == "yes"
        assert field.checked is False

    def test_parse_checkbox_checked(self) -> None:
        html = """<html><body>
        <form action="/save">
            <input type="checkbox" name="agree" value="yes" checked>
            <input type="submit" value="Save">
        </form>
        </body></html>"""
        doc = self.parser.parse(html, "https://example.com")
        form = doc.blocks[0]
        field = form.fields[0]
        assert field.checked is True

    def test_parse_radio_buttons(self) -> None:
        html = """<html><body>
        <form action="/vote">
            <input type="radio" name="choice" value="a">
            <input type="radio" name="choice" value="b" checked>
            <input type="radio" name="choice" value="c">
            <input type="submit" value="Vote">
        </form>
        </body></html>"""
        doc = self.parser.parse(html, "https://example.com")
        form = doc.blocks[0]
        assert isinstance(form, Form)
        assert len(form.fields) == 3
        assert form.fields[0].field_type == "radio"
        assert form.fields[0].checked is False
        assert form.fields[1].field_type == "radio"
        assert form.fields[1].checked is True
        assert form.fields[2].field_type == "radio"
        assert form.fields[2].checked is False

    def test_parse_textarea(self) -> None:
        html = """<html><body>
        <form action="/comment">
            <textarea name="body" placeholder="Write something..."></textarea>
            <input type="submit" value="Comment">
        </form>
        </body></html>"""
        doc = self.parser.parse(html, "https://example.com")
        form = doc.blocks[0]
        assert isinstance(form, Form)
        assert len(form.fields) == 1
        field = form.fields[0]
        assert field.name == "body"
        assert field.field_type == "textarea"
        assert field.placeholder == "Write something..."

    def test_parse_button_as_submit(self) -> None:
        html = """<html><body>
        <form action="/go">
            <input type="text" name="q">
            <button type="submit">Search Now</button>
        </form>
        </body></html>"""
        doc = self.parser.parse(html, "https://example.com")
        form = doc.blocks[0]
        assert isinstance(form, Form)
        assert form.submit_text == "Search Now"

    def test_form_id_assigned(self) -> None:
        html = """<html><body>
        <form action="/a"><input type="text" name="x"><input type="submit"></form>
        <form action="/b"><input type="text" name="y"><input type="submit"></form>
        </body></html>"""
        doc = self.parser.parse(html, "https://example.com")
        assert len(doc.blocks) == 2
        assert doc.blocks[0].form_id != doc.blocks[1].form_id
        assert doc.blocks[0].form_id == 1
        assert doc.blocks[1].form_id == 2

    def test_form_relative_action_url(self) -> None:
        html = """<html><body>
        <form action="/submit">
            <input type="text" name="q">
            <input type="submit">
        </form>
        </body></html>"""
        doc = self.parser.parse(html, "https://example.com/page")
        form = doc.blocks[0]
        assert form.action == "https://example.com/submit"

    def test_form_default_method_is_get(self) -> None:
        html = """<html><body>
        <form action="/search">
            <input type="text" name="q">
            <input type="submit">
        </form>
        </body></html>"""
        doc = self.parser.parse(html, "https://example.com")
        form = doc.blocks[0]
        assert form.method == "GET"

    def test_form_post_method(self) -> None:
        html = """<html><body>
        <form action="/submit" method="post">
            <input type="text" name="q">
            <input type="submit">
        </form>
        </body></html>"""
        doc = self.parser.parse(html, "https://example.com")
        form = doc.blocks[0]
        assert form.method == "POST"

    def test_multiple_input_types(self) -> None:
        html = """<html><body>
        <form action="/go">
            <input type="text" name="name" value="Alice">
            <input type="email" name="email" placeholder="Email">
            <input type="password" name="pass" placeholder="Password">
            <input type="number" name="age" value="25">
            <input type="submit" value="Register">
        </form>
        </body></html>"""
        doc = self.parser.parse(html, "https://example.com")
        form = doc.blocks[0]
        assert isinstance(form, Form)
        assert len(form.fields) == 4
        types = [f.field_type for f in form.fields]
        assert "text" in types
        assert "email" in types
        assert "password" in types
        assert "number" in types

    def test_search_input_type(self) -> None:
        html = """<html><body>
        <form action="/search">
            <input type="search" name="q" placeholder="Search...">
            <input type="submit">
        </form>
        </body></html>"""
        doc = self.parser.parse(html, "https://example.com")
        form = doc.blocks[0]
        assert form.fields[0].field_type == "search"
        assert form.fields[0].placeholder == "Search..."

    def test_empty_form_returns_empty_form(self) -> None:
        html = "<html><body><form></form></body></html>"
        doc = self.parser.parse(html, "https://example.com")
        assert len(doc.blocks) == 1
        form = doc.blocks[0]
        assert isinstance(form, Form)
        assert len(form.fields) == 0
        assert form.hidden_fields == {}
