import os
import click
from .command_functions import get_repo_list, clone_repo, run_flask, list_accounts, get_theme
from .utils import check, check_user, create_user_structure, get_token
from flask.cli import FlaskGroup


@click.group()
@click.version_option()
def cli():
    """BentoDev
    Used to develop themes locally for BentoBox sites!
    """
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
@click.argument('slug')
def clone(slug):
    """Clone an account you have access too."""
    token = get_token()
    clone_repo(token, slug)

#####################################################


@cli.command('start')
@click.argument('account', required=False)
def start(account):
    """Begin running the development server"""
    # click.echo('runserver at %s.localdev.me:8000' % (site))
    token = get_token()
    if account:
        repo = get_theme(token, account)
        run_flask(account, repo)
    else:
        list_accounts(token)
