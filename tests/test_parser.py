from tweb.parser.html import HTMLParser
from tweb.parser.elements import Heading, Paragraph, Link, Image, List, CodeBlock, Table


class TestHTMLParser:
    def setup_method(self) -> None:
        self.parser = HTMLParser()

    def test_parse_title(self) -> None:
        html = "<html><head><title>Test Page</title></head><body></body></html>"
        doc = self.parser.parse(html, "https://example.com")
        assert doc.title == "Test Page"

    def test_parse_h1(self) -> None:
        html = "<html><body><h1>Hello World</h1></body></html>"
        doc = self.parser.parse(html, "https://example.com")
        assert len(doc.blocks) == 1
        assert isinstance(doc.blocks[0], Heading)
        assert doc.blocks[0].level == 1
        assert doc.blocks[0].text == "Hello World"

    def test_parse_paragraph(self) -> None:
        html = "<html><body><p>This is a paragraph.</p></body></html>"
        doc = self.parser.parse(html, "https://example.com")
        assert len(doc.blocks) == 1
        assert isinstance(doc.blocks[0], Paragraph)
        assert doc.blocks[0].text == "This is a paragraph."

    def test_parse_link(self) -> None:
        html = '<html><body><a href="/about">About</a></body></html>'
        doc = self.parser.parse(html, "https://example.com")
        assert len(doc.blocks) == 1
        assert isinstance(doc.blocks[0], Link)
        assert doc.blocks[0].url == "https://example.com/about"
        assert doc.blocks[0].text == "About"
        assert len(doc.links) == 1

    def test_parse_image(self) -> None:
        html = '<html><body><img src="/logo.png" alt="Logo"></body></html>'
        doc = self.parser.parse(html, "https://example.com")
        assert len(doc.blocks) == 1
        assert isinstance(doc.blocks[0], Image)
        assert doc.blocks[0].alt == "Logo"

    def test_parse_unordered_list(self) -> None:
        html = "<html><body><ul><li>Item 1</li><li>Item 2</li></ul></body></html>"
        doc = self.parser.parse(html, "https://example.com")
        assert len(doc.blocks) == 1
        assert isinstance(doc.blocks[0], List)
        assert doc.blocks[0].ordered is False
        assert len(doc.blocks[0].items) == 2

    def test_parse_ordered_list(self) -> None:
        html = "<html><body><ol><li>First</li><li>Second</li></ol></body></html>"
        doc = self.parser.parse(html, "https://example.com")
        assert isinstance(doc.blocks[0], List)
        assert doc.blocks[0].ordered is True

    def test_parse_code_block(self) -> None:
        html = "<html><body><pre><code>print('hello')</code></pre></body></html>"
        doc = self.parser.parse(html, "https://example.com")
        assert len(doc.blocks) == 1
        assert isinstance(doc.blocks[0], CodeBlock)
        assert doc.blocks[0].code == "print('hello')"

    def test_parse_table(self) -> None:
        html = """<html><body>
        <table>
            <tr><th>Name</th><th>Age</th></tr>
            <tr><td>Alice</td><td>30</td></tr>
        </table>
        </body></html>"""
        doc = self.parser.parse(html, "https://example.com")
        assert len(doc.blocks) == 1
        assert isinstance(doc.blocks[0], Table)
        assert len(doc.blocks[0].rows) == 2
        assert doc.blocks[0].rows[0].cells[0].header is True

    def test_relative_url_resolution(self) -> None:
        html = '<html><body><a href="/page">Link</a></body></html>'
        doc = self.parser.parse(html, "https://example.com/path/page")
        assert doc.blocks[0].url == "https://example.com/page"

    def test_absolute_url_preserved(self) -> None:
        html = '<html><body><a href="https://other.com">Link</a></body></html>'
        doc = self.parser.parse(html, "https://example.com")
        assert doc.blocks[0].url == "https://other.com"

    def test_skips_script_and_style(self) -> None:
        html = """<html><body>
        <script>alert('hi')</script>
        <p>Content</p>
        <style>.x{color:red}</style>
        </body></html>"""
        doc = self.parser.parse(html, "https://example.com")
        assert len(doc.blocks) == 1
        assert isinstance(doc.blocks[0], Paragraph)

    def test_heading_levels(self) -> None:
        html = "<html><body><h1>H1</h1><h2>H2</h2><h3>H3</h3></body></html>"
        doc = self.parser.parse(html, "https://example.com")
        assert len(doc.blocks) == 3
        assert doc.blocks[0].level == 1
        assert doc.blocks[1].level == 2
        assert doc.blocks[2].level == 3
