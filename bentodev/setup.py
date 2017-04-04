import json
import os
import requests

from getpass import getpass
from shutil import copy2

token_url = 'http://localtest.me:8000/api/api-token-auth/'
verify_url = 'http://localtest.me:8000/api/api-token-verify/'

home_dir = os.path.expanduser('~')
bentodev_dir = home_dir + '/bentodev/'
user_config = bentodev_dir + 'config.json'


def create_user_structure(verbose):
    if not os.path.exists(home_dir):
        if verbose:
            print('No home directory. Exiting gracefully.')
        raise SystemExit
    if not os.path.exists(bentodev_dir):
        if verbose:
            print("Creating ~/bentodev/ ...")
        os.makedirs(bentodev_dir)
    if not os.path.exists(user_config):
        if verbose:
            print("Creating ~/bentodev/config.json ...")
        dir = os.path.dirname(os.path.realpath(__file__))
        setup_file = dir + '/setup_files/config.json'
        copy2(setup_file, bentodev_dir)


def check_user(verbose, username=None):
    user = None

    while not user:
        config_file = open(user_config, "r")
        config_data = json.load(config_file)
        config_file.close()
        if not config_data['BENTO_USER']:
            if not username:
                username = input("Enter BentoBox Username: ")
            config_data['BENTO_USER'] = username
            with open(user_config, "w") as config_file:
                json.dump(config_data, config_file, sort_keys=True, indent=4)
            config_file.close()
        else:
            user = config_data['BENTO_USER']
    return user


def token_auth():
    user = check_user(verbose=False)
    print('Enter Password for BentoBox User: %s' % user)
    pw = getpass(prompt="Password: ")

    headers = {
        'Content-Type': 'application/json',
    }

    data = {
        'email': user,
        'password': pw,
    }

    r = requests.post(token_url, data=json.dumps(data), headers=headers)
    del pw

    token = ''
    if r.status_code == '200' and 'token' in r.json():
        token = r.json()['token']

    data = {
        'token': token,
    }

    r = requests.post(verify_url, data=json.dumps(data), headers=headers)
    if r.status_code == '200':
        print('Incorrect Token')
        raise SystemExit

    return token


def check():
    create_user_structure(verbose=False)
    check_user(verbose=False)
