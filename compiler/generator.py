class Generator:

    def __init__(self, ast):

        self.ast = ast

    def generate(self):

        output = []

        for node in self.ast:

            node_type = node.get("type")

            # ---------------------------------
            # Button Intent
            # ---------------------------------

            if node_type == "button":

                element = node["element"]

                events = node.get("events", [])

                actions = node.get("actions", [])

                if not events:

                    events = ["click"]

                for event in events:

                    output.append(
                        f'document.getElementById("{element}")'
                        f'.addEventListener("{event}", () => {{'
                    )

                    for action in actions:

                        output.append(
                            f'    {action}();'
                        )

                    output.append("});")
                    output.append("")

            # ---------------------------------
            # Navigation
            # ---------------------------------

            elif node_type == "navigation":

                page = node["page"]

                output.append(
                    f'window.location.href = "{page}";'
                )

                output.append("")

            # ---------------------------------
            # API Request
            # ---------------------------------

            elif node_type == "fetch":

                endpoint = node["endpoint"]

                output.append(
                    f'fetch("{endpoint}")'
                )

                output.append("")

            # ---------------------------------
            # Environment Variable
            # ---------------------------------

            elif node_type == "environment":

                variable = node["variable"]

                output.append(
                    f'process.env["{variable}"]'
                )

                output.append("")

            # ---------------------------------
            # Unknown Intent
            # ---------------------------------

            elif node_type == "unknown":

                output.append(
                    f'// Unknown keyword: {node["keyword"]}'
                )

                output.append("")

        return "\n".join(output)
