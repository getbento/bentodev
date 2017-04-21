import requests
from requests.exceptions import ConnectionError, Timeout
import json
from json.decoder import JSONDecodeError


PROTOCOL = 'http://'
SECURE_PROTOCOL = 'https://'
BENTOBOX_URL = 'getbento.com/'
BENTOBOX_LOCAL_URL = 'localtest.me:8000/'

ACCOUNT_URL = '{}{}'.format(
    BENTOBOX_LOCAL_URL, 'api/account')
ACCOUNTS_URL = '{}{}{}'.format(
    PROTOCOL, BENTOBOX_LOCAL_URL, 'api/developers/accounts')
GITHUB_ACCOUNT_URL = '{}{}{}'.format(
    PROTOCOL, BENTOBOX_LOCAL_URL, 'api/developers/github_account/')
THEMES_URL = '{}{}{}'.format(
    PROTOCOL, BENTOBOX_LOCAL_URL, 'api/developers/themes')
TOKEN_URL = '{}{}{}'.format(
    PROTOCOL, BENTOBOX_LOCAL_URL, 'api/developers/api-token-auth/')
VERIFY_URL = '{}{}{}'.format(
    PROTOCOL, BENTOBOX_LOCAL_URL, 'api/developers/api-token-verify/')


def error(self):
    if not self.request.ok:
        print(self.request.text)
        print(self.request.status_code)


def context_url_build(account, path=''):
    return '{}{}.{}{}{}'.format(PROTOCOL, account, BENTOBOX_LOCAL_URL, path, '?help')


def account_url_builder(account):
    return '{}{}.{}'.format(PROTOCOL, account, ACCOUNT_URL)


def form_url_build(account, path):
    return '{}{}.{}{}'.format(
        PROTOCOL, account, BENTOBOX_LOCAL_URL, path)


def store_token_url_build(account, path):
    # return '{}{}.{}{}{}'.format(PROTOCOL, account, BENTOBOX_LOCAL_URL, 'store/', path)
    return '{}{}.{}{}'.format(PROTOCOL, account, BENTOBOX_LOCAL_URL, path)


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
                cookies=self.cookies
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
                cookies=self.cookies
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


class TokenRequest(RequestFactory):

    def __init__(self, url=None, headers=None, data=None, token=None, *args, **kwargs):
        super(TokenRequest, self).__init__(url=TOKEN_URL, data=data)

    def post(self):
        super(TokenRequest, self).post()
        self.data = {}


class VerifyRequest(RequestFactory):
    def __init__(self, url=None, headers=None, data=None, token=None, *args, **kwargs):
        super(VerifyRequest, self).__init__(url=VERIFY_URL, data=data)


class GitHubAccountRequest(RequestFactory):
    def __init__(self, url=None, headers=None, data=None, token=None, *args, **kwargs):
        super(GitHubAccountRequest, self).__init__(
            headers=headers,
            url=GITHUB_ACCOUNT_URL,
            data=data,
            token=token
        )


class HelpDataRequest(RequestFactory):
    def __init__(self, url=None, headers=None, data=None, token=None, cookies=None, *args, **kwargs):
        super(HelpDataRequest, self).__init__(
            url=context_url_build(account=kwargs['account'], path=kwargs['path']),
            headers={'X-Requested-With': 'XMLHttpRequest'},
            cookies=cookies
        )


class CookieRequest(RequestFactory):
    def __init__(self, url=None, headers=None, data=None, token=None, *args, **kwargs):
        url = store_token_url_build(account=kwargs['account'], path=kwargs['path'])
        super(CookieRequest, self).__init__(
            url=url
        )
        del self.headers['Content-Type']


class AccountRequest(RequestFactory):
    def __init__(self, url=None, headers=None, data=None, token=None, *args, **kwargs):
        super(AccountRequest, self).__init__(
            url=account_url_builder(account=kwargs['account']),
            token=token
        )


class AjaxFormRequest(RequestFactory):
    def __init__(self, url=None, headers=None, data=None, token=None,  cookies=None, *args, **kwargs):
        super(AjaxFormRequest, self).__init__(
            url=form_url_build(account=kwargs['account'], path=kwargs['path']),
            headers={
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': kwargs['csrf_token']
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
