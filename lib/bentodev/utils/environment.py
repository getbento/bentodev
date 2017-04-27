from jinja2.ext import Extension
from jinja2 import Undefined, nodes


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
        path = path.lstrip('/')
        url = '{}{}'.format('http://localhost:5000/assets/', path)
        return url


class ScssUrlExtension(Extension):
    def __init__(self, environment):
        super(ScssUrlExtension, self).__init__(environment)
        environment.globals["scss"] = self._scss

    def _scss(self, path):
        # file_parts = path.split('.')
        path = path.lstrip('/')
        url = '{}{}'.format('http://localhost:5000/assets/', path)
        return url
