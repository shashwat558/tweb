from tweb.parser.css import (
    CSSStyle,
    css_style_to_rich,
    get_element_default_color,
    get_element_default_style,
    merge_styles,
    parse_inline_style,
)


class TestParseInlineStyle:
    def test_empty_string(self) -> None:
        css = parse_inline_style("")
        assert css.is_empty()

    def test_color(self) -> None:
        css = parse_inline_style("color: red")
        assert css.color == "#ff0000"

    def test_background_color(self) -> None:
        css = parse_inline_style("background-color: #00ff00")
        assert css.bg_color == "#00ff00"

    def test_font_weight_bold(self) -> None:
        css = parse_inline_style("font-weight: bold")
        assert css.font_weight == "bold"

    def test_font_style_italic(self) -> None:
        css = parse_inline_style("font-style: italic")
        assert css.font_style == "italic"

    def test_text_decoration_underline(self) -> None:
        css = parse_inline_style("text-decoration: underline")
        assert css.text_decoration == "underline"

    def test_text_decoration_line_through(self) -> None:
        css = parse_inline_style("text-decoration: line-through")
        assert css.text_decoration == "line-through"

    def test_opacity(self) -> None:
        css = parse_inline_style("opacity: 0.5")
        assert css.opacity == 0.5

    def test_multiple_declarations(self) -> None:
        css = parse_inline_style("color: blue; font-weight: bold; font-style: italic")
        assert css.color == "#0000ff"
        assert css.font_weight == "bold"
        assert css.font_style == "italic"

    def test_hex_3(self) -> None:
        css = parse_inline_style("color: #f00")
        assert css.color == "#ff0000"

    def test_hex_6(self) -> None:
        css = parse_inline_style("color: #00ff00")
        assert css.color == "#00ff00"

    def test_rgb(self) -> None:
        css = parse_inline_style("color: rgb(255, 128, 0)")
        assert css.color == "#ff8000"

    def test_rgba(self) -> None:
        css = parse_inline_style("color: rgba(128, 0, 255, 0.5)")
        assert css.color == "#8000ff"

    def test_hsl(self) -> None:
        css = parse_inline_style("color: hsl(120, 100%, 50%)")
        assert css.color == "#00ff00"

    def test_named_color(self) -> None:
        css = parse_inline_style("color: coral")
        assert css.color == "#ff7f50"

    def test_transparent_returns_none(self) -> None:
        css = parse_inline_style("color: transparent")
        assert css.color is None

    def test_inherit_returns_none(self) -> None:
        css = parse_inline_style("color: inherit")
        assert css.color is None


class TestCSSStyleToRich:
    def test_empty_style(self) -> None:
        css = CSSStyle()
        assert css_style_to_rich(css) == ""

    def test_color_only(self) -> None:
        css = CSSStyle(color="#ff0000")
        assert css_style_to_rich(css) == "#ff0000"

    def test_bg_color(self) -> None:
        css = CSSStyle(bg_color="#0000ff")
        assert css_style_to_rich(css) == "on #0000ff"

    def test_bold(self) -> None:
        css = CSSStyle(font_weight="bold")
        assert css_style_to_rich(css) == "bold"

    def test_italic(self) -> None:
        css = CSSStyle(font_style="italic")
        assert css_style_to_rich(css) == "italic"

    def test_underline(self) -> None:
        css = CSSStyle(text_decoration="underline")
        assert css_style_to_rich(css) == "underline"

    def test_strike(self) -> None:
        css = CSSStyle(text_decoration="line-through")
        assert css_style_to_rich(css) == "strike"

    def test_dim_opacity(self) -> None:
        css = CSSStyle(opacity=0.3)
        assert css_style_to_rich(css) == "dim"

    def test_full_style(self) -> None:
        css = CSSStyle(color="#ff0000", font_weight="bold", font_style="italic")
        result = css_style_to_rich(css)
        assert "#ff0000" in result
        assert "bold" in result
        assert "italic" in result


class TestMergeStyles:
    def test_merge_two(self) -> None:
        assert merge_styles("bold", "italic") == "bold italic"

    def test_merge_empty(self) -> None:
        assert merge_styles("", "") == ""

    def test_merge_with_empty(self) -> None:
        assert merge_styles("bold", "", "italic") == "bold italic"


class TestElementDefaults:
    def test_h1_default_style(self) -> None:
        assert "bold" in get_element_default_style("h1")

    def test_a_default_color(self) -> None:
        color = get_element_default_color("a")
        assert color is not None

    def test_unknown_element(self) -> None:
        assert get_element_default_style("xyz") == ""
        assert get_element_default_color("xyz") is None
