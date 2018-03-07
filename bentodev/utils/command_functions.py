import os

from enum import Enum
from git import Repo
from shutil import get_terminal_size
from webbrowser import open_new_tab
from functools import wraps

from bentodev.utils.factory import (
    AccountRequest,
    SessionFactory,
    ACCOUNTS_URL,
    THEMES_URL,
    TOKEN_URL
)
from bentodev.utils.helpers import github_account, get_user_settings
from bentodev.utils.server import main

HOME_DIR = os.path.expanduser('~')
BENTODEV_DIR = HOME_DIR + '/bentodev/'
THEMES_DIR = BENTODEV_DIR + 'sites/'
WIDTH = int((get_terminal_size()[0] - 5) / 2)


class ListFlags(Enum):
    CLONE = 1
    START = 2


def set_user_settings():
    user_settings = get_user_settings()
    if 'DEV_ROOT' in user_settings:
        if os.path.exists(user_settings['DEV_ROOT']):
            global THEMES_DIR
            THEMES_DIR = THEMES_DIR.replace(
                BENTODEV_DIR, user_settings['DEV_ROOT'])
        else:
            print('Path defined for DEV_ROOT does not exist')
            raise SystemExit
    return user_settings


def get_theme(token, account):
    kwargs = {
        'account': account,
        'help': True,
        'token': token
    }
    r = AccountRequest(**kwargs)
    print(r.url)
    r.get()
    if r.request.ok and r.json():
        theme_pk = r.json()[0]['theme']
        url = '{}/{}'.format(THEMES_URL, theme_pk)
        s = SessionFactory(url=url, token=token)
        print(s.url)
        s.get()
        s.get()
        if s.request.ok and s.json():
            return s.json()['slug']


def get_cloned_themes():
    if os.path.exists(THEMES_DIR):
        return {name for name in os.listdir(THEMES_DIR)}
    else:
        print('Custom folder `{}` does not exists.\nPlease create the folder.'.format(
            str(THEMES_DIR)))
        raise SystemExit


def list_available_repos():
    set_user_settings()
    cloned_themes = get_cloned_themes()
    print("Select a theme to work with:")
    print('{0:-<{WIDTH}}'.format('-', '', WIDTH=WIDTH * 2))
    [print(theme) for theme in cloned_themes]


def list_accounts(token, flag=None):
    set_user_settings()
    if github_account(token):
        kwargs = {
            'url': ACCOUNTS_URL,
            'token': token
        }
        r = SessionFactory(**kwargs)
        r.get()
        if r.request.ok and r.json():
            cloned_themes = get_cloned_themes()
            print('{0: <{2}} | {1: <{2}}'.format('Account', 'Theme', WIDTH))
            print('{0:-<{WIDTH}}'.format('-', '', WIDTH=WIDTH * 2))
            for account in r.json():
                slug = account['slug']
                theme_name = account['theme']
                status = '[available]'
                if theme_name in cloned_themes:
                    if flag is ListFlags.CLONE:
                        break
                    status = '[cloned]'
                print('{0: <{3}} | {1:<15} {2: <{3}}'.format(
                    slug, theme_name, status, WIDTH))


def run_flask(account, theme):
    user_settings = set_user_settings()
    cloned_themes = get_cloned_themes()
    if theme not in cloned_themes:
        print("Theme `{}` has not been cloned!".format(theme))
        raise SystemExit
    main(theme, account, user_settings)


def clone_repo(token, slug):
    set_user_settings()
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
                    github_repo_url = 'git@github.com:getbento/{}.git'.format(
                        slug)
                    try:
                        clone_dir = '{}{}'.format(THEMES_DIR, slug)
                        if github_repo_url:
                            Repo.clone_from(github_repo_url, clone_dir)
                            print('Succesfully cloned {} to:\n{}'.format(
                                slug, clone_dir))
                        else:
                            print(
                                'GitHub repo url not connected to theme through BentoBox')
                    except Exception as e:
                        print(e)
                        raise SystemExit
