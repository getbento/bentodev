import codecs
import os
import re
import sass
import jinja2.ext
from flask import Flask, render_template, make_response, abort, request, json, redirect, url_for, Response
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
from bentodev.config.factory import HelpDataRequest, GenericFormRequest, CookieRequest, AjaxFormRequest


REPO = str(environ['REPO'])
ACCOUNT = str(environ['ACCOUNT'])
ENVIRON = str(environ['ENVIRON'])
HOME_DIR = path.expanduser('~')
BENTODEV_DIR = HOME_DIR + '/bentodev/'
REPO_DIR = '{}{}{}'.format(BENTODEV_DIR, 'sites/', REPO)
STATIC_DIR = '{}{}'.format(REPO_DIR, '/assets/')
TEMPLATE_DIR = '{}{}'.format(REPO_DIR, '/templates/')
SCSS_DIR = '{}{}'.format(REPO_DIR, '/assets/scss/')
BUILD_DIR = '{}{}'.format(REPO_DIR, '/assets/build/')
MACROS_DIR = '{}{}'.format(path.abspath(path.dirname(__file__)), '/templates/macros/')
CURRENT_CONTEXT_DATA = None
CURRENT_CSRF_TOKEN = None
CURRENT_SESSION_ID = None
whitelisted_extensions = ['.scss', '.css', '.sass']


