from flask import Flask, send_from_directory, request, render_template
from os import path
# import click
import os
import requests
from . import filters
from .environment import StaticFilesExtension, BentoJinja2Environment
from inspect import getmembers, isfunction


home_dir = path.expanduser('~')
bentodev_dir = home_dir + '/bentodev/'

static_dir = bentodev_dir + 'sites/{}/assets/'
template_dir = bentodev_dir + 'sites/{}/templates/'

preview_url = 'getbento.com/'
help_url = '?help'

repo = str(os.environ['REPO'])


def create_app():
    app = Flask(__name__)
    app.template_folder = template_dir.format(repo)
    app.static_folder = static_dir.format(repo)
    app.debug = True

    app.jinja_env.add_extension(StaticFilesExtension)
    app.jinja_env.autoescape = False
    my_filters = {name: function for name, function in getmembers(filters) if isfunction(function)}

    app.jinja_env.filters.update(my_filters)
    app.config.update(
        DEBUG=True,
        TEMPLATES_AUTO_RELOAD=True
    )
    return app


app = create_app()


def handle_request(path):
    headers = {
        'X-Requested-With': 'XMLHttpRequest',
    }
    request_url = 'http://{}.{}{}{}'.format('unionsquarecafe-copy', preview_url, path, help_url)
    print(request_url)
    try:
        r = requests.get(request_url, headers=headers)
        context_data = r.json()
        return context_data
    except Exception as e:
        print(e)


@app.route('/assets/<path:path>')
def static_file(path):
    file = app.static_folder + path
    print(file)
    return app.send_static_file(path)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def path_router(path):
    context_data = handle_request(path)
    template = context_data['current']['template']
    return render_template(template, **context_data)


if __name__ == "__main__":
    app = create_app()
    app.run()
