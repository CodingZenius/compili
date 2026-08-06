def generate(program):

    output = []

    current_element = None
    current_event = None

    for node in program.children:

        match node.type:

            case "button_element":
                current_element = node.value

            case "event_listener":
                current_event = node.value

            case "action":

                if current_element and current_event:

                    output.append(
f"""document.getElementById("{current_element}").addEventListener("{current_event}", () => {{
    {node.value}();
}});"""
                    )

            case "navigate_to_diff_page":

                output.append(
f'window.location.href = "{node.value}";'
                )

            case "add_css_class":

                if current_element:
                    output.append(
f'document.getElementById("{current_element}").classList.add("{node.value}");'
                    )

            case "remove_css_class":

                if current_element:
                    output.append(
f'document.getElementById("{current_element}").classList.remove("{node.value}");'
                    )

            case _:

                output.append(
f'// Unknown command: {node.type}'
                )

    return "\n\n".join(output)
