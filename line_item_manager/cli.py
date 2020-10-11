"""Console script for line_item_manager."""
from functools import partial
import sys
import click

click.option = partial(click.option, show_default=True)

@click.command()
@click.option('--network-code', required=True, type=int, help='GAM network code.')
@click.option('--private-key-file', '-k', required=True, default='gam_creds.json', type=click.Path(exists=True), help='Path to json GAM crendials file.')
@click.option('--bidder-name', '-b', required=True, multiple=True, help='Bidder name, which may be used multiple times.')
@click.option('--default-config-file', help='Path to default configuration file, if not supplied module defaults are used.')
@click.option('--config-file', type=click.Path(exists=True), help='Path to configuration that overwrites the default configuration.')
@click.option('--test-run', '-t', is_flag=True, help='Execute a limited GAM setup for testing and manual review.')
@click.option('--dry-run', '-n', is_flag=True, help='Print commands that would be executed, but do not execute them.')
def main(*args, **kwargs):
    """Console script for line_item_manager."""
    click.echo("See click documentation at https://click.palletsprojects.com/")
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
