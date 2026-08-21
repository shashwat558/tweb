from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class CSSStyle:
    color: Optional[str] = None
    bg_color: Optional[str] = None
    font_weight: Optional[str] = None
    font_style: Optional[str] = None
    text_decoration: Optional[str] = None
    text_align: Optional[str] = None
    font_size: Optional[str] = None
    opacity: Optional[float] = None

    def is_empty(self) -> bool:
        return all(
            v is None
            for v in [
                self.color,
                self.bg_color,
                self.font_weight,
                self.font_style,
                self.text_decoration,
                self.text_align,
                self.font_size,
                self.opacity,
            ]
        )


CSS_COLOR_NAMES = {
    "black": "#000000",
    "white": "#ffffff",
    "red": "#ff0000",
    "green": "#008000",
    "blue": "#0000ff",
    "yellow": "#ffff00",
    "cyan": "#00ffff",
    "magenta": "#ff00ff",
    "gray": "#808080",
    "grey": "#808080",
    "silver": "#c0c0c0",
    "maroon": "#800000",
    "olive": "#808000",
    "lime": "#00ff00",
    "aqua": "#00ffff",
    "teal": "#008080",
    "navy": "#000080",
    "fuchsia": "#ff00ff",
    "purple": "#800080",
    "orange": "#ffa500",
    "pink": "#ffc0cb",
    "brown": "#a52a2a",
    "coral": "#ff7f50",
    "crimson": "#dc143c",
    "darkblue": "#00008b",
    "darkgreen": "#006400",
    "darkred": "#8b0000",
    "gold": "#ffd700",
    "indigo": "#4b0082",
    "ivory": "#fffff0",
    "khaki": "#f0e68c",
    "lavender": "#e6e6fa",
    "lightblue": "#add8e6",
    "lightgreen": "#90ee90",
    "lightgray": "#d3d3d3",
    "lightgrey": "#d3d3d3",
    "lightyellow": "#ffffe0",
    "linen": "#faf0e6",
    "moccasin": "#ffe4b5",
    "plum": "#dda0dd",
    "salmon": "#fa8072",
    "seagreen": "#2e8b57",
    "sienna": "#a0522d",
    "skyblue": "#87ceeb",
    "slateblue": "#6a5acd",
    "slategray": "#708090",
    "slategrey": "#708090",
    "snow": "#fffafa",
    "tan": "#d2b48c",
    "thistle": "#d8bfd8",
    "tomato": "#ff6347",
    "turquoise": "#40e0d0",
    "violet": "#ee82ee",
    "wheat": "#f5deb3",
    "whitesmoke": "#f5f5f5",
    "darkgray": "#a9a9a9",
    "darkgrey": "#a9a9a9",
    "dimgray": "#696969",
    "dimgrey": "#696969",
}


def parse_inline_style(style_str: str) -> CSSStyle:
    if not style_str:
        return CSSStyle()

    css = CSSStyle()
    declarations = _parse_declarations(style_str)

    for prop, value in declarations:
        prop = prop.strip().lower()
        value = value.strip()

        if prop == "color":
            css.color = _resolve_color(value)
        elif prop == "background-color" or prop == "background":
            resolved = _resolve_color(value)
            if resolved:
                css.bg_color = resolved
        elif prop == "font-weight":
            css.font_weight = value.lower()
        elif prop == "font-style":
            css.font_style = value.lower()
        elif prop in ("text-decoration", "text-decoration-line"):
            css.text_decoration = value.lower()
        elif prop == "text-align":
            css.text_align = value.lower()
        elif prop == "font-size":
            css.font_size = value.lower()
        elif prop == "opacity":
            try:
                css.opacity = float(value)
            except ValueError:
                pass

    return css


def _parse_declarations(style_str: str) -> list[tuple[str, str]]:
    result: list[tuple[str, str]] = []
    for decl in style_str.split(";"):
        decl = decl.strip()
        if ":" not in decl:
            continue
        prop, _, value = decl.partition(":")
        if prop.strip() and value.strip():
            result.append((prop.strip(), value.strip()))
    return result


