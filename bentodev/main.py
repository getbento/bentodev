import click
from .command_functions import get_repo_list
from .setup import check, check_user, create_user_structure, token_auth


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
    token = token_auth()
    get_repo_list(token)

#####################################################


@cli.command('start')
@click.option('--site', default='seamores')
def start(site):
    """Begin running the development server"""
    click.echo('runserver at %s.localdev.me:8000' % (site))
