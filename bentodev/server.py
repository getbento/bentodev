import os
import codecs
import sass
import jinja2.ext
from tempfile import mkdtemp

from flask import Flask, render_template, make_response
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

REPO_DIR = '{}{}{}'.format(BENTODEV_DIR, 'sites/', REPO)
STATIC_DIR = '{}{}'.format(REPO_DIR, '/assets/')
TEMPLATE_DIR = '{}{}'.format(REPO_DIR, '/templates/')
SCSS_DIR = '{}{}'.format(REPO_DIR, '/assets/scss/')
BUILD_DIR = '{}{}'.format(REPO_DIR, '/assets/build/')

CURRENT_CONTEXT_DATA = None

whitelisted_extensions = ['.scss', '.css', '.sass']


def create_app():
    app = Flask(__name__)
    app.static_folder = STATIC_DIR
    app.debug = True

    loader = jinja2.ChoiceLoader([
        app.jinja_loader,
        jinja2.FileSystemLoader([TEMPLATE_DIR, SCSS_DIR]),
    ])
    app.jinja_loader = loader

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
        global CURRENT_CONTEXT_DATA
        CURRENT_CONTEXT_DATA = r.json()
        return r.json()
    except Exception as e:
        print(e)
        raise SystemExit


def compile_scss(path):
    for root, dirs, files in os.walk(SCSS_DIR):
        new_path = root.replace(SCSS_DIR, BUILD_DIR)
        if not os.path.isdir(new_path):
            os.makedirs(new_path)
        for file in files:
            name, extension = os.path.splitext(file)
            if extension not in whitelisted_extensions:
                continue
            with codecs.open(os.path.join(new_path, file), 'w+', 'utf-8') as outfile:
                try:
                    filepath = "{}/{}".format(root.replace(SCSS_DIR, ''), file)
                    template = app.jinja_env.get_template(filepath)
                    outfile.write(template.render(**CURRENT_CONTEXT_DATA))
                except Exception as e:
                    print('Error: ' + str(e))

    file_path = "{}{}".format(BUILD_DIR, path.split('/')[-1])

    with codecs.open(file_path, 'r', 'utf-8') as file:
        scss = file.read()

    return sass.compile(string=scss, include_paths=[BUILD_DIR], output_style='nested')


@app.route('/assets/<path:path>')
def static_file(path):
    print('REQUEST: ' + path)
    if '.scss' in path:
        scss = compile_scss(path)
        response = make_response(scss)
        response.headers['Content-Type'] = 'text/css'
        return response
    else:
        response = app.send_static_file(path)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def path_router(path):
    context_data = handle_request(path)
    try:
        template = context_data['current']['template']
        print("TEMPLATE: " + template)
        response = make_response(render_template(template, **context_data))
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    except Exception as e:
        print("Error: " + str(e))


if __name__ == "__main__":
    app = create_app()
    app.run()
