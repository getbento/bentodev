import json
import requests


def get_repo_list(token):
    headers = {
        'Content-Type': 'application/json',
    }

    data = {
        'token': token,
    }

    r = requests.get('http://localtest.me:8000/api/theme_repos', data=json.dumps(data), headers=headers)

    print('Themes')
    print('Slug           |    Availability   ')
    print('-----------------------------------')
    for theme in r.json():
        line_output = '{}    |   [{}]'.format(theme['slug'], 'available')
        print(line_output)
