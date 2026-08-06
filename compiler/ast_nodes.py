"""
ast_nodes.py
============

AST node class definitions for VTC.

Design decision: the parser builds typed Node objects (ButtonNode,
CardNode, ApiNode, ...) rather than passing raw dicts around. This
costs a little boilerplate but pays off in readability, IDE support,
and safer expansion -- new contributors can see exactly what shape
of data a given block produces.

Every node is intentionally a lightweight dataclass. Nodes hold:
  - the raw statements that made them up (`statements`, a list of
    (keyword, value) pairs in source order) so the Generator has full
    access to everything the block declared, even keywords a specific
    node subclass doesn't have a dedicated field for.
  - `line`: the source line the block started on, for error reporting.

New node types
--------------
To add a new node type:
  1. Add a subclass of Node below (usually just needs `category`
     to distinguish it -- most behaviour comes from `statements`).
  2. Register the category -> node class mapping in `NODE_CLASSES`.
  3. Add a matching `generate_<category>` method in generator.py.

Most new *keywords* do NOT require a new Node type -- see
dictionary.py for the common case of extending an existing category.
"""

from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class Statement:
    """A single (keyword=value) or (keyword) statement inside a block."""
    keyword: str
    value: str | None
    line: int


@dataclass
class Node:
    """Base class for all VTC AST nodes. Represents one block of intent."""
    category: str
    statements: list[Statement] = field(default_factory=list)
    line: int = 0

    def get(self, keyword: str) -> str | None:
        """Return the value of the first statement matching `keyword`, if any."""
        for stmt in self.statements:
            if stmt.keyword == keyword:
                return stmt.value
        return None

    def get_all(self, keyword: str) -> list[str | None]:
        """Return all values for statements matching `keyword` (order preserved)."""
        return [s.value for s in self.statements if s.keyword == keyword]

    def has(self, keyword: str) -> bool:
        return any(s.keyword == keyword for s in self.statements)


@dataclass
class ButtonNode(Node):
    category: str = "button"


@dataclass
class FormNode(Node):
    category: str = "form"


@dataclass
class CardNode(Node):
    category: str = "card"


@dataclass
class DropdownNode(Node):
    category: str = "dropdown"


@dataclass
class NavigationNode(Node):
    category: str = "navigation"


@dataclass
class AnimationNode(Node):
    category: str = "smart_object"


@dataclass
class ApiNode(Node):
    category: str = "api"


@dataclass
class ModalNode(Node):
    category: str = "modal"


@dataclass
class HistoryNode(Node):
    category: str = "history"


@dataclass
class TransferNode(Node):
    category: str = "transfer"


@dataclass
class ReceiveNode(Node):
    category: str = "receive"


@dataclass
class WalletNode(Node):
    category: str = "wallet"


@dataclass
class ValidationNode(Node):
    category: str = "validation"


@dataclass
class NewsletterNode(Node):
    category: str = "newsletter"


@dataclass
class GenericNode(Node):
    """
    Fallback node for blocks whose target keyword doesn't map to a
    dedicated Node subclass yet. Keeps the compiler forward-compatible:
    new dictionary entries work immediately, even before a specialised
    Node/generator method exists for them.
    """
    category: str = "generic"


@dataclass
class ImportNode:
    """Represents `import(graphics)` style future-module imports."""
    module: str
    line: int = 0


# Maps a block's detected category to the Node subclass that should
# represent it. See parser.py for how the category is detected.
NODE_CLASSES: dict[str, type] = {
    "button": ButtonNode,
    "form": FormNode,
    "card": CardNode,
    "dropdown": DropdownNode,
    "navigation": NavigationNode,
    "smart_object": AnimationNode,
    "api": ApiNode,
    "modal": ModalNode,
    "history": HistoryNode,
    "transfer": TransferNode,
    "receive": ReceiveNode,
    "wallet": WalletNode,
    "validation": ValidationNode,
    "newsletter": NewsletterNode,
}


def make_node(category: str, statements: list[Statement], line: int) -> Node:
    """Factory: build the correct Node subclass for a given category."""
    cls = NODE_CLASSES.get(category, GenericNode)
    return cls(statements=statements, line=line)
