"""
Prompted activation of a targeting key by network code and targeting key name.
"""
import argparse
from pprint import pprint
from os import path

from line_item_manager.config import config
from line_item_manager.gam_operations import client as gam_client
from line_item_manager.operations import AppOperations, TargetingKey

class MyTargetingKey(AppOperations):
    service = 'CustomTargetingService'
    def activate(self) -> dict:
        return self.svc().performCustomTargetingKeyAction(
            {'xsi_type': 'ActivateCustomTargetingKeys'},
            self.statement().ToStatement()) # type: ignore[union-attr]

def file_exists(filename: str) -> str:
    if not path.exists(filename):
        raise argparse.ArgumentTypeError('Private key file does not exist.')
    return filename

def is_yes(question: str, answer=None) -> bool:
    while answer not in {'y', 'n'}:
        answer = input(f"{question}? (y/n) ").lower()
    return answer == 'y'

def activate() -> None:
    args = cli_args()
    config.cli = dict(
        network_code=args.network_code,
        private_key_file=args.private_key_file
    )
    config.set_client_factory(gam_client)

    tgt_key = TargetingKey(name=args.name).fetchone()
    if not tgt_key:
        print('Targeting key not found. Exiting.')
        return
    if args.verbose:
        pprint(tgt_key)
    if tgt_key['status'] == 'ACTIVE':
        print('Targeting key is already ACTIVE. Exiting.')
        return
    print(f"Targeting key: id={tgt_key['id']}, name={tgt_key['name']}, type={tgt_key['type']}")
    if is_yes('Activate', answer='y' if args.yes else None):
        print('Activating...')
        pprint(MyTargetingKey(id=[tgt_key['id']]).activate())
    print('Exiting.')

def cli_args():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('network_code', type=int, help='GAM network code.')
    parser.add_argument('name', help='Targeting key name')
    parser.add_argument('-k', '--private_key_file', default='gam_creds.json', type=file_exists,
                        help='Path to json GAM credentials file.')
    parser.add_argument('-y', '--yes', action='store_true', help='Archive without prompting.')
    parser.add_argument('-v', '--verbose', action='store_true', help='Show full object')
    return parser.parse_args()

def main() -> None:
    activate()

if __name__ == '__main__':
    main()
