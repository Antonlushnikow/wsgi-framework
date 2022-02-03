from jinja2 import FileSystemLoader
from jinja2.environment import Environment


TEMPLATES = 'templates'


def render(template_name, **kwargs):
    env = Environment()
    env.loader = FileSystemLoader(TEMPLATES)
    template = env.get_template(template_name)
    return template.render(**kwargs)


