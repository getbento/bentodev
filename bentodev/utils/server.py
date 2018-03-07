import codecs
import os
import re
import sass
import jinja2.ext
from tempfile import TemporaryDirectory
from flask import Flask, render_template, make_response, abort, request, json, redirect
from inspect import getmembers, isfunction
from sassutils.wsgi import SassMiddleware
from bentodev.utils import filters
from bentodev.utils.environment import (
    CsrfExtension,
    ScssUrlExtension,
    SilentUndefined,
    StaticFilesExtension,
    PaginationExtension
)
from bentodev.utils.factory import HelpDataRequest, GenericFormRequest, CookieRequest, AjaxFormRequest


THEME = None
ACCOUNT = None
MACROS_DIR = os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), 'templates', 'jinja2', 'macros')
HOME_DIR = os.path.expanduser('~')
BENTODEV_URSER_DIR = os.path.join(HOME_DIR, 'bentodev')
REPO_DIR = None
STATIC_DIR = None
TEMPLATE_DIR = None
SCSS_DIR = None
CURRENT_CONTEXT_DATA = None
CURRENT_CSRF_TOKEN = None
CURRENT_SESSION_ID = None
LOCAL_HOST = '127.0.0.1'
LOCAL_PORT = '5000'
whitelisted_extensions = ['.scss', '.css', '.sass']

app = Flask(__name__)


def create_app():
    print(MACROS_DIR)
    app.debug = True
    app.threaded = True

    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.static_folder = STATIC_DIR
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
    app.jinja_env.add_extension(PaginationExtension)
    app.jinja_env.add_extension(jinja2.ext.do)
    app.jinja_env.add_extension(jinja2.ext.loopcontrols)
    app.jinja_env.add_extension(jinja2.ext.with_)
    custom_filters = {name: function for name, function in getmembers(filters) if isfunction(function)}
    app.jinja_env.filters.update(custom_filters)

    app.wsgi_app = SassMiddleware(app.wsgi_app, {
        'bentodev': (THEME + 'assets/sass', THEME + 'assets/css')
    })
    return app


def set_globals(theme, account, user_settings):
    global THEME, ACCOUNT, BENTODEV_URSER_DIR, REPO_DIR, STATIC_DIR, TEMPLATE_DIR, SCSS_DIR, LOCAL_HOST, LOCAL_PORT, LOCAL_URL
    THEME = theme
    ACCOUNT = account
    if 'DEV_ROOT' in user_settings:
        BENTODEV_URSER_DIR = user_settings['DEV_ROOT']
    REPO_DIR = os.path.join(BENTODEV_URSER_DIR, 'sites', THEME)
    STATIC_DIR = os.path.join(REPO_DIR, 'assets')
    TEMPLATE_DIR = os.path.join(REPO_DIR, 'templates')
    SCSS_DIR = os.path.join(REPO_DIR, 'assets', 'scss')
    if 'PORT' in user_settings:
        LOCAL_PORT = user_settings['PORT']
    if 'HOST' in user_settings:
        LOCAL_HOST = user_settings['HOST']
    LOCAL_URL = 'http://{}:{}/'.format(LOCAL_HOST, LOCAL_PORT)


def main(theme, account, user_settings):
    set_globals(theme, account, user_settings)
    app = create_app()
    app.run(host=LOCAL_HOST, port=int(LOCAL_PORT))


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
    with TemporaryDirectory() as BUILD_DIR:
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
                        filepath = os.path.join(root.replace(SCSS_DIR, ''), file)
                        template = app.jinja_env.get_template(filepath)
                        outfile.write(template.render(**CURRENT_CONTEXT_DATA))
                    except Exception as e:
                        print('Error: ' + str(e))
        file_path = os.path.join(BUILD_DIR, path.split('/')[-1])
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
            return redirect(LOCAL_URL+'store/cart', 302)


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
        return redirect(LOCAL_URL+'store/cart', 302)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def path_router(path):
    print('PATH: ' + path)
    if 'favicon' in path:
        return abort(404)
    context_data = handle_request(path)
    if not context_data:
        return redirect(LOCAL_URL, 302)
    get_csrf_token()
    if 'template' in context_data['current']:
        template = context_data['current']['template']
        print("TEMPLATE: " + template)
        context_data['current']['request']['is_ajax'] = False
        context_data['current']['request']['is_mobile'] = False
        response = make_response(render_template(template, **context_data))
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    else:
        print("No template defined in request.")
        return abort(404)


if __name__ == "__main__":
    main()
