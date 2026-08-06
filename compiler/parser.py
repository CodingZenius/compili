class Parser:

    def __init__(self, tokens):

        self.tokens = tokens

        self.ast = []

    def parse(self):

        current = {}

        for token in self.tokens:

            key = token["key"]
            value = token["value"]

            # Start of a new intent block
            if key == "button_element":

                if current:
                    self.ast.append(current)

                current = {
                    "type": "button",
                    "element": value,
                    "events": [],
                    "actions": []
                }

            elif key == "event_listener":

                current.setdefault("events", []).append(value)

            elif key == "action":

                current.setdefault("actions", []).append(value)

            elif key == "navigate_to_diff_page":

                self.ast.append({
                    "type": "navigation",
                    "page": value
                })

            elif key == "request_from_api":

                self.ast.append({
                    "type": "fetch",
                    "endpoint": value
                })

            elif key == "get_from_OS.env":

                self.ast.append({
                    "type": "environment",
                    "variable": value
                })

            else:

                self.ast.append({
                    "type": "unknown",
                    "keyword": key,
                    "value": value
                })

        if current:
            self.ast.append(current)

        return self.ast
