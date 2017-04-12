import jinja2.ext

from flask import Flask, render_template
from inspect import getmembers, isfunction
from os import path, environ
from sassutils.wsgi import SassMiddleware

from bentodev.config import filters
from bentodev.config.environment import (
    CsrfExtension,
    ScssUrlExtension,
    SilentUndefined,
    StaticFilesExtension,
)
from bentodev.config.factory import HelpDataRequest

REPO = str(environ['REPO'])
ACCOUNT = str(environ['ACCOUNT'])

HOME_DIR = path.expanduser('~')
BENTODEV_DIR = HOME_DIR + '/bentodev/'

REPO_DIR = '{}{}{}/'.format(BENTODEV_DIR, 'sites/', REPO)
STATIC_DIR = BENTODEV_DIR + 'sites/{}/assets/'
TEMPLATE_DIR = BENTODEV_DIR + 'sites/{}/templates/'


def create_app():
    app = Flask(__name__)
    app.template_folder = TEMPLATE_DIR.format(REPO)
    app.static_folder = STATIC_DIR.format(REPO)
    app.debug = True

    app.jinja_env.autoescape = False
    app.jinja_env.undefined = SilentUndefined

    app.jinja_env.add_extension(CsrfExtension)
    app.jinja_env.add_extension(StaticFilesExtension)
    app.jinja_env.add_extension(ScssUrlExtension)
    app.jinja_env.add_extension(jinja2.ext.do)
    app.jinja_env.add_extension(jinja2.ext.loopcontrols)
    app.jinja_env.add_extension(jinja2.ext.with_)

    custom_filters = {name: function for name, function in getmembers(filters) if isfunction(function)}
    app.jinja_env.filters.update(custom_filters)
    app.config.update(
        DEBUG=True,
        TEMPLATES_AUTO_RELOAD=True
    )

    app.wsgi_app = SassMiddleware(app.wsgi_app, {
        'bentodev': (REPO + 'assets/sass', REPO + 'assets/css')
    })

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
    if 'scss' in path:
        print(path)
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
