import requests
from requests.exceptions import ConnectionError, Timeout
import json
from json.decoder import JSONDecodeError
from requests import Session


PROTOCOL = 'https://'
BENTOBOX_URL = 'www.getbento.com/'

# PROTOCOL = 'http://'
# BENTOBOX_URL = 'localtest.me:8000/'

ACCOUNT_URL = '{}{}'.format(
    BENTOBOX_URL, 'api/account')
ACCOUNTS_URL = '{}{}{}'.format(
    PROTOCOL, BENTOBOX_URL, 'api/developers/accounts')
GITHUB_ACCOUNT_URL = '{}{}{}'.format(
    PROTOCOL, BENTOBOX_URL, 'api/developers/github-account/')
THEMES_URL = '{}{}{}'.format(
    PROTOCOL, BENTOBOX_URL, 'api/developers/themes')
TOKEN_URL = '{}{}{}'.format(
    PROTOCOL, BENTOBOX_URL, 'api/developers/api-token-auth/')
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


class RequestFactory():

    def __init__(self, url=None, headers=None, data=None, token=None, cookies=None, *args, **kwargs):
        """" Initialize a request """
        self.url = url
        self.headers = {
            'Content-Type': 'application/json',
        }
        if headers:
            self.headers.update(headers)
        if token:
            self.headers.update({'Authorization': 'JWT ' + token})
        self.data = {}
        if data:
            self.data.update(data)
        self.cookies = {}
        if cookies:
            self.cookies.update(cookies)
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
            print("Cannot connect to BentoBox. Check network connection.")
            exit()
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
            print("Cannot connect to BentoBox. Check network connection.")
            exit()
        error(self)

    def json(self):
        try:
            return self.request.json()
        except JSONDecodeError:
            return None


class SessionFactory():

    def __init__(self, url=None, headers=None, data=None, token=None, cookies=None, *args, **kwargs):
        """" Initialize a request """
        self.url = url
        self.session = Session()
        self.session.headers.update({'Content-Type': 'application/json'})
        if headers:
            self.session.headers.update(headers)
        if token:
            self.session.headers.update({'Authorization': 'JWT ' + token})
        self.data = {}
        if data:
            self.data.update(data)
        self.cookies = {}
        if cookies:
            self.cookies.update(cookies)
        self.request = None

    def get(self):
        """" Make a get request """
        try:
            self.request = self.session.get(
                self.url,
                data=json.dumps(self.data),
                cookies=self.cookies,
            )
        except (ConnectionError, Timeout):
            print("Cannot connect to BentoBox. Check network connection.")
            exit()
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
            # if self.request.history[0].request:
            #     post()
        except (ConnectionError, Timeout):
            print("Cannot connect to BentoBox. Check network connection.")
            exit()
        error(self)

    def json(self):
        try:
            return self.request.json()
        except JSONDecodeError:
            return None


class TokenRequest(RequestFactory):

    def __init__(self, url=None, headers=None, data=None, token=None, *args, **kwargs):
        super(TokenRequest, self).__init__(url=TOKEN_URL, data=data)

    def post(self):
        super(TokenRequest, self).post()
        self.data = {}


class VerifyRequest(SessionFactory):
    def __init__(self, url=None, headers=None, data=None, token=None, *args, **kwargs):
        super(VerifyRequest, self).__init__(url=VERIFY_URL, token=token, data=data)


class GitHubAccountRequest(SessionFactory):
    def __init__(self, url=None, headers=None, data=None, token=None, *args, **kwargs):
        super(GitHubAccountRequest, self).__init__(
            headers=headers,
            url=GITHUB_ACCOUNT_URL,
            data=data,
            token=token,
        )

    def get(self):
        super(GitHubAccountRequest, self).get()
        super(GitHubAccountRequest, self).get()


class HelpDataRequest(RequestFactory):
    def __init__(self, url=None, headers=None, data=None, token=None, cookies=None, *args, **kwargs):
        super(HelpDataRequest, self).__init__(
            url=context_url_build(account=kwargs['account'], path=kwargs['path']),
            headers={'X-Requested-With': 'XMLHttpRequest'},
            cookies=cookies
        )


class CookieRequest(RequestFactory):
    def __init__(self, url=None, headers=None, data=None, token=None, *args, **kwargs):
        super(CookieRequest, self).__init__(
            url=CSRF_TOKEN_URL
        )
        del self.headers['Content-Type']


class AccountRequest(SessionFactory):
    def __init__(self, url=None, headers=None, data=None, token=None, *args, **kwargs):
        url = account_url_builder(account=kwargs['account'])
        print(url)
        super(AccountRequest, self).__init__(
            url=url,
            token=token
        )

    def get(self):
        super(AccountRequest, self).get()
        super(AccountRequest, self).get()


class AjaxFormRequest(RequestFactory):
    def __init__(self, url=None, headers=None, data=None, token=None,  cookies=None, *args, **kwargs):
        for k, v in kwargs.items():
            print(k + ': ' + v)
        super(AjaxFormRequest, self).__init__(
            url=form_url_build(account=kwargs['account'], path=kwargs['path']),
            headers={
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': kwargs['csrf_token'],
                'Referer': kwargs['referer']
            },
            data=data,
            cookies=cookies,
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
    def __init__(self, url=None, headers=None, data=None, token=None,  cookies=None, *args, **kwargs):
        super(GenericFormRequest, self).__init__(
            url=form_url_build(account=kwargs['account'], path=kwargs['path']),
            headers={
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Referer': kwargs['referer']
            },
            data=data,
            cookies=cookies,
        )

    def get(self):
        print(self.url)
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
