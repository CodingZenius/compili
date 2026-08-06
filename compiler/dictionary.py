"""
Intent Language Lexicon

Every keyword in the language lives here.

The compiler never needs to know JavaScript directly.

It simply asks this dictionary
how each keyword should translate.
"""

LANGUAGE = {

    "button_element": {
        "type": "element",
        "js": "document.getElementById"
    },

    "event_listener": {
        "type": "event",
        "js": "addEventListener"
    },

    "add_event_listener/click": {
        "type": "event",
        "value": "click"
    },

    "add_event_listener/hover": {
        "type": "event",
        "value": "mouseover"
    },

    "navigate_to_diff_page": {
        "type": "navigation",
        "js": "window.location.href"
    },

    "request_from_api": {
        "type": "api",
        "js": "fetch"
    },

    "make_api_call": {
        "type": "api",
        "js": "fetch"
    },

    "get_from_OS.env": {
        "type": "environment",
        "js": "process.env"
    },

    "add_css_class": {
        "type": "css",
        "js": "classList.add"
    },

    "remove_css_class": {
        "type": "css",
        "js": "classList.remove"
    },

    "MODHTML_element_content": {
        "type": "dom",
        "js": "innerHTML"
    },

    "MODinline_style": {
        "type": "style",
        "js": "style"
    }

}
