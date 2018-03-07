from jinja2.ext import Extension
from jinja2 import Undefined, nodes
from bentodev.utils.helpers import get_user_settings
from bentodev.utils.paginator import Paginator

LOCAL_HOST = '127.0.0.1'
LOCAL_PORT = '5000'
LOCAL_URL = None


def set_globals():
    global LOCAL_HOST, LOCAL_PORT, LOCAL_URL
    user_settings = get_user_settings()
    if 'SERVER_URL' in user_settings:
        LOCAL_URL = user_settings['SERVER_URL']
    else:
        if 'PORT' in user_settings:
            LOCAL_PORT = user_settings['PORT']
        if 'HOST' in user_settings:
            LOCAL_HOST = user_settings['HOST']

        LOCAL_URL = 'http://{}:{}/'.format(LOCAL_HOST, LOCAL_PORT)


class CsrfExtension(Extension):
    """
    Implements django's `{% csrf_token %}` tag.
    Taken from: https://github.com/MoritzS/jinja2-django-tags/blob/master/jdj_tags/extensions.py
    """
    tags = set(['csrf_token'])

    def parse(self, parser):
        lineno = parser.stream.expect('name:csrf_token').lineno
        call = self.call_method(
            '_csrf_token',
            [nodes.Name('csrf_token', 'load', lineno=lineno)],
            lineno=lineno
        )
        return nodes.Output([nodes.MarkSafe(call)])

    def _csrf_token(self, csrf_token):
        if not csrf_token or csrf_token == 'NOTPROVIDED':
            return ''
        else:
            return '<input type="hidden" name="csrfmiddlewaretoken" value="{}" />' \
                .format(csrf_token)


class SilentUndefined(Undefined):
    """
    Dont break pageloads because vars arent there!
    """

    def _fail_with_undefined_error(self, *args, **kwargs):
        return ''


class StaticFilesExtension(Extension):

    def __init__(self, environment):
        super(StaticFilesExtension, self).__init__(environment)
        environment.globals["static"] = self._static

    def _static(self, path):
        set_globals()
        path = path.lstrip('/')
        url = '{}{}{}'.format(LOCAL_URL, 'assets/', path)
        return url


class ScssUrlExtension(Extension):

    def __init__(self, environment):
        super(ScssUrlExtension, self).__init__(environment)
        environment.globals["scss"] = self._scss

    def _scss(self, path, account=None):
        set_globals()
        path = path.lstrip('/')
        url = '{}{}{}'.format(LOCAL_URL, 'assets/', path)
        return url


class PaginationExtension(Extension):

    def __init__(self, environment):
        super(PaginationExtension, self).__init__(environment)
        environment.globals["paginate"] = self._paginate

    def _paginate(self, objects, page_size=20, query_param='p', current_page=None):
        paginator = Paginator(objects, page_size)
        return paginator.page(1)
