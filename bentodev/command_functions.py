import os

from enum import Enum
from git import Repo
from shutil import get_terminal_size
from webbrowser import open_new_tab
from functools import wraps

from bentodev.config.factory import AccountRequest, SessionFactory, ACCOUNTS_URL, THEMES_URL, TOKEN_URL
from bentodev.utils import github_account

HOME_DIR = os.path.expanduser('~')
BENTODEV_DIR = HOME_DIR + '/bentodev/'
THEMES_DIR = BENTODEV_DIR + 'sites/'
WIDTH = int((get_terminal_size()[0] - 5) / 2)


class ListFlags(Enum):
    CLONE = 1
    START = 2


# @check_local
def get_theme(token, account):
    kwargs = {
        'account': account,
        'help': True,
        'token': token
    }
    r = AccountRequest(**kwargs)
    r.get()
    if r.request.ok and r.json():
        theme_pk = r.json()[0]['theme']
        url = '{}/{}'.format(THEMES_URL, theme_pk)
        s = SessionFactory(url=url, token=token)
        s.get()
        s.get()
        if s.request.ok and s.json():
            return s.json()['slug']


def get_cloned_themes():
    return {name for name in os.listdir(THEMES_DIR)}


def list_available_repos():
    print("Select a theme to work with:")
    print('{0:-<{WIDTH}}'.format('-', '', WIDTH=WIDTH*2))
    [print(theme) for theme in get_cloned_themes()]


def list_accounts(token, flag=None):
    if github_account(token):
        kwargs = {
            'url': ACCOUNTS_URL,
            'token': token
        }
        r = SessionFactory(**kwargs)
        r.get()
        if r.request.ok and r.json():
            print('{0: <{2}} | {1: <{2}}'.format('Account', 'Theme', WIDTH))
            print('{0:-<{WIDTH}}'.format('-', '', WIDTH=WIDTH*2))
            cloned_themes = get_cloned_themes()
            for account in r.json():
                slug = account['slug']
                theme_name = account['theme']
                status = '[available]'
                if theme_name in cloned_themes:
                    if flag is ListFlags.CLONE:
                        break
                    status = '[cloned]'
                print('{0: <{3}} | {1:<15} {2: <{3}}'.format(slug, theme_name, status, WIDTH))


def run_flask(account, repo):
    cloned_themes = get_cloned_themes()
    if repo not in cloned_themes:
        print("Theme has not been cloned!")
        raise SystemExit
    dir = os.path.dirname(os.path.realpath(__file__))
    os.environ['ACCOUNT'] = account
    os.environ['REPO'] = repo
    os.environ['FLASK_APP'] = dir + '/server.py'
    os.system("flask run --debugger")


def clone_repo(token, slug):
    if github_account(token):
        kwargs = {
            'url': THEMES_URL,
            'token': token
        }
        r = SessionFactory(**kwargs)
        r.get()
        if r.json():
            for theme in r.json():
                if theme['slug'] == slug:
                    github_repo_url = (theme['github_repo_url'])
                    try:
                        clone_dir = '{}{}'.format(THEMES_DIR, slug)
                        Repo.clone_from(github_repo_url, clone_dir)
                        print('Succesfully cloned {} to:\n{}'.format(slug, clone_dir))
                    except Exception as e:
                        print(e)
                        raise SystemExit
