import csv
from datetime import datetime
import logging
import pkg_resources
import pytz
from urllib import request
import yaml

from googleads import ad_manager

from .utils import date_from_string, values_from_bucket, ichunk

logging.basicConfig()

VERBOSE1 = logging.INFO - 1
VERBOSE2 = logging.INFO - 2

class Config:

    _client = None
    _schema = None
    _bidder_data = None
    _cpm_names = None

    def __init__(self):
        self._app = self.load_package_file('settings.yml')
        self._start_time = datetime.now()
        self.set_logger()

    def isLoggingEnabled(self, level):
        return self._logger.getEffectiveLevel() <= level

    def set_logger(self):
        self._logger = logging.getLogger(__package__)
        self._logger.setLevel(logging.INFO)
        logging.addLevelName(VERBOSE1, 'VERBOSE1')
        logging.addLevelName(VERBOSE2, 'VERBOSE2')

    def getLogger(self, name):
        return self._logger.getChild(name.split('.')[-1])

    def set_log_level(self):
        if self.cli['verbose']:
            self._logger.setLevel(logging.INFO - len(self.cli['verbose']))
        if self.cli['quiet']:
            self._logger.setLevel(logging.WARNING)

    @property
    def app(self):
        return self._app

    @property
    def cli(self):
        return self._cli

    @cli.setter
    def cli(self, obj):
        self._cli = obj
        self._client = None
        self.set_log_level()

    @property
    def user(self):
        return self._user

    def set_user_configfile(self, filename):
        self._user = self.load_file(filename)
        self._cpm_names = None

    @property
    def start_time(self):
        return self._start_time

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

    def read_package_file(self, name):
        with open(self.package_filename(name)) as fp:
            return fp.read()

    def bidder_name(self, code):
        if self.cli['single_order']:
            return self.app['mgr']['single_order']['bidder_name']
        return self.bidder_data()[code]['bidder-name']

    def bidder_data(self):
        if self._bidder_data is None:
            reader = csv.DictReader([l.decode('utf-8') for l in \
                request.urlopen(self.app['prebid']['bidders']['data']).readlines()])
            self._bidder_data = {row['bidder-code']:row for row in reader}
        return self._bidder_data

    def bidder_codes(self):
        if self.cli['single_order']:
            return [self.app['mgr']['single_order']['bidder_code']]
        return self.cli['bidder_code']

    def media_types(self):
        return [m_ for m_ in ('video', 'banner') if self.user['creative'].get(m_)]

    def cpm_buckets(self):
        _type = self.user['rate']['granularity']['type']
        if _type == "custom":
            return self.user['rate']['granularity']['custom']
        return self.app['prebid']['price_granularity'][_type]

    def cpm_names(self):
        if self._cpm_names is None:
            values = set()
            for bucket in self.cpm_buckets():
                values.update(values_from_bucket(bucket))
            self._cpm_names = ['%.2f' % v_ for v_ in sorted(values)]
        if self.cli['test_run']:
            return self._cpm_names[:self.app['mgr']['test_run']['line_item_limit']]
        return self._cpm_names

    def cpm_names_batched(self):
        return ichunk(self.cpm_names(), self.app['googleads']['line_items']['max_per_order'])

    def custom_targeting_key_values(self):
        return [(_c['name'], set(_c['values'])) for _c in self.user.get('targeting', {}).get('custom', [])]

    def bidder_codestr(self, code):
        return '' if self.cli['single_order'] else code

    def bidder_params(self, code):
        _map = self.user.get('bidder_key_map', {}).get(code, {})
        codestr = self.bidder_codestr(code)
        return {k:_map.get(k, self.fmt_bidder_key(k, codestr))
                for k in self.app['prebid']['bidders']['keys']}

    def fmt_bidder_key(self, prefix, code):
        if not code:
            return prefix
        return f'{prefix}_{code}'[:self.app['prebid']['bidders']['key_char_limit']]

    def targeting_key(self, code):
        return self.bidder_params(code)[self.app['prebid']['bidders']['targeting_key']]

    def micro_amount(self, cpm):
        return int(float(cpm) * self.app['googleads']['line_items']['micro_cent_factor'])

    def validate_bidder_key_map(self):
        key_map = self.user.get('bidder_key_map')
        if not key_map:
            return
        valid_properties = set(self.bidder_data().keys())
        valid_properties.add(self.app['prebid']['bidders']['targeting_key'])
        if not set(key_map.keys()).issubset(valid_properties):
            raise ValueError(f"'bidder_key_map' properties, {set(key_map.keys())} must be valid bidder codes")
        valid_keys = set(self.app['prebid']['bidders']['keys'])
        for k, v in key_map.items():
            if not set(v.keys()).issubset(valid_keys):
                raise ValueError(f"'bidder_key_map' properties, {set(v.keys())}, for '{k}' must be valid bidder keys")

    def pre_create(self):
        li_ = self.user['line_item']
        is_standard = li_['item_type'].upper() == "STANDARD"
        end_str = li_.get('end_datetime')
        start_str = li_.get('start_datetime')
        fmt = self.app['mgr']['date_fmt']
        vcpm = self.user['rate'].get('vcpm')

        if vcpm and not is_standard:
            raise ValueError("Specifying 'vcpm' requires using line item type 'standard'")

        try:
            tz_str = li_.get('timezone', self.app['mgr']['timezone'])
            _ = pytz.timezone(tz_str)
        except pytz.exceptions.UnknownTimeZoneError as e:
            raise ValueError(f'Unknown Time Zone, {e}')

        for i_ in ('line_item', 'order'):
            self.user[i_]['name'] = ''.join(['{{ run_mode }}', self.user[i_]['name']])

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
