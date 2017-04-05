import os
import requests
from git import Repo

from .utils import github_account
from shutil import get_terminal_size

home_dir = os.path.expanduser('~')
bentodev_dir = home_dir + '/bentodev/'
themes_dir = bentodev_dir + '/sites/'

width = int((get_terminal_size()[0] - 2) / 2)



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
            for theme in r.json():
                print('{0: <{2}} | {1: <{2}}'.format(theme['slug'], 'available', width))
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
                    Repo.clone_from(github_repo_url, themes_dir + '/' + slug)
        else:
            print("Error: {}".format(r.status_code))
