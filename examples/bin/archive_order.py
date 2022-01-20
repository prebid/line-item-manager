"""
Prompted archival of an order by network code and order id.
"""
import argparse
from pprint import pprint
from os import path

from line_item_manager.config import config
from line_item_manager.gam_operations import client as gam_client
from line_item_manager.operations import Order

def file_exists(filename: str) -> str:
    if not path.exists(filename):
        raise argparse.ArgumentTypeError('Private key file does not exist.')
    return filename

def is_yes(question: str, answer=None) -> bool:
    while answer not in {'y', 'n'}:
        answer = input(f"{question}? (y/n) ").lower()
    return answer == 'y'

def archive() -> None:
    args = cli_args()
    config.cli = dict(
        network_code=args.network_code,
        private_key_file=args.private_key_file
    )
    config.set_client_factory(gam_client)

    order = Order(id=args.id).fetchone()
    if not order:
        print('Order not found. Exiting.')
        return
    if args.verbose:
        pprint(order)
    if order['isArchived']:
        print('Order is already archived. Exiting.')
        return
    print(f"Order: {order['name']}")
    if is_yes('Archive', answer='y' if args.yes else None):
        print('Archiving...')
        pprint(Order(id=[args.id]).archive())
    print('Exiting.')

def cli_args():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('network_code', type=int, help='GAM network code.')
    parser.add_argument('id', help='Order Id.')
    parser.add_argument('-k', '--private_key_file', default='gam_creds.json', type=file_exists,
                        help='Path to json GAM credentials file.')
    parser.add_argument('-y', '--yes', action='store_true', help='Archive without prompting.')
    parser.add_argument('-v', '--verbose', action='store_true', help='Show full object')
    return parser.parse_args()

def main() -> None:
    archive()

if __name__ == '__main__':
    main()