def create_app():
    app = Flask(__name__)
    app.static_folder = STATIC_DIR
    print(MACROS_DIR)
    loader = jinja2.ChoiceLoader([
        app.jinja_loader,
        jinja2.FileSystemLoader([TEMPLATE_DIR, SCSS_DIR, MACROS_DIR]),
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
    global CURRENT_CONTEXT_DATA
    global CURRENT_CSRF_TOKEN
    cookies = {
        'csrftoken': CURRENT_CSRF_TOKEN,
        'csrfmiddlewaretoken': CURRENT_CSRF_TOKEN,
        'sessionid': CURRENT_SESSION_ID
    }
    kwargs = {
        'account': ACCOUNT,
        'path': path,
        'help': True,
        'cookies': cookies
    }
    r = HelpDataRequest(**kwargs)
    print('REQUEST: ' + r.url)
    r.get()
    if r.json():
        CURRENT_CONTEXT_DATA = r.json()
        return r.json()
    else:
        print("No Context Data Returned")
        return None


def set_cookies(cookies):
    if 'csrftoken' in cookies:
        global CURRENT_CSRF_TOKEN
        if not CURRENT_CSRF_TOKEN or (CURRENT_CSRF_TOKEN != cookies['csrftoken']):
            CURRENT_CSRF_TOKEN = cookies['csrftoken']
    if 'sessionid' in cookies:
        global CURRENT_SESSION_ID
        if not CURRENT_SESSION_ID or (CURRENT_SESSION_ID != cookies['sessionid']):
            CURRENT_SESSION_ID = cookies['sessionid']


def get_csrf_token():
    r = CookieRequest()
    r.get()
    if 'Set-Cookie' in r.request.headers:
        set_cookies(r.request.cookies)


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
def static_file_router(path):
    print('REQUEST: ' + path)
    r = None
    try:
        if '.scss' in path:
            scss = compile_scss(path)
            r = make_response(scss)
            r.headers['Content-Type'] = 'text/css'
        else:
            r = app.send_static_file(path)
            r.headers.add('Access-Control-Allow-Origin', '*')
        return r
    except Exception as e:
        print(e)
        abort(404)


@app.route('/form_to_email/', methods=['POST'])
def form_to_email_router():
    resource_url = request.url
    resource_url = resource_url.replace(request.url_root, '')
    get_csrf_token()
    kwargs = {
        'account': ACCOUNT,
        'path': resource_url,
        'csrf_token': CURRENT_CSRF_TOKEN,
        'referer': 'https://{}.getbento.com/{}'.format(ACCOUNT, 'contact/'),
        'data': request.form.to_dict()
    }
    r = AjaxFormRequest(**kwargs)
    r.post()
    response = app.response_class(
        response=json.dumps(r.request.json()),
        status=r.request.status_code,
        mimetype=r.request.headers['Content-Type']
    )
    return response


@app.route('/forms/<path:path>', methods=['POST'])
def generic_form_router(path):
    get_csrf_token()
    kwargs = {
        'account': ACCOUNT,
        'path': '{}{}'.format('forms/', path),
        'data': request.form.to_dict()
    }
    r = GenericFormRequest(**kwargs)
    r.post()

    response = app.response_class(
        response=json.dumps(r.request.json()),
        status=r.request.status_code,
        mimetype=r.request.headers['Content-Type']
    )
    return response


@app.route('/store/<path:path>', methods=['POST'])
def generic_store_router(path):
    STORE_PATH_URL = 'store/' + path
    args = re.split(r'{}'.format(STORE_PATH_URL), request.url)[-1]
    path = '{}{}'.format(STORE_PATH_URL, args)
    get_csrf_token()
    cookies = {
        'csrftoken': CURRENT_CSRF_TOKEN,
        'csrfmiddlewaretoken': CURRENT_CSRF_TOKEN,
        'sessionid': CURRENT_SESSION_ID
    }
    kwargs = {
        'account': ACCOUNT,
        'path': path,
        'csrf_token': CURRENT_CSRF_TOKEN,
        'referer': 'https://{}.getbento.com/{}'.format(ACCOUNT, STORE_PATH_URL),
        'cookies': cookies,
        'data': request.form.to_dict()
    }
    r = None
    if 'X-Requested-With' in request.headers:
        kwargs['data'].update(cookies)
        r = AjaxFormRequest(**kwargs)
        r.post()
        if 'Set-Cookie' in r.request.headers:
            set_cookies(r.request.cookies)
        return app.response_class(
            response=r.request.text,
            status=r.request.status_code,
            mimetype=r.request.headers['Content-Type']
        )
    else:
        kwargs['data'].update(cookies)
        r = GenericFormRequest(**kwargs)
        r.post()
        if 'Set-Cookie' in r.request.headers:
            set_cookies(r.request.cookies)
        if r.request.status_code:
            return redirect('http://localhost:5000/store/cart', 302)


@app.route('/store/cart/update/<path:path>', methods=['GET'])
def cart_item_router(path):
    CART_ITEM_UPDATE_URL = 'store/cart/update/'
    args = re.split(r'{}'.format(CART_ITEM_UPDATE_URL), request.url)[-1]
    path = '{}{}'.format(CART_ITEM_UPDATE_URL, args)
    cookies = {
        'csrftoken': CURRENT_CSRF_TOKEN,
        'csrfmiddlewaretoken': CURRENT_CSRF_TOKEN,
        'sessionid': CURRENT_SESSION_ID
    }
    kwargs = {
        'account': ACCOUNT,
        'path': path,
        'csrf_token': CURRENT_CSRF_TOKEN,
        'referer': 'https://{}.getbento.com/{}'.format(ACCOUNT, 'store'),
        'data': request.form.to_dict(),
        'cookies': cookies
    }
    r = None
    if 'X-Requested-With' in request.headers:
        r = AjaxFormRequest(**kwargs)
        r.get()
        return app.response_class(
            response=r.request.text,
            status=r.request.status_code,
            mimetype=r.request.headers['Content-Type']
        )
    else:
        kwargs['data'].update(cookies)
        r = GenericFormRequest(**kwargs)
        r.get()
        return redirect('http://localhost:5000/store/cart', 302)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def path_router(path):
    print('PATH: ' + path)
    context_data = handle_request(path)
    if not context_data:
        return redirect('http://localhost:5000/', 302)
    get_csrf_token()
    if 'template' in context_data['current']:
        template = context_data['current']['template']
        print("TEMPLATE: " + template)
        response = make_response(render_template(template, **context_data))
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    else:
        print("No template defined in request.")
        return abort(404)


if __name__ == "__main__":
    app = create_app()
    app.run()
