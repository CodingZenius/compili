import re


class Lexer:

    def __init__(self, source):

        self.source = source

    def tokenize(self):

        tokens = []

        pattern = r"\((.*?)=(.*?)\)"

        matches = re.findall(pattern, self.source)

        for key, value in matches:

            tokens.append({
                "key": key.strip(),
                "value": value.strip()
            })

        return tokens
