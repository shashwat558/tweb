from tweb.cli import normalize_url


class TestNormalizeUrl:
    def test_adds_https_scheme(self) -> None:
        assert normalize_url("example.com") == "https://example.com"

    def test_preserves_existing_scheme(self) -> None:
        assert normalize_url("https://example.com") == "https://example.com"
        assert normalize_url("http://example.com") == "http://example.com"

    def test_strips_whitespace(self) -> None:
        assert normalize_url("  example.com  ") == "https://example.com"

    def test_empty_string(self) -> None:
        assert normalize_url("") == ""

    def test_complex_url(self) -> None:
        url = "https://example.com/path?q=1#fragment"
        assert normalize_url(url) == url

    def test_relative_path(self) -> None:
        assert normalize_url("/about") == "https:///about"
