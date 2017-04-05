import json
import requests
from .utils import github_account

width = 30

def get_repo_list(token):

    if github_account(token):

        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'JWT ' + token,
        }

        r = requests.get('http://localtest.me:8000/api/theme_repos', headers=headers)

        if r.ok and r.json():
            print('Themes')
            print('{0: <{2}} | {1: <{2}}'.format('Slug', 'Status', width))
            print('{0:-<{width}}'.format('-', '', width=width*2))
            for theme in r.json():
                print('{0: <{2}} | {1: <{2}}'.format(theme['slug'], 'available', width))
        else:
            print("Error: {}".format(r.status_code))
