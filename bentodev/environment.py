from jinja2.ext import Extension


class StaticFilesExtension(Extension):
    def __init__(self, environment):
        super(StaticFilesExtension, self).__init__(environment)

        environment.globals["static"] = self._static

    def _static(self, path):
        path = path.lstrip('/')
        url = '{}{}'.format('http://localhost:5000/assets/', path)
        return url
