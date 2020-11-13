"""Console script for line_item_manager."""
from functools import partial
import json
import pkg_resources
import sys

import click
from googleads.errors import GoogleAdsServerFault
import yaml

from .config import config
from .create import create_line_items
from .exceptions import ResourceNotFound
from .validate import Validator
from .app_operations import CurrentNetwork

click.option = partial(click.option, show_default=True)

@click.group()
def cli():
    pass

@cli.command()
@click.argument('configfile', type=click.Path(exists=True))
@click.option('--network-code', type=int, help='GAM network code, must reconcile with the network name.')
@click.option('--network-name', help='GAM network name, must reconcile with the network code.')
@click.option('--private-key-file', '-k', required=True, default='gam_creds.json', type=click.Path(exists=True), help='Path to json GAM crendials file.')
@click.option('--single-order', '-s', is_flag=True, help='Create a single set of orders instead of orders per bidder.')
@click.option('--bidder-code', '-b', multiple=True, help='Bidder code, which may be used multiple times.')
@click.option('--test-run', '-t', is_flag=True, help='Execute a limited number of line_items for testing and manual review which will be auto-archived.')
@click.option('--dry-run', '-n', is_flag=True, help='Print commands that would be executed, but do not execute them.')
@click.option('--archive-on-failure', is_flag=True, help='If a GAM operation fails, auto-archive already completed operations.')
@click.option('--delete-on-failure', is_flag=True, help='If a GAM operation fails, auto-delete already completed operations.')
@click.pass_context
def create(ctx, configfile, **kwargs):
    """Create line items"""
    try:
        config.user_configfile = configfile
    except yaml.reader.ReaderError as e:
        raise click.UsageError(f'Check your configfile. {e}', ctx=ctx)

    config.cli = kwargs

    # validate CLI options
    if not kwargs['single_order'] and not kwargs['bidder_code']:
        raise click.UsageError('You must use --single-order or provide at least one --bidder-code', ctx=ctx)

    if kwargs['single_order'] and kwargs['bidder_code']:
        raise click.UsageError('Use of --single-order and --bidder-code is ambiguous and not allowed.', ctx=ctx)

    if not config.network_code:
        raise click.UsageError('Network code must be provided as an option or set in the config file', ctx=ctx)

    if not config.network_name:
        raise click.UsageError('Network name must be provided as an option or set in the config file', ctx=ctx)

    for bidder_code in kwargs['bidder_code']:
        if not bidder_code in config.bidder_data():
            raise click.UsageError(f'Bidder code \'{bidder_code}\' is not recognized', ctx=ctx)

    # validate GAM client
    try:
        config.client
    except json.decoder.JSONDecodeError:
        raise click.UsageError('Check your private key file. File is not formatted properly as json', ctx=ctx)
    except ValueError as e:
        raise click.UsageError(f'Check your private key file. {e.args[0]}', ctx=ctx)
    except Exception:
        raise click.UsageError(f'Check your private key file. Not able to successfully access your service account', ctx=ctx)

    # validate GAM network access
    try:
        name = CurrentNetwork().fetch()['displayName']
    except GoogleAdsServerFault:
        raise click.UsageError(f'Check your network code and permissions. Not able to successfully access your service account', ctx=ctx)
    if not name == config.network_name:
        raise click.UsageError(f"Network name found \'{name}\' does not match provided \'{config.network_name}\'", ctx=ctx)

    # validate user configuration
    user_cfg = Validator(config.schema, config.user)
    if not user_cfg.is_valid():
        err_str = '\n'.join([f'  - {user_cfg.fmt(_e)}' for _e in user_cfg.errors()])
        raise click.UsageError(f'Check your configfile for the following validation errors:\n{err_str}')

    # create line items
    try:
        create_line_items()
    except ResourceNotFound as _e:
        raise click.UsageError(f'Not able to find the following resource:\n  - {_e}', ctx=ctx)

@cli.command()
@click.argument('resource', type=click.Choice(['config', 'bidders']))
def show(resource):
    """Show resources"""
    if resource == 'config':
        config_file = pkg_resources.resource_filename('line_item_manager', 'conf.d/line_item_manager.yml')
        with open(config_file) as fp:
            print(fp.read())
    if resource == 'bidders':
        print("%-25s%s" % ('Code', 'Name'))
        print("%-25s%s" % ('----', '----'))
        for row in sorted(config.bidder_data().values(), key=lambda x: x['bidder-code']):
            print("%-25s%s" % (row['bidder-code'], row['bidder-name']))

def main():
    cli()

if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
