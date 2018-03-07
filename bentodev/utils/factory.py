import requests
from requests.exceptions import ConnectionError, Timeout
import json
from json.decoder import JSONDecodeError
from requests import Session
from requests.models import Response
from os import environ


try:
    ENVIRON = str(environ['ENVIRON'])
except KeyError:
    ENVIRON = 'production'

if ENVIRON == 'local':
    PROTOCOL = 'http://'
    BENTOBOX_URL = 'localtest.me:8000/'
else:
    PROTOCOL = 'https://'
    BENTOBOX_URL = 'www.getbento.com/'


ACCOUNT_URL = '{}{}'.format(
    BENTOBOX_URL, 'api/account')
ACCOUNTS_URL = '{}{}{}'.format(
    PROTOCOL, BENTOBOX_URL, 'api/developers/accounts')
GITHUB_ACCOUNT_URL = '{}{}{}'.format(
    PROTOCOL, BENTOBOX_URL, 'api/developers/github-account/')
THEMES_URL = '{}{}{}'.format(
    PROTOCOL, BENTOBOX_URL, 'api/developers/themes')
TOKEN_URL = '{}{}{}'.format(
    PROTOCOL, BENTOBOX_URL.replace('www.', ''), 'api/developers/api-token-auth/')
VERIFY_URL = '{}{}{}'.format(
    PROTOCOL, BENTOBOX_URL, 'api/developers/api-token-verify/')
CSRF_TOKEN_URL = '{}{}{}'.format(
    PROTOCOL, BENTOBOX_URL, 'api/developers/csrf-token/')


def error(self):
    if not self.request.ok:
        if not (self.request.status_code == 403 and self.request.text == '{"detail":"Authentication credentials were not provided."}'):
            print('Error: ' + str(self.request.status_code))
            print(self.request.text)


def context_url_build(account, path=''):
    url = BENTOBOX_URL
    if 'www' in BENTOBOX_URL:
        url = BENTOBOX_URL.replace('www.', '')
    return '{}{}.{}{}{}'.format(PROTOCOL, account, url, path, '?help')


def account_url_builder(account):
    url = ACCOUNT_URL
    if 'www' in ACCOUNT_URL:
        url = ACCOUNT_URL.replace('www.', '')
    return '{}{}.{}'.format(PROTOCOL, account, url)


def form_url_build(account, path):
    url = BENTOBOX_URL
    if 'www' in BENTOBOX_URL:
        url = BENTOBOX_URL.replace('www.', '')

    return '{}{}.{}{}'.format(
        PROTOCOL, account, url, path)


def store_token_url_build(account, path):
    return '{}{}.{}{}'.format(PROTOCOL, account, BENTOBOX_URL, path)


def connection_error():
    print("Cannot connect to BentoBox. Check network connection.")
    if ENVIRON == 'local':
        print("Local sever may not be running.")
    exit()


class RequestFactory():

    def __init__(self, *args, **kwargs):
        """" Initialize a request """
        self.url = kwargs['url']
        self.headers = {
            'Content-Type': 'application/json',
        }
        if 'headers' in kwargs:
            self.headers.update(kwargs['headers'])
        if 'token' in kwargs:
            self.headers.update({'Authorization': 'JWT ' + kwargs['token']})
        self.data = {}
        if 'data' in kwargs:
            self.data.update(kwargs['data'])
        self.cookies = {}
        if 'cookies' in kwargs:
            self.cookies.update(kwargs['cookies'])
        self.request = None

    def get(self):
        """" Make a get request """
        try:
            self.request = requests.get(
                self.url,
                data=json.dumps(self.data),
                headers=self.headers,
                cookies=self.cookies,
            )
        except (ConnectionError, Timeout):
            connection_error()
        error(self)

    def post(self):
        """" Make a post request """
        try:
            self.request = requests.post(
                self.url,
                data=json.dumps(self.data),
                headers=self.headers,
                cookies=self.cookies,
                allow_redirects=False
            )
        except (ConnectionError, Timeout):
            connection_error()
        error(self)

    def json(self):
        try:
            return self.request.json()
        except JSONDecodeError:
            return None


