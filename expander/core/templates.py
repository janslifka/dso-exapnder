import pkgutil

from jinja2 import Template

TEMPLATES = {
    'scss': 'dso.scss.jinja2'
}


def load_template(key):
    template_data = pkgutil.get_data(__name__, f'../templates/{TEMPLATES[key]}').decode()
    return Template(template_data)
