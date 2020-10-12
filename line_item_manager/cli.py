"""Console script for line_item_manager."""
from functools import partial
import sys
import click

click.option = partial(click.option, show_default=True)


@click.command()
@click.option('--network-code', required=True, type=int, help='GAM network code.')
@click.option('--private-key-file', '-k', required=True, default='gam_creds.json', type=click.Path(exists=True), help='Path to json GAM crendials file.')
@click.option('--single-order', '-s', is_flag=True, help='Create a single set of orders instead of orders per bidder.')
@click.option('--bidder-name', '-b', multiple=True, help='Bidder name, which may be used multiple times.')
@click.option('--default-config-file', help='Path to default configuration file, if not supplied module defaults are used.')
@click.option('--config-file', type=click.Path(exists=True), help='Path to configuration that overwrites the default configuration.')
@click.option('--test-run', '-t', is_flag=True, help='Execute a limited GAM setup for testing and manual review.')
@click.option('--dry-run', '-n', is_flag=True, help='Print commands that would be executed, but do not execute them.')
@click.pass_context
def main(ctx, **kwargs):
    """Console script for line_item_manager."""
    if not kwargs['single_order'] and not kwargs['bidder_name']:
        raise click.UsageError('You must use --single-order or provide at least one --bidder-name', ctx=ctx)
    if kwargs['single_order'] and kwargs['bidder_name']:
        raise click.UsageError('Use of --single-order and --bidder-name is ambiguous.', ctx=ctx)
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
