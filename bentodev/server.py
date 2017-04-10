from flask import Flask, render_template
from os import path, environ
from . import filters
from .environment import StaticFilesExtension
from inspect import getmembers, isfunction
from jinja2.ext import do
from .factory import HelpDataRequest


HOME_DIR = path.expanduser('~')
BENTODEV_DIR = HOME_DIR + '/bentodev/'

STATIC_DIR = BENTODEV_DIR + 'sites/{}/assets/'
TEMPLATE_DIR = BENTODEV_DIR + 'sites/{}/templates/'

REPO = str(environ['REPO'])
ACCOUNT = str(environ['ACCOUNT'])


def create_app():
    app = Flask(__name__)
    app.template_folder = TEMPLATE_DIR.format(REPO)
    app.static_folder = STATIC_DIR.format(REPO)
    app.debug = True

    app.jinja_env.add_extension(StaticFilesExtension)
    app.jinja_env.add_extension(do)

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
    kwargs = {
        'account': ACCOUNT,
        'path': path,
        'help': True,
    }
    r = HelpDataRequest(**kwargs)
    print('REQUEST: ' + r.url)
    try:
        r.get()
        return r.json()
    except Exception as e:
        print(e)
        raise SystemExit


@app.route('/assets/<path:path>')
def static_file(path):
    return app.send_static_file(path)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def path_router(path):
    context_data = handle_request(path)
    try:
        template = context_data['current']['template']
        return render_template(template, **context_data)
    except Exception as e:
        print(e)
        raise SystemExit


if __name__ == "__main__":
    app = create_app()
    app.run()
