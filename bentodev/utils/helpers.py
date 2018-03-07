import json
import os
from webbrowser import open_new_tab
from getpass import getpass
from shutil import copy2
from bentodev.utils.factory import (
    TokenRequest,
    VerifyRequest,
    GitHubAccountRequest
)

HOME_DIR = os.path.expanduser('~')
BENTODEV_USER_DIR = os.path.join(HOME_DIR, 'bentodev')
USER_CONFIG = os.path.join(BENTODEV_USER_DIR, 'config.json')
SITE_DIR = os.path.join(BENTODEV_USER_DIR, 'sites')

BENTODEV_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
CONFIG_DIR = os.path.join(BENTODEV_DIR, 'config')
GLOBAL_CONFIG = os.path.join(CONFIG_DIR, 'base_config.json')
CONFIG_EMPTY = os.path.join(BENTODEV_DIR, 'setup_files', 'config.json')
GLOBAL_CONFIG_EMPTY = os.path.join(
    BENTODEV_DIR, 'setup_files', 'base_config.json')


def create_user_structure(verbose):
    if not os.path.exists(HOME_DIR):
        if verbose:
            print('No home directory. Exiting gracefully.')
        raise SystemExit
    if not os.path.exists(BENTODEV_USER_DIR):
        if verbose:
            print("Creating ~/bentodev/ ...")
        os.makedirs(BENTODEV_USER_DIR)
    if not os.path.exists(SITE_DIR):
        if verbose:
            print("Creating ~/bentodev/sites/ ...")
        os.makedirs(SITE_DIR)
    if not os.path.exists(USER_CONFIG):
        if verbose:
            print("Creating ~/bentodev/config.json ...")
        copy2(CONFIG_EMPTY, BENTODEV_USER_DIR)
    if not os.path.exists(GLOBAL_CONFIG):
        if verbose:
            print("Creating global config ...")
        copy2(GLOBAL_CONFIG_EMPTY, CONFIG_DIR)


def check_user(verbose, username=None):
    user = None
    while not user:
        config_file = open(USER_CONFIG, "r")
        try:
            config_data = json.load(config_file)
            config_file.close()
            if not config_data['BENTO_USER']:
                if not username:
                    username = input("Enter BentoBox Username: ")
                config_data['BENTO_USER'] = username
                with open(USER_CONFIG, "w") as config_file:
                    json.dump(config_data, config_file,
                              sort_keys=True, indent=4)
                config_file.close()
            else:
                user = config_data['BENTO_USER']
        except json.decoder.JSONDecodeError as e:
            print("User configuration has malformed JSON.")
            print(e)
            raise SystemExit
    return user


def get_user_settings():
    config_file = open(USER_CONFIG, "r")
    try:
        config_data = json.load(config_file)
        config_file.close()
        return config_data
    except json.decoder.JSONDecodeError as e:
        print("User configuration has malformed JSON.")
        print(e)
        raise SystemExit


def token_auth():
    user = check_user(verbose=False)
    print('Enter Password for BentoBox User: %s' % user)
    pw = getpass(prompt="Password: ")
    data = {'email': user, 'password': pw}
    kwargs = {
        'data': data,
    }
    r = TokenRequest(**kwargs)
    r.post()
    del pw
    token = ''
    if 'token' in r.json():
        token = r.json()['token']
    if verify_token(token):
        return token


def verify_token(token):
    kwargs = {
        'token': token,
        'data': {'token': token}
    }
    r = VerifyRequest(**kwargs)
    r.post()
    if r.request.ok:
        return True
    print('Token Expired')
    return False


def write_config(config_data):
    with open(GLOBAL_CONFIG, "w") as config_file:
        json.dump(config_data, config_file, sort_keys=True, indent=4)
        config_file.close()


def get_token():
    config_file = open(GLOBAL_CONFIG, "r")
    try:
        config_data = json.load(config_file)
        config_file.close()
        token = ''
        while not token:
            if not config_data['BENTOBOX_TOKEN']:
                config_data['BENTOBOX_TOKEN'] = token_auth()
                write_config(config_data)
            elif not verify_token(config_data['BENTOBOX_TOKEN']):
                config_data['BENTOBOX_TOKEN'] = ''
                write_config(config_data)
            else:
                token = config_data['BENTOBOX_TOKEN']
        return token
    except json.decoder.JSONDecodeError as e:
        print("Token parsing error from malformed JSON.")
        print(e)
        raise SystemExit


def github_account(token, verbose=True):
    github_check = False
    while not github_check:
        if token:
            kwargs = {
                'token': token
            }
            r = GitHubAccountRequest(**kwargs)
            r.get()
            if r.request.ok and r.json() and verbose:
                print('Connected to GitHub Account: {}'.format(
                    str(r.json()[0]['username'])))
                github_check = True
            elif r.request.ok and not r.json():
                print('You have not connected your GitHub!')
                print('Opening BentoBox Admin to Connect GitHub Account!')
                open_new_tab(
                    'https://seamores.getbento.com/bentobox/developers/')
                print("Waiting. Have you connected your GitHub Account?")
                complete_flag = input(
                    "Type 'yes' to continue, or 'no' to cancel: ")
                if complete_flag != 'yes':
                    raise SystemExit
            else:
                token = get_token()
    return github_check


def check():
    create_user_structure(verbose=False)
    check_user(verbose=False)
