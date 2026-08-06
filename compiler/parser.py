"""
parser.py
=========

Turns the flat Token stream from lexer.py into a list of AST nodes
(ast_nodes.py), consulting dictionary.py to validate keywords and
enforce intent ordering (e.g. an `action` requires an `event_listener`
which requires a `target`).

Grammar (informal)
-------------------
    program      := block*
    block        := statement+ (separated by blank NEWLINE from next block)
    statement    := IMPORT '(' IDENT ')'
                  | '(' IDENT ['=' value] ')'
    value        := IDENT

A "block" is a run of consecutive statements with no blank line between
them. Each block becomes exactly one AST Node. Blank lines are purely
a readability / grouping device for the VTC author.

Category detection
-------------------
A block's category (button / form / card / api / ...) is decided by
the FIRST statement's keyword, via its dictionary entry's `category`
field. This keeps ordering meaningful: you lead a block with the
"target" statement.
"""

from __future__ import annotations
from .lexer import Token
from .ast_nodes import Statement, Node, ImportNode, make_node
from . import dictionary
from .errors import IntentError, unknown_keyword_error, missing_dependency_error


class Parser:
    """Consumes a token list and produces a list of AST nodes."""

    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0

    # ------------------------------------------------------------------
    def parse(self) -> list[Node | ImportNode]:
        nodes: list[Node | ImportNode] = []
        self._skip_newlines()

        while not self._at_end():
            block_statements: list[Statement] = []
            block_line = self._peek().line

            # An `import(...)` is always its own standalone node.
            if self._peek().kind == "IMPORT":
                nodes.append(self._parse_import())
                self._skip_newlines()
                continue

            # Otherwise, gather a run of statements until a blank line/EOF.
            while not self._at_end() and self._peek().kind != "NEWLINE":
                stmt = self._parse_statement()
                block_statements.append(stmt)

            if block_statements:
                nodes.append(self._build_node(block_statements, block_line))

            self._skip_newlines()

        return nodes

    # ------------------------------------------------------------------
    def _build_node(self, statements: list[Statement], line: int) -> Node:
        """Validate a block's statements and construct the right Node type."""
        first_keyword = statements[0].keyword
        entry = dictionary.lookup(first_keyword)

        if entry is None:
            raise unknown_keyword_error(
                first_keyword, dictionary.all_keywords(), line=statements[0].line
            )

        category = entry["category"]

        # Validate every statement's keyword exists in the dictionary.
        for stmt in statements:
            stmt_entry = dictionary.lookup(stmt.keyword)
            if stmt_entry is None:
                raise unknown_keyword_error(
                    stmt.keyword, dictionary.all_keywords(), line=stmt.line
                )

            # enforce declared dependencies, e.g. action requires target+event.
            # Only roles seen STRICTLY BEFORE this statement satisfy the requirement.
            for required_role in stmt_entry.get("requires", []):
                if not self._role_present_earlier(statements, stmt, required_role):
                    raise missing_dependency_error(
                        this_keyword=stmt.keyword,
                        requires_keyword=self._keyword_for_role(statements, required_role) or required_role,
                        before_keyword=stmt.keyword,
                        line=stmt.line,
                    )

        return make_node(category, statements, line)

    @staticmethod
    def _role_present_earlier(statements: list[Statement], current: Statement, role: str) -> bool:
        for stmt in statements:
            if stmt is current:
                break
            entry = dictionary.lookup(stmt.keyword)
            if entry and entry["role"] == role:
                return True
        return False

    @staticmethod
    def _keyword_for_role(statements: list[Statement], role: str) -> str | None:
        # Prefer a keyword actually present in this block...
        for stmt in statements:
            entry = dictionary.lookup(stmt.keyword)
            if entry and entry["role"] == role:
                return stmt.keyword
        # ...otherwise fall back to any dictionary keyword with that role,
        # so the error message still names something concrete and helpful
        # (e.g. "requires (event_listener)" instead of "requires (event)").
        for kw, entry in dictionary.KEYWORDS.items():
            if entry["role"] == role:
                return kw
        return None

    # ------------------------------------------------------------------
    def _parse_import(self) -> ImportNode:
        line = self._peek().line
        self._expect("IMPORT")
        self._expect("LPAREN")
        module_token = self._expect("IDENT")
        self._expect("RPAREN")
        return ImportNode(module=module_token.value, line=line)

    def _parse_statement(self) -> Statement:
        line = self._peek().line
        self._expect("LPAREN")
        keyword_token = self._expect("IDENT")
        keyword = keyword_token.value.lower()

        value = None
        if self._peek().kind == "EQUALS":
            self._advance()
            value_token = self._expect("IDENT")
            value = value_token.value

        self._expect("RPAREN")
        return Statement(keyword=keyword, value=value, line=line)

    # ------------------------------------------------------------------
    def _skip_newlines(self) -> None:
        while not self._at_end() and self._peek().kind == "NEWLINE":
            self._advance()

    def _peek(self) -> Token:
        return self.tokens[self.pos]

    def _advance(self) -> Token:
        tok = self.tokens[self.pos]
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return tok

    def _at_end(self) -> bool:
        return self._peek().kind == "EOF"

    def _expect(self, kind: str) -> Token:
        tok = self._peek()
        if tok.kind != kind:
            raise IntentError(
                message=f"Expected {kind} but found '{tok.value or tok.kind}'",
                line=tok.line,
            )
        return self._advance()
