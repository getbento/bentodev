import requests
import json

PROTOCOL = 'http://'
SECURE_PROTOCOL = 'https://'
BENTOBOX_URL = 'getbento.com/'
BENTOBOX_LOCAL_URL = 'localtest.me:8000/'

ACCOUNT_URL = '{}{}{}'.format(
    PROTOCOL, BENTOBOX_LOCAL_URL, 'api/account')
ACCOUNTS_URL = '{}{}{}'.format(
    PROTOCOL, BENTOBOX_LOCAL_URL, 'api/accounts')
GITHUB_ACCOUNT_URL = '{}{}{}'.format(
    PROTOCOL, BENTOBOX_LOCAL_URL, 'api/github_account/')
THEMES_URL = '{}{}{}'.format(
    PROTOCOL, BENTOBOX_LOCAL_URL, 'api/themes/')
TOKEN_URL = '{}{}{}'.format(
    PROTOCOL, BENTOBOX_LOCAL_URL, 'api/api-token-auth/')
VERIFY_URL = '{}{}{}'.format(
    PROTOCOL, BENTOBOX_LOCAL_URL, 'api/api-token-verify/')


def error(self):
    if not self.request.ok:
        print(self.request.text)
        print(self.request.status_code)


class RequestFactory():

    def __init__(self, url=None, headers=None, data=None, token=None):
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
        self.request = None

    def get(self):
        """" Make a get request """
        self.request = requests.get(
            self.url,
            data=json.dumps(self.data),
            headers=self.headers
        )
        error(self)

    def post(self):
        """" Make a post request """
        self.request = requests.post(
            self.url,
            data=json.dumps(self.data),
            headers=self.headers
        )
        error(self)

    def json(self):
        return self.request.json()


class TokenRequest(RequestFactory):

    def __init__(self, url=None, headers=None, data=None, token=None):
        super(TokenRequest, self).__init__(url=TOKEN_URL, data=data)

    def post(self):
        super(TokenRequest, self).post()
        self.data = {}


class VerifyRequest(RequestFactory):
    def __init__(self, url=None, headers=None, data=None, token=None):
        super(VerifyRequest, self).__init__(url=VERIFY_URL, data=data)


class GitHubAccountRequest(RequestFactory):
    def __init__(self, url=None, headers=None, data=None, token=None):
        super(GitHubAccountRequest, self).__init__(
            headers=headers,
            url=GITHUB_ACCOUNT_URL,
            data=data,
            token=token
        )
