import csv
from datetime import datetime
import logging
import pkg_resources
import pytz
from urllib import request
import yaml

from googleads import ad_manager

from .utils import date_from_string

logging.basicConfig()

class Config:

    _client = None
    _schema = None
    _bidder_data = None
    _cpm_names = None

    def __init__(self):
        self._app = self.load_package_file('settings.yml')
        self._start_time = datetime.now()
        self._logger = logging.getLogger(__package__)
        self._logger.setLevel(logging.INFO)
        self._dry_id = 8000000

    def new_dry_id(self):
        self._dry_id += 1
        return self._dry_id

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

    def set_user_configfile(self, filename):
        self._user = self.load_file(filename)

    @property
    def start_time(self):
        return self._start_time

    def getLogger(self, name):
        return self._logger.getChild(name.split('.')[-1])

    def verbose(self):
        self._logger.setLevel(logging.DEBUG)

    def quiet(self):
        self._logger.setLevel(logging.WARNING)

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

    def package_filename(self, name):
        return pkg_resources.resource_filename('line_item_manager', f'conf.d/{name}')

    def load_package_file(self, name):
        return self.load_file(self.package_filename(name))

    def bidder_data(self):
        if self._bidder_data is None:
            reader = csv.DictReader([l.decode('utf-8') for l in \
                request.urlopen(self.app['prebid']['bidders']['data']).readlines()])
            self._bidder_data = {row['bidder-code']:row for row in reader}
        return self._bidder_data

    def bidder_codes(self):
        if self.cli['single_order']:
            return [self.app['line_item_manager']['single_order']['bidder_code']]
        return self.cli['bidder_code']

    def bucket_cpm_values(self, bucket):
        rng = [int(100 * bucket[_k]) for _k in ('min', 'max', 'interval')]
        rng[1] += rng[2] # make stop inclusive
        return {_x / 100 for _x in range(*rng)}

    def cpm_names(self):
        if self._cpm_names is None:
            values = set()
            for bucket in self.user['rate']['cpm_buckets']:
                values.update(self.bucket_cpm_values(bucket))
            self._cpm_names = ['%.2f' % v_ for v_ in sorted(values)]
        return self._cpm_names

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

    def pre_create(self):
        li_ = self.user['line_item']
        is_standard = li_['item_type'].upper() == "STANDARD"
        end_str = li_.get('end_datetime')
        start_str = li_.get('start_datetime')
        fmt = self.app['line_item_manager']['date_fmt']
        vcpm = self.user['rate'].get('vcpm')

        try:
            tz_str = li_.get('timezone', self.app['line_item_manager']['timezone'])
            _ = pytz.timezone(tz_str)
        except pytz.exceptions.UnknownTimeZoneError as e:
            raise ValueError(f'Unknown Time Zone, {e}')

        if vcpm and not is_standard:
            raise ValueError("Specifying 'vcpm' requires using line item type 'standard'")

        if is_standard and not end_str:
            raise ValueError("No end date specified when using line item type 'standard'")

        li_.update(dict(
            start_dt=date_from_string(start_str, fmt, tz_str) if start_str else "IMMEDIATELY",
            start_dt_type="USE_START_DATE_TIME" if start_str else "IMMEDIATELY",
            end_dt=date_from_string(end_str, fmt, tz_str),
            unlimited_end_dt=not end_str,
        ))

        li_.update({'goal': dict(
            goalType="NONE",
        )})

        if vcpm:
            li_.update({'goal': dict(
                goalType="LIFETIME",
                unitType="VIEWABLE_IMPRESSIONS",
                units=vcpm,
            )})

        self.user['rate'].update(dict(
            cost_type="VCPM" if vcpm else "CPM"
        ))

config = Config()
