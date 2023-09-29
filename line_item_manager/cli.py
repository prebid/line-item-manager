"""Console script for line_item_manager."""
from functools import partial
import json
import pkg_resources
import sys

import click
from googleads.errors import GoogleAdsError
import yaml

from . import version as VERSION
from .config import config
from .exceptions import ResourceNotActive, ResourceNotFound
from .gam_config import GAMConfig
from .gam_operations import client as gam_client
from .prebid import prebid, PrebidBidder
from .validate import Validator

click.option = partial(click.option, show_default=True)

logger = config.getLogger(__name__)

@click.group(invoke_without_command=True)
@click.option('--version', is_flag=True, help='Print version information and exit.')
@click.pass_context
def cli(ctx: click.core.Context, version: bool) -> None:
    if version:
        print(f'line-item-manager version {VERSION}')
        return
    if not ctx.invoked_subcommand:
        click.echo(cli.get_help(ctx))

@cli.command()
@click.argument('configfile', type=click.Path(exists=True))
@click.option('--network-code', type=int,
              help='GAM network code, must reconcile with the network name.')
@click.option('--network-name', help='GAM network name, must reconcile with the network code.')
@click.option('--private-key-file', '-k', required=True, default='gam_creds.json',
              type=click.Path(exists=True), help='Path to json GAM credentials file.')
@click.option('--template',
              type=click.Path(exists=True), help='Advanced users: path to custom line item template. ' \
              'Use "line_item_manager show template" to see the package default')
@click.option('--settings',
              type=click.Path(exists=True), help='Advanced users: path to settings file. ' \
              'Use "line_item_manager show settings" to see the package default')
@click.option('--schema',
              type=click.Path(exists=True), help='Advanced users: path to schema file. ' \
              'Use "line_item_manager show schema" to see the package default')
@click.option('--single-order', '-s', is_flag=True,
              help='Create a single set of orders instead of orders per bidder.')
@click.option('--bidder-code', '-b', multiple=True,
              help='Bidder code, may be used multiple times.')
@click.option('--test-run', '-t', is_flag=True,
              help='Create a limited number of line_items for testing and review in GAM. ' \
              'Order and line item names are prepended with \'Test: \'.')
@click.option('--dry-run', '-n', is_flag=True,
              help='Print commands that would be executed, but do not execute them.')
@click.option('--quiet', '-q', is_flag=True, help='Logging is limited to warnings and errors.')
@click.option('--verbose', '-v', multiple=True, is_flag=True,
              help='Verbose logging, use multiple times to increase verbosity.')
@click.option('--skip-auto-archive', is_flag=True,
              help='Upon failure or interruption, do NOT auto-archive already created orders.')
@click.pass_context
def create(ctx: click.core.Context, configfile: str, **kwargs):
    """Create line items"""
    config.cli = kwargs

    try:
        config.set_user_configfile(configfile)
    except yaml.YAMLError as e:
        raise click.UsageError(f'Check your configfile. {e}', ctx=ctx)

    gam = GAMConfig()

    # validate CLI options
    if not kwargs['single_order'] and not kwargs['bidder_code']:
        raise click.UsageError(
            'You must use --single-order or provide at least one --bidder-code', ctx=ctx)

    if kwargs['single_order'] and kwargs['bidder_code']:
        raise click.UsageError(
            'Use of --single-order and --bidder-code is ambiguous and not allowed.', ctx=ctx)

    if not config.network_code:
        raise click.UsageError(
            'Network code must be provided as an option or set in the config file', ctx=ctx)

    if not config.network_name:
        raise click.UsageError(
            'Network name must be provided as an option or set in the config file', ctx=ctx)

    for bidder_code in kwargs['bidder_code']:
        if not bidder_code in prebid.bidders:
            raise click.UsageError(f'Bidder code \'{bidder_code}\' is not recognized', ctx=ctx)

    # validate GAM client
    config.set_client_factory(gam_client)
    try:
        config.client
    except json.decoder.JSONDecodeError as e:
        raise click.UsageError(
            'Check your private key file. File is not formatted properly as json', ctx=ctx)
    except ValueError as e:
        raise click.UsageError(f'Check your private key file. {e.args[0]}', ctx=ctx)
    except Exception as e:
        raise click.UsageError('Check your private key file. Not able to successfully ' \
                               'access your service account', ctx=ctx)

    # validate GAM network access
    try:
        if not gam.network['displayName'] == config.network_name:
            raise click.UsageError(f"Network name found \'{gam.network['displayName']}\' " \
                                   f"does not match provided \'{config.network_name}\'", ctx=ctx)
    except GoogleAdsError as _e:
        logger.error(f'GoogleAdsError, {_e}')
        raise click.UsageError(
            'Not able to successfully access your service account.  ' \
            'Check WARNING/ERROR messages above and consider \nupgrading to latest version.', ctx=ctx)

    # validate user configuration
    user_cfg = Validator(config.schema, config.user)
    if not user_cfg.is_valid():
        err_str = '\n'.join([f'  - {user_cfg.fmt(_e)}' for _e in user_cfg.errors()])
        raise click.UsageError(f'Check your configfile for the following validation ' \
                               f'errors:\n{err_str}', ctx=ctx)
    try:
        PrebidBidder.validate_override_map(config.user.get('bidder_key_map'))
    except ValueError as e:
        raise click.UsageError(f'{e}', ctx=ctx)

    # pre-create line items config
    try:
        config.pre_create()
    except ValueError as e:
        raise click.UsageError(f'{e}', ctx=ctx)

    # create line items
    try:
        gam.create_line_items()
        gam.success = True
    except ResourceNotActive as _e:
        logger.error('Resource is not active:\n  - %s', _e)
    except ResourceNotFound as _e:
        logger.error('Not able to find the following resource:\n  - %s', _e)
    except GoogleAdsError as _e:
        logger.error('Google Ads Error, %s', _e)
    except ValueError as _e:
        logger.error('Unexpected result, %s', _e)
    except KeyboardInterrupt:
        logger.warning('User Interrupt')
    finally:
        try:
            gam.cleanup()
        except GoogleAdsError as _e:
            logger.error('Cleanup: Google Ads Error, %s', _e)

def show_resource(filename: str) -> None:
    rsrc_name = pkg_resources.resource_filename('line_item_manager', filename) # type: ignore[misc]
    with open(rsrc_name) as fp:
        print(fp.read())

@cli.command()
@click.argument('resource', type=click.Choice(['config', 'bidders', 'template',
                                               'settings', 'schema']))
def show(resource: str) -> None:
    """Show resources"""
    if resource == 'config':
        show_resource('conf.d/line_item_manager.yml')
    if resource == 'template':
        show_resource('conf.d/line_item_template.yml')
    if resource == 'settings':
        show_resource('conf.d/settings.yml')
    if resource == 'schema':
        show_resource('conf.d/schema.yml')
    if resource == 'bidders':
        print("%-25s%s" % ('Code', 'Name'))
        print("%-25s%s" % ('----', '----'))
        for row in sorted(prebid.bidders.values(), key=lambda x: x['bidder-code']):
            print("%-25s%s" % (row['bidder-code'], row['bidder-name']))

def main():
    cli() # pylint: disable=no-value-for-parameter

if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
