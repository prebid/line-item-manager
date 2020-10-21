"""Console script for line_item_manager."""
import csv
from functools import partial
import pkg_resources
from urllib import request
import sys

import click
import yaml

click.option = partial(click.option, show_default=True)

with open(pkg_resources.resource_filename('line_item_manager', 'conf.d/settings.yml')) as fp:
    settings = yaml.safe_load(fp)

@click.group()
def cli():
    pass

@cli.command()
@click.argument('configfile', type=click.Path(exists=True))
@click.option('--network-code', required=True, type=int, help='GAM network code, must reconcile with the network name.')
@click.option('--network-name', required=True, help='GAM network name, must reconcile with the network code.')
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
    if not kwargs['single_order'] and not kwargs['bidder_code']:
        raise click.UsageError('You must use --single-order or provide at least one --bidder-code', ctx=ctx)
    if kwargs['single_order'] and kwargs['bidder_code']:
        raise click.UsageError('Use of --single-order and --bidder-code is ambiguous.', ctx=ctx)
    return 0

@cli.command()
@click.argument('resource', type=click.Choice(['config', 'bidders']))
def show(resource):
    """Show resources"""
    if resource == 'config':
        config_file = pkg_resources.resource_filename('line_item_manager', 'conf.d/line_item_manager.yml')
        with open(config_file) as fp:
            print(fp.read())
    if resource == 'bidders':
        reader = csv.DictReader([l.decode('utf-8') for l in request.urlopen(settings['bidders']['data']).readlines()])
        print("%-25s%s" % ('Code', 'Name'))
        print("%-25s%s" % ('----', '----'))
        for row in reader:
            print("%-25s%s" % (row['bidder-code'], row['bidder-name']))

def main():
    cli()

if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