class SessionFactory():

    def __init__(self, *args, **kwargs):
        """" Initialize a request """
        self.url = kwargs['url']
        self.session = Session()
        self.session.headers.update({'Content-Type': 'application/json'})
        if 'headers' in kwargs:
            self.session.headers.update(kwargs['headers'])
        if 'token' in kwargs:
            self.session.headers.update(
                {'Authorization': 'JWT ' + kwargs['token']})
        self.data = {}
        if 'data' in kwargs:
            self.data.update(kwargs['data'])
        self.cookies = {}
        if 'cookies' in kwargs:
            self.cookies.update(kwargs['cookies'])
        self.request = None

    def get(self):
        """" Make a get request """
        try:
            self.request = self.session.get(
                self.url,
                data=json.dumps(self.data),
                cookies=self.cookies,
            )
            if self.request.history and type(self.request.history[0]) is Response and self.request.history[0].status_code == 301:
                self.get()
        except (ConnectionError, Timeout):
            connection_error()
        error(self)

    def post(self):
        """" Make a post request """
        try:
            self.request = self.session.post(
                self.url,
                data=json.dumps(self.data),
                cookies=self.cookies,
                allow_redirects=False
            )
            if self.request.history and type(self.request.history[0]) is Response and self.request.history[0].status_code == 301:
                self.post()
        except (ConnectionError, Timeout):
            connection_error()
        error(self)

    def json(self):
        try:
            return self.request.json()
        except JSONDecodeError:
            return None


class TokenRequest(RequestFactory):

    def __init__(self, *args, **kwargs):
        super(TokenRequest, self).__init__(url=TOKEN_URL, data=kwargs['data'])

    def post(self):
        """" Make a post request """
        self.request = requests.post(self.url, self.data)
        self.data = {}


class VerifyRequest(SessionFactory):

    def __init__(self, *args, **kwargs):
        super(VerifyRequest, self).__init__(
            url=VERIFY_URL,
            token=kwargs['token'],
            data=kwargs['data']
        )


class GitHubAccountRequest(SessionFactory):

    def __init__(self, *args, **kwargs):
        super(GitHubAccountRequest, self).__init__(
            url=GITHUB_ACCOUNT_URL,
            token=kwargs['token'],
        )


class HelpDataRequest(RequestFactory):

    def __init__(self, *args, **kwargs):
        super(HelpDataRequest, self).__init__(
            url=context_url_build(
                account=kwargs['account'], path=kwargs['path']),
            headers={'X-Requested-With': 'XMLHttpRequest'},
            cookies=kwargs['cookies']
        )


class CookieRequest(RequestFactory):

    def __init__(self, *args, **kwargs):
        super(CookieRequest, self).__init__(
            url=CSRF_TOKEN_URL
        )
        del self.headers['Content-Type']


class AccountRequest(SessionFactory):

    def __init__(self, *args, **kwargs):
        super(AccountRequest, self).__init__(
            url=account_url_builder(account=kwargs['account']),
            token=kwargs['token']
        )

    def get(self):
        super(AccountRequest, self).get()
        super(AccountRequest, self).get()


class AjaxFormRequest(RequestFactory):

    def __init__(self, *args, **kwargs):
        super(AjaxFormRequest, self).__init__(
            url=form_url_build(account=kwargs['account'], path=kwargs['path']),
            headers={
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': kwargs['csrf_token'],
                'Referer': kwargs['referer']
            },
            data=kwargs['data'],
            cookies=kwargs['data'],
        )

    def post(self):
        """" Make a post request """
        self.request = requests.post(
            self.url,
            data=self.data,
            headers=self.headers,
            cookies=self.cookies,
        )
        error(self)


class GenericFormRequest(RequestFactory):

    def __init__(self, *args, **kwargs):
        super(GenericFormRequest, self).__init__(
            url=form_url_build(account=kwargs['account'], path=kwargs['path']),
            headers={
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Referer': kwargs['referer']
            },
            data=kwargs['data'],
            cookies=kwargs['cookies'],
        )

    def get(self):
        """" Make a post request """
        self.request = requests.get(
            self.url,
            data=self.data,
            headers=self.headers,
            cookies=self.cookies,
            allow_redirects=False,
        )

    def post(self):
        """" Make a post request """
        self.request = requests.post(
            self.url,
            data=self.data,
            headers=self.headers,
            cookies=self.cookies,
            allow_redirects=False,
        )
        error(self)
