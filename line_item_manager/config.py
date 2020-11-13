import csv
from datetime import datetime
import pkg_resources
from urllib import request
import yaml

from googleads import ad_manager

class Config:

    _client = None
    _schema = None
    _bidder_data = None

    def __init__(self):
        self._app = self.load_package_file('settings.yml')
        self._start_time = datetime.now()

    @property
    def app(self):
        return self._app

    @property
    def cli(self):
        return self._cli

    @cli.setter
    def cli(self, obj):
        self._cli = obj

    @property
    def user(self):
        return self._user

    @property
    def start_time(self):
        return self._start_time

    @user.setter
    def user_configfile(self, filename):
        self._user = self.load_file(filename)

    @property
    def network_code(self):
        return self.cli['network_code'] or self.user.get('publisher', {}).get('network_code')

    @property
    def network_name(self):
        return self.cli['network_name'] or self.user.get('publisher', {}).get('network_name')

    @property
    def client(self):
        if self._client is None:
            _cfg = self.load_package_file('googleads.yaml')
            _cfg['ad_manager']['network_code'] = self.network_code
            _cfg['ad_manager']['path_to_private_key_file'] = self.cli['private_key_file']
            self._client = ad_manager.AdManagerClient.LoadFromString(yaml.dump(_cfg))
        return self._client

    @property
    def schema(self):
        if self._schema is None:
            self._schema = self.load_package_file('schema.yml')
        return self._schema

    def load_file(self, filename):
        with open(filename) as fp:
            return yaml.safe_load(fp)

    def load_package_file(self, filename):
        return self.load_file(pkg_resources.resource_filename('line_item_manager',
                                                              f'conf.d/{filename}'))
    def bidder_data(self):
        if self._bidder_data is None:
            reader = csv.DictReader([l.decode('utf-8') for l in request.urlopen(self.app['prebid']['bidders']['data']).readlines()])
            self._bidder_data = {row['bidder-code']:row for row in reader}
        return self._bidder_data

    def bidder_codes(self):
        if self.cli['single_order']:
            return [self.app['line_item_manager']['single_order']['bidder_code']]
        return self.cli['bidder_code']

    def bucket_cpm_names(self, bucket):
        rng = [int(100 * bucket[_k]) for _k in ('min', 'max', 'interval')]
        rng[1] += rng[2] # make stop inclusive
        return ['%.2f' % (_x / 100) for _x in range(*rng)]

    def cpm_names(self):
        names = []
        for bucket in self.user['rate']['cpm_buckets']:
            names += self.bucket_cpm_names(bucket)
        return names

    def custom_targeting_key_values(self):
        return [(_c['name'], set(_c['values'])) for _c in self.user['targeting'].get('custom', [])]

    def fmt_bidder_key(self, prefix, code):
        return f'{prefix}_{code}'[:self.app['prebid']['bidders']['key_char_limit']]

    def targeting_key(self, bidder_code):
        _map = self.user.get('bidder_key_map', {})
        prefix = self.app['prebid']['bidders']['targeting_key']
        if self.cli['single_order']:
            return _map.get(bidder_code, prefix)
        return _map.get(bidder_code, self.fmt_bidder_key(prefix, bidder_code))

config = Config()
