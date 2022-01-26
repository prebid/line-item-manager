"""
Get and display Google Ad Manager resources.
"""
import argparse
from pprint import pprint
from os import path

from line_item_manager.config import config
from line_item_manager.gam_operations import client as gam_client
from line_item_manager.operations import Advertiser, AdUnit, Placement, Order, CurrentNetwork, \
     CurrentUser, Creative, TargetingKey

RESOURCES = dict(
    ad_unit=AdUnit,
    advertiser=Advertiser,
    placement=Placement,
    order=Order,
    network=CurrentNetwork,
    user=CurrentUser,
    creative=Creative,
    targeting_key=TargetingKey,
)

def fetch():
    args = cli_args()
    config.cli = dict(
        network_code=args.network_code,
        private_key_file=args.private_key_file
    )
    config.set_client_factory(gam_client)

    params = {}
    if args.id:
        params = dict(id=args.id)
    if args.name:
        params = dict(name=args.name)
    op = RESOURCES[args.resource]
    if op.use_statement:
        return [i_ if args.verbose else {'id': i_['id'], 'name': i_['name']}
                for i_ in op(**params).fetch()]
    return op(**params).fetchone()

def file_exists(filename) -> str:
    if not path.exists(filename):
        raise argparse.ArgumentTypeError('Private key file does not exist.')
    return filename

def cli_args():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('network_code', type=int, help='GAM network code.')
    parser.add_argument('resource', choices=RESOURCES.keys(), help='GAM resource.')
    parser.add_argument('-k', '--private_key_file', default='gam_creds.json', type=file_exists,
                        help='Path to json GAM credentials file.')
    parser.add_argument('--id', help='Resource Id.')
    parser.add_argument('--name', help='Resouce Name.')
    parser.add_argument('-v', '--verbose', action='store_true', help='Show full object')
    return parser.parse_args()

def main() -> None:
    pprint(fetch())

if __name__ == '__main__':
    main()
