import json
import requests


def get_repo_list(token):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'JWT ' + token,
    }

    r = requests.get('http://localtest.me:8000/api/theme_repos', headers=headers)

    if r.ok and r.json():
        print('Themes')
        print('Slug           |    Availability   ')
        print('-----------------------------------')
        for theme in r.json():
            line_output = '{}    |   [{}]'.format(theme['slug'], 'available')
            print(line_output)
    else:
        print("Error: {}".format(r.status_code))
