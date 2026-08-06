class Node:
    def __init__(self, node_type, value=None):
        self.type = node_type
        self.value = value
        self.children = []

    def add(self, child):
        self.children.append(child)


def parse(tokens):

    program = Node("Program")

    i = 0

    while i < len(tokens):

        token = tokens[i]

        # Skip newlines
        if token["type"] == "NEWLINE":
            i += 1
            continue

        # Looking for:
        # ( keyword = value )

        if (
            i + 4 < len(tokens)
            and tokens[i]["value"] == "("
            and tokens[i + 1]["type"] == "WORD"
            and tokens[i + 2]["value"] == "="
            and tokens[i + 3]["type"] == "WORD"
            and tokens[i + 4]["value"] == ")"
        ):

            keyword = tokens[i + 1]["value"]
            value = tokens[i + 3]["value"]

            node = Node(keyword, value)

            program.add(node)

            i += 5
            continue

        i += 1

    return program
