import os

import yaml
from jinja2 import Template as Jinja2Template


class Template:
    def __init__(self, filename: str):
        """YAML Jinja2 template for request payloads.

        Loads a local YAML and converts it into a Jinja2 template. That makes it
        available for further processing via Jinja2 templating.

        Args:
            filename (str): YAML file name to load.
        """
        base = os.path.dirname(os.path.abspath(__file__))
        with open(f"{base}/{filename}", "r") as template:
            content = template.read()
        self.template = Jinja2Template(content)

    def render(self, **kwargs) -> dict:
        """Render the template.

        Pass variables to Jinja rendering function.

        Returns:
            dict: Rendered YAML document as a Python dict
        """
        render = self.template.render(**kwargs)
        return yaml.safe_load(render)
