import re

# Characters that have meaning in the language
SPECIAL = "(){}[]=<>/"

def tokenize(source: str):

    tokens = []

    line = 1
    column = 1

    current = ""

    def push_current():
        nonlocal current

        if current.strip():
            tokens.append({
                "type": "WORD",
                "value": current.strip()
            })

        current = ""

    for char in source:

        if char == "\n":

            push_current()

            tokens.append({
                "type": "NEWLINE",
                "value": "\\n"
            })

            line += 1
            column = 1
            continue

        if char in SPECIAL:

            push_current()

            tokens.append({
                "type": "SYMBOL",
                "value": char
            })

            column += 1
            continue

        if char.isspace():

            push_current()

            column += 1
            continue

        current += char
        column += 1

    push_current()

    return tokens
