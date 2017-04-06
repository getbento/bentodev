from flask import Flask
from flask import render_template
from flask import request
from os import path
# import click
import os

home_dir = path.expanduser('~')
bentodev_dir = home_dir + '/bentodev/'

static_dir = bentodev_dir + 'sites/{}/assets/'
template_dir = bentodev_dir + 'sites/{}/templates/'


app = Flask(__name__)


def create_app(repo):
    app = Flask(__name__)
    repo = str(os.environ['REPO'])
    app.template_folder = template_dir.format(repo)
    app.static_folder = static_dir.format(repo)
    app.debug = True
    app.config['DEBUG'] = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    return app


app = create_app(repo='test')


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def path_router(path):
    print(request)
    print(app.template_folder)
    context = {}
    context['path'] = path
    template = 'base.html'
    return render_template(template, path=path)
