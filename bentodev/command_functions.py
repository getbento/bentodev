import os
import requests
from git import Repo

from .utils import github_account
from shutil import get_terminal_size

home_dir = os.path.expanduser('~')
bentodev_dir = home_dir + '/bentodev/'
themes_dir = bentodev_dir + 'sites/'

width = int((get_terminal_size()[0] - 5) / 2)


def get_theme(token, account):

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'JWT ' + token,
    }
    url = "http://{}.{}{}".format(account, 'localtest.me:8000', '/api/account')
    r = requests.get(url, headers=headers)

    theme_pk = None
    if r.ok and r.json():
        theme_pk = r.json()[0]['theme']
    else:
        print("Error: {}".format(r.status_code))

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'JWT ' + token,
    }
    url = "http://{}.{}{}{}".format(account, 'localtest.me:8000', '/api/themes/', theme_pk)

    if r.ok and r.json():
        r = requests.get(url, headers=headers)
        return r.json()['slug']
    else:
        print("Error: {}".format(r.status_code))


def list_accounts(token):
    if github_account(token):

        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'JWT ' + token,
        }

        r = requests.get('http://localtest.me:8000/api/accounts', headers=headers)

        if r.ok and r.json():
            for account in r.json():
                print('{0: <{2}} | {1: <{2}}'.format('Account', 'Theme', width))
                print('{0:-<{width}}'.format('-', '', width=width*2))
                cloned_themes = get_cloned_themes()
                for account in r.json():
                    slug = account['slug']
                    theme_name = account['theme']
                    status = '[available]'
                    if theme_name in cloned_themes:
                        status = '[cloned]'
                    print('{0: <{3}} | {1:<15} {2: <{3}}'.format(slug, theme_name, status, width))
        else:
            print("Error: {}".format(r.status_code))


def get_cloned_themes():
    return [name for name in os.listdir(themes_dir)]


def list_available_repos():
    print("Select a theme to work with:")
    print('{0:-<{width}}'.format('-', '', width=width*2))
    [print(theme) for theme in get_cloned_themes()]


def run_flask(account, repo):
    cloned_themes = get_cloned_themes()
    if repo not in cloned_themes:
        print("Theme has not been cloned!")
        raise SystemExit
    dir = os.path.dirname(os.path.realpath(__file__))
    os.environ['ACCOUNT'] = account
    os.environ['REPO'] = repo
    os.environ['FLASK_APP'] = dir + '/server.py'
    os.system("flask run")


def get_repo_list(token):
    if github_account(token):

        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'JWT ' + token,
        }

        r = requests.get('http://localtest.me:8000/api/themes', headers=headers)

        if r.ok and r.json():
            print('Themes')
            print('{0: <{2}} | {1: <{2}}'.format('Slug', 'Status', width))
            print('{0:-<{width}}'.format('-', '', width=width*2))
            cloned_themes = get_cloned_themes()
            for theme in r.json():
                theme_name = theme['slug']
                status = 'available'
                if theme_name in cloned_themes:
                    status = 'cloned'
                print('{0: <{2}} | {1: <{2}}'.format(theme_name, status, width))
        else:
            print("Error: {}".format(r.status_code))


def clone_repo(token, slug):
    if github_account(token):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'JWT ' + token,
        }

        r = requests.get('http://localtest.me:8000/api/themes', headers=headers)

        if r.ok and r.json():
            for theme in r.json():
                if theme['slug'] == slug:
                    github_repo_url = (theme['github_repo_url'])
                    try:
                        clone_dir = '{}{}'.format(themes_dir, slug)
                        Repo.clone_from(github_repo_url, clone_dir)
                        print('Succesfully cloned {} to:\n{}'.format(slug, clone_dir))
                    except Exception as e:
                        print(e)
                        raise SystemExit
        else:
            print("Error: {}".format(r.status_code))
