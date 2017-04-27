import click
from bentodev.command_functions import (
    get_theme,
    clone_repo,
    run_flask,
    list_accounts,
    ListFlags)
from bentodev.utils import check, check_user, create_user_structure, get_token
import os


@click.group()
@click.version_option()
@click.option('--local', is_flag=True)
def cli(local):
    """BentoDev
    Used to develop themes locally for BentoBox sites!
    """
    os.environ['ENVIRON'] = 'production'
    if local:
        os.environ['ENVIRON'] = 'local'
    check()
######################################################


@cli.command('config')
@click.option('--username')
def config(username):
    """Base configuration"""
    if username:
        create_user_structure(verbose=False)
        check_user(verbose=False, username=username)
    else:
        check()

######################################################


@cli.command('list')
def list():
    """List accounts and themes you have access too."""
    token = get_token()
    list_accounts(token)

#####################################################


@cli.command('clone')
@click.argument('slug', required=False)
def clone(slug):
    """Clone an account you have access too."""
    token = get_token()
    if slug:
        clone_repo(token, slug)
    else:
        list_accounts(token, ListFlags.CLONE)

#####################################################


@cli.command('start')
@click.argument('account', required=False)
def start(account):
    """Begin running the development server"""
    token = get_token()
    if account:
        repo = get_theme(token, account)
        run_flask(account, repo)
    else:
        list_accounts(token, ListFlags.START)
