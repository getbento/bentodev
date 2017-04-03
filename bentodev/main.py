import click
from .setup import setup


@click.group()
@click.version_option()
def cli():
    """BentoDev
    Used to develop themes locally for BentoBox sites!
    """
    setup()

######################################################


@cli.command('config')
@click.argument('arg')
@click.option('--option', metavar='KN', default=10,
              help='full option')
def config(arg, option):
    """Base configuration"""
    click.echo('Testing config %s %s' % (arg, option))


######################################################


@cli.command('list')
def list():
    """List accounts and themes you have access too."""
    click.echo('list list list')

#####################################################


@cli.command('start')
@click.option('--site', default='seamores')
def start(site):
    """Begin running the development server"""
    click.echo('runserver at %s.localdev.me:8000' % (site))
