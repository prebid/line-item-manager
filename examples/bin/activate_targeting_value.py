"""
Prompted activation of a targeting value by network code and targeting key name.
"""
import argparse
from pprint import pprint
from os import path

from line_item_manager.config import config
from line_item_manager.gam_operations import client as gam_client
from line_item_manager.operations import AppOperations, TargetingValues

class MyTargetingValue(AppOperations):
    service = 'CustomTargetingService'
    def activate(self) -> dict:
        return self.svc().performCustomTargetingValueAction(
            {'xsi_type': 'ActivateCustomTargetingValues'},
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

    for _v in args.names:
        tgt_value = TargetingValues(key_id=args.targeting_key_id, name=_v).fetchone()
        if not tgt_value:
            print('Targeting value not found. Exiting.')
            continue
        if args.verbose:
            pprint(tgt_value)
        if tgt_value['status'] == 'ACTIVE':
            print('Targeting value is already ACTIVE. Exiting.')
            continue
        print(f"Targeting value: id={tgt_value['id']}, name={tgt_value['name']}")
        if is_yes('Activate', answer='y' if args.yes else None):
            print('Activating...')
            pprint(MyTargetingValue(id=[tgt_value['id']]).activate())
    print('Exiting.')

def cli_args():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('network_code', type=int, help='GAM network code.')
    parser.add_argument('targeting_key_id', help='Targeting Key Id')
    parser.add_argument('names', nargs='+', help='Targeting value names')
    parser.add_argument('-k', '--private_key_file', default='gam_creds.json', type=file_exists,
                        help='Path to json GAM credentials file.')
    parser.add_argument('-y', '--yes', action='store_true', help='Archive without prompting.')
    parser.add_argument('-v', '--verbose', action='store_true', help='Show full object')
    return parser.parse_args()

def main() -> None:
    activate()

if __name__ == '__main__':
    main()
