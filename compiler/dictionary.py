"""
dictionary.py
=============

VTC is a *data-driven* language. Instead of hardcoding hundreds of
if/elif branches inside the Generator, every keyword the language
understands is registered here as a small declarative entry.

This is the file that is expected to GROW over time as VTC gains new
intent keywords. The compiler core (lexer.py, parser.py, ast_nodes.py,
generator.py) should rarely need to change just to add a new keyword —
only this dictionary should.

Entry shape
-----------
Each keyword maps to a dict describing:

    category:    which AST node family this keyword belongs to
                 (e.g. "button", "api", "card", "style", "dom", "misc")
    js_binding:  the underlying JS API/pattern this keyword compiles
                 toward (documentation + used by the generator)
    role:        how the keyword is used inside a block:
                     "target"   -> identifies the element/subject
                     "event"    -> identifies a DOM event to listen for
                     "action"   -> identifies a named action/handler
                     "modifier" -> a smart-object / CSS-ish modifier
                     "config"   -> a standalone config statement
    requires:    list of roles that MUST appear earlier in the same
                 block before this keyword is valid (drives the
                 "(x) requires (y) before (z)" dependency errors)
    description: human-readable explanation (used in docs/errors)

Adding a new keyword
---------------------
1. Pick (or invent) a category.
2. Add an entry to KEYWORDS below.
3. If it introduces a wholly new AST shape, add a Node class in
   ast_nodes.py and a matching `generate_<category>` method in
   generator.py. Most new keywords do NOT need this -- they can reuse
   an existing category (e.g. any new event name just extends the
   "event" role under the existing button/element categories).
4. Add an example .vtc file under examples/ if it showcases something new.

See context.md for the full philosophy behind this design.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Core keyword table
# ---------------------------------------------------------------------------
KEYWORDS: dict[str, dict] = {

    # --- Elements / targets -------------------------------------------------
    "button_element": {
        "category": "button",
        "role": "target",
        "js_binding": "document.getElementById",
        "requires": [],
        "description": "Selects a button element by id to attach behaviour to.",
    },
    "form_element": {
        "category": "form",
        "role": "target",
        "js_binding": "document.getElementById",
        "requires": [],
        "description": "Selects a form element by id.",
    },
    "card_element": {
        "category": "card",
        "role": "target",
        "js_binding": "document.getElementById",
        "requires": [],
        "description": "Selects a card element by id.",
    },
    "dropdown_element": {
        "category": "dropdown",
        "role": "target",
        "js_binding": "document.getElementById",
        "requires": [],
        "description": "Selects a dropdown element by id.",
    },
    "modal_element": {
        "category": "modal",
        "role": "target",
        "js_binding": "document.getElementById",
        "requires": [],
        "description": "Selects a modal element by id.",
    },
    "nav_element": {
        "category": "navigation",
        "role": "target",
        "js_binding": "document.getElementById",
        "requires": [],
        "description": "Selects a navigation element by id.",
    },
    "input_element": {
        "category": "form",
        "role": "target",
        "js_binding": "document.getElementById",
        "requires": [],
        "description": "Selects an input element by id.",
    },
    "wallet_element": {
        "category": "wallet",
        "role": "target",
        "js_binding": "document.getElementById",
        "requires": [],
        "description": "Selects a virtual-wallet style element by id.",
    },

    # --- Events ---------------------------------------------------------------
    "event_listener": {
        "category": "event",
        "role": "event",
        "js_binding": "addEventListener",
        "requires": ["target"],
        "description": "Declares which DOM event to listen for (click, hover, swipe...).",
    },

    # --- Actions ---------------------------------------------------------------
    "action": {
        "category": "action",
        "role": "action",
        "js_binding": "function-call",
        "requires": ["target", "event"],
        "description": "Names the handler function to run when the event fires.",
    },

    # --- Networking -------------------------------------------------------------
    "request_from_api": {
        "category": "api",
        "role": "config",
        "js_binding": "fetch",
        "requires": [],
        "description": "Performs a fetch() request to the given endpoint.",
    },
    "fetch_page": {
        "category": "api",
        "role": "config",
        "js_binding": "fetch",
        "requires": [],
        "description": "Fetches a partial page/fragment and swaps it into the DOM.",
    },
    "get_from_os.env": {
        "category": "env",
        "role": "config",
        "js_binding": "window.__VTC_ENV__",
        "requires": [],
        "description": "Reads a frontend-exposed environment variable.",
    },

    # --- DOM / style modification -----------------------------------------------
    "add_css_class": {
        "category": "style",
        "role": "config",
        "js_binding": "classList.add",
        "requires": [],
        "description": "Adds a CSS class to the target element.",
    },
    "remove_css_class": {
        "category": "style",
        "role": "config",
        "js_binding": "classList.remove",
        "requires": [],
        "description": "Removes a CSS class from the target element.",
    },
    "toggle_css_class": {
        "category": "style",
        "role": "config",
        "js_binding": "classList.toggle",
        "requires": [],
        "description": "Toggles a CSS class on the target element.",
    },
    "modhtml_element_content": {
        "category": "dom",
        "role": "config",
        "js_binding": "innerHTML",
        "requires": [],
        "description": "Modifies the HTML content of the target element.",
    },
    "modinline_style": {
        "category": "dom",
        "role": "config",
        "js_binding": "style",
        "requires": [],
        "description": "Modifies an inline CSS style property of the target element.",
    },

    # --- History / navigation ------------------------------------------------
    "push_history": {
        "category": "history",
        "role": "config",
        "js_binding": "history.pushState",
        "requires": [],
        "description": "Pushes a new entry onto the browser history stack.",
    },
    "go_back": {
        "category": "history",
        "role": "config",
        "js_binding": "history.back",
        "requires": [],
        "description": "Navigates back one entry in browser history.",
    },

    # --- Data transfer (wallet-style interfaces) -------------------------------
    "transfer_amount": {
        "category": "transfer",
        "role": "config",
        "js_binding": "custom:transfer",
        "requires": [],
        "description": "Declares a transfer-out amount for a wallet-style UI.",
    },
    "receive_amount": {
        "category": "receive",
        "role": "config",
        "js_binding": "custom:receive",
        "requires": [],
        "description": "Declares a receive-in amount for a wallet-style UI.",
    },

    # --- Validation --------------------------------------------------------------
    "validate_input": {
        "category": "validation",
        "role": "config",
        "js_binding": "custom:validate",
        "requires": [],
        "description": "Declares a validation rule for a form input (e.g. email, required).",
    },

    # --- Newsletter / signup shortcut -----------------------------------------
    "newsletter_signup": {
        "category": "newsletter",
        "role": "config",
        "js_binding": "custom:newsletter",
        "requires": [],
        "description": "Declares a newsletter signup endpoint shortcut.",
    },

    # --- Smart Objects (future CSS/animation layer) -----------------------------
    "card_center_screen": {
        "category": "smart_object",
        "role": "modifier",
        "js_binding": "css:position-center",
        "requires": [],
        "description": "Positions a card in the center of the screen.",
    },
    "card_middle": {
        "category": "smart_object",
        "role": "modifier",
        "js_binding": "css:position-middle",
        "requires": [],
        "description": "Positions a card vertically in the middle of its container.",
    },
    "card_bottom": {
        "category": "smart_object",
        "role": "modifier",
        "js_binding": "css:position-bottom",
        "requires": [],
        "description": "Positions a card at the bottom of its container.",
    },
    "card_float": {
        "category": "smart_object",
        "role": "modifier",
        "js_binding": "css:float-animation",
        "requires": [],
        "description": "Applies a floating/hover animation to a card.",
    },
    "card_glide": {
        "category": "smart_object",
        "role": "modifier",
        "js_binding": "css:glide-animation",
        "requires": [],
        "description": "Applies a gliding entrance/transition animation to a card.",
    },
    "card_flip": {
        "category": "smart_object",
        "role": "modifier",
        "js_binding": "css:flip-animation",
        "requires": [],
        "description": "Applies a 3D flip animation to a card.",
    },

    # --- Page transitions / popups -----------------------------------------------
    "page_transition": {
        "category": "transition",
        "role": "config",
        "js_binding": "css:page-transition",
        "requires": [],
        "description": "Declares a transition style used when navigating between pages.",
    },
    "popup_screen": {
        "category": "modal",
        "role": "config",
        "js_binding": "custom:popup",
        "requires": [],
        "description": "Declares a popup/overlay screen.",
    },
}


# ---------------------------------------------------------------------------
# Recognized event names (used by `event_listener=...`)
# ---------------------------------------------------------------------------
EVENTS: dict[str, str] = {
    "click": "click",
    "hover": "mouseenter",
    "swipe": "touchstart",
    "submit": "submit",
    "change": "change",
    "input": "input",
    "focus": "focus",
    "blur": "blur",
}


def all_keywords() -> list[str]:
    """Return every recognized top-level keyword (for typo suggestions)."""
    return list(KEYWORDS.keys())


def all_events() -> list[str]:
    """Return every recognized event name (for typo suggestions)."""
    return list(EVENTS.keys())


def lookup(keyword: str) -> dict | None:
    """Look up a keyword's dictionary entry (case-insensitive)."""
    return KEYWORDS.get(keyword.lower())


def lookup_event(event_name: str) -> str | None:
    """Resolve a VTC event name (e.g. 'hover') to its JS event name (e.g. 'mouseenter')."""
    return EVENTS.get(event_name.lower())
