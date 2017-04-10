import json
import os
from webbrowser import open_new_tab

from getpass import getpass
from shutil import copy2
from .factory import TokenRequest, VerifyRequest, GitHubAccountRequest


home_dir = os.path.expanduser('~')
bentodev_dir = home_dir + '/bentodev/'
user_config = bentodev_dir + 'config.json'
sites_dir = bentodev_dir + 'sites/'


def create_user_structure(verbose):
    if not os.path.exists(home_dir):
        if verbose:
            print('No home directory. Exiting gracefully.')
        raise SystemExit
    if not os.path.exists(bentodev_dir):
        if verbose:
            print("Creating ~/bentodev/ ...")
        os.makedirs(bentodev_dir)
    if not os.path.exists(sites_dir):
        if verbose:
            print("Creating ~/bentodev/sites/ ...")
        os.makedirs(sites_dir)
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
    r = TokenRequest(data={'email': user, 'password': pw})
    r.post()
    del pw
    token = ''
    if r.json()['token']:
        token = r.json()['token']
    if verify_token(token):
        return token


def verify_token(token):
    r = VerifyRequest(data={'token': token})
    r.post()
    if not r.request.ok:
        print('Token Expired')
        return False
    return True


def get_token():
    global_config = os.path.dirname(os.path.realpath(__file__)) + '/config.json'
    config_file = open(global_config, "r")
    config_data = json.load(config_file)
    config_file.close()
    token = ''
    while not token:
        if not config_data['BENTOBOX_TOKEN']:
            config_data['BENTOBOX_TOKEN'] = token_auth()
            with open(global_config, "w") as config_file:
                json.dump(config_data, config_file, sort_keys=True, indent=4)
            config_file.close()
        elif not verify_token(config_data['BENTOBOX_TOKEN']):
            config_data['BENTOBOX_TOKEN'] = ''
        else:
            token = config_data['BENTOBOX_TOKEN']
    return token


def github_account(token, verbose=True):
    github_check = False
    while not github_check:
        if token:
            r = GitHubAccountRequest(token=token)
            r.get()
            if r.request.ok and r.json() and verbose:
                print('Connected to GitHub Account: {}'.format(str(r.json()[0]['username'])))
                github_check = True
            elif r.ok and not r.json():
                print('You have not connected your GitHub!')
                print('Opening BentoBox Admin to Connect GitHub Account!')
                open_new_tab('http://seamores.localtest.me:8000/bentobox/developers/')
                print("Waiting. Have you connected your GitHub Account?")
                complete_flag = input("Type 'yes' to continue, or 'no' to cancel: ")
                if complete_flag != 'yes':
                    raise SystemExit
    return github_check


def check():
    create_user_structure(verbose=False)
    check_user(verbose=False)
