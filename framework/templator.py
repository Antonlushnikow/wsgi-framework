import os
from jinja2 import Template
from settings import TEMPLATES


def render(template_name, **kwargs):
    path = os.path.join(TEMPLATES, template_name)
    with open(path, encoding='utf-8') as f:
        template = Template(f.read())
    return template.render(**kwargs)
