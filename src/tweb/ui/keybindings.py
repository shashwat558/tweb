from __future__ import annotations

from textual.binding import Binding

BINDINGS = [
    Binding("ctrl+q", "quit", "Quit", show=True),
    Binding("ctrl+l", "focus_url", "URL", show=True, key_display="Ctrl+L"),
    Binding("ctrl+r", "reload", "Reload", show=True, key_display="Ctrl+R"),
    Binding("ctrl+f", "toggle_find", "Find", show=True, key_display="Ctrl+F"),
    Binding("alt+left", "go_back", "Back", show=True, key_display="Alt+←"),
    Binding("alt+right", "go_forward", "Forward", show=True, key_display="Alt+→"),
    Binding("escape", "focus_content", "Content", show=False),
    Binding("j", "select_next_link", "Next Link", show=False),
    Binding("k", "select_prev_link", "Prev Link", show=False),
    Binding("enter", "open_selected_link", "Open Link", show=False),
    Binding("up", "scroll_up", "Up", show=False),
    Binding("down", "scroll_down", "Down", show=False),
    Binding("pageup", "page_up", "Page Up", show=False),
    Binding("pagedown", "page_down", "Page Down", show=False),
    Binding("home", "scroll_home", "Home", show=False),
    Binding("end", "scroll_end", "End", show=False),
]