def _resolve_color(value: str) -> Optional[str]:
    value = value.strip().lower()

    if value in ("transparent", "inherit", "initial", "unset", "currentColor", "currentcolor"):
        return None

    m = re.match(r"^#([0-9a-f]{3,8})$", value)
    if m:
        hex_str = m.group(1)
        if len(hex_str) == 3:
            return f"#{hex_str[0]*2}{hex_str[1]*2}{hex_str[2]*2}"
        elif len(hex_str) >= 6:
            return f"#{hex_str[:6]}"
        return None

    m = re.match(r"^rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)$", value)
    if m:
        r, g, b = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return f"#{r:02x}{g:02x}{b:02x}"

    m = re.match(r"^rgba\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*[\d.]+\s*\)$", value)
    if m:
        r, g, b = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return f"#{r:02x}{g:02x}{b:02x}"

    m = re.match(r"^hsl\(\s*(\d+)\s*,\s*(\d+)%\s*,\s*(\d+)%\s*\)$", value)
    if m:
        r, g, b = _hsl_to_rgb(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        return f"#{r:02x}{g:02x}{b:02x}"

    if value in CSS_COLOR_NAMES:
        return CSS_COLOR_NAMES[value]

    return None


def _hsl_to_rgb(h: int, s: int, l: int) -> tuple[int, int, int]:
    s /= 100
    l /= 100

    c = (1 - abs(2 * l - 1)) * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = l - c / 2

    if h < 60:
        r_, g_, b_ = c, x, 0
    elif h < 120:
        r_, g_, b_ = x, c, 0
    elif h < 180:
        r_, g_, b_ = 0, c, x
    elif h < 240:
        r_, g_, b_ = 0, x, c
    elif h < 300:
        r_, g_, b_ = x, 0, c
    else:
        r_, g_, b_ = c, 0, x

    return int((r_ + m) * 255), int((g_ + m) * 255), int((b_ + m) * 255)


def css_style_to_rich(css: CSSStyle) -> str:
    parts: list[str] = []

    if css.color:
        parts.append(css.color)

    if css.bg_color:
        parts.append(f"on {css.bg_color}")

    if css.font_weight in ("bold", "bolder", "600", "700", "800", "900"):
        parts.append("bold")

    if css.font_style == "italic":
        parts.append("italic")

    if css.text_decoration and "underline" in css.text_decoration:
        parts.append("underline")

    if css.text_decoration and "line-through" in css.text_decoration:
        parts.append("strike")

    if css.opacity is not None and css.opacity < 0.5:
        parts.append("dim")

    return " ".join(parts)


def merge_styles(*styles: str) -> str:
    return " ".join(s for s in styles if s)


def get_element_default_style(tag: str) -> str:
    defaults = {
        "h1": "bold white",
        "h2": "bold bright_white",
        "h3": "bold bright_white",
        "h4": "bold",
        "h5": "bold",
        "h6": "bold",
        "strong": "bold",
        "b": "bold",
        "em": "italic",
        "i": "italic",
        "u": "underline",
        "a": "underline cyan",
        "code": "on grey11",
        "pre": "on grey11",
        "mark": "black on yellow",
        "small": "dim",
        "del": "strike",
        "s": "strike",
        "ins": "underline",
        "sub": "dim",
        "sup": "dim",
    }
    return defaults.get(tag, "")


def get_element_default_color(tag: str) -> Optional[str]:
    color_map = {
        "a": "#0066cc",
        "h1": "#ffffff",
        "h2": "#f0f0f0",
        "h3": "#f0f0f0",
        "h4": "#e0e0e0",
        "h5": "#e0e0e0",
        "h6": "#e0e0e0",
        "blockquote": "#aaaaaa",
        "code": "#d4d4d4",
        "pre": "#d4d4d4",
        "mark": "#000000",
        "small": "#999999",
    }
    return color_map.get(tag)
