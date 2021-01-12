from datetime import datetime
import logging
from typing import Callable, Dict, List, Iterable, Optional, Tuple, Union
import pytz

from googleads import ad_manager

from .utils import date_from_string, values_from_bucket, ichunk, load_file, \
     load_package_file

logging.basicConfig()

VERBOSE1: int = logging.INFO - 1
VERBOSE2: int = logging.INFO - 2

class Config:

    def __init__(self):
        self._schema = None
        self._cpm_names = None
        self._app = load_package_file('settings.yml')
        self._start_time = datetime.now()
        self.set_logger()

    def isLoggingEnabled(self, level: int) -> bool:
        return self._logger.getEffectiveLevel() <= level

    def set_logger(self) -> None:
        self._logger = logging.getLogger(__package__)
        self._logger.setLevel(logging.INFO)
        logging.addLevelName(VERBOSE1, 'VERBOSE1')
        logging.addLevelName(VERBOSE2, 'VERBOSE2')

    def getLogger(self, name: str) -> logging.Logger:
        return self._logger.getChild(name.split('.')[-1])

    def set_log_level(self) -> None:
        if self.cli['verbose']:
            self._logger.setLevel(logging.INFO - len(self.cli['verbose']))
        if self.cli['quiet']:
            self._logger.setLevel(logging.WARNING)

    @property
    def app(self) -> dict:
        return self._app

    @property
    def cli(self) -> dict:
        return self._cli

    @cli.setter
    def cli(self, obj) -> None:
        self._cli = obj
        self._client = None
        self.set_log_level()

    @property
    def client(self) -> Optional[ad_manager.AdManagerClient]:
        if self._client is None:
            self._client = self._client_factory(self.network_code, self.cli['private_key_file'])
        return self._client

    @property
    def user(self) -> dict:
        return self._user

    def set_client_factory(self, factory: Callable) -> None:
        self._client = None
        self._client_factory = factory

    def set_user_configfile(self, filename: str) -> None:
        self._user = load_file(filename)
        self._client = None
        self._cpm_names = None

    @property
    def start_time(self) -> datetime:
        return self._start_time

    @property
    def network_code(self) -> int:
        return self.cli['network_code'] or self.user.get('publisher', {}).get('network_code')

    @property
    def network_name(self) -> str:
        return self.cli['network_name'] or self.user.get('publisher', {}).get('network_name')

    @property
    def schema(self) -> dict:
        if self._schema is None:
            self._schema = load_package_file('schema.yml')
        return self._schema

    def bidder_codes(self) -> List[str]:
        if self.cli['single_order']:
            return [self.app['prebid']['bidders']['single_order']['code']]
        return self.cli['bidder_code']

    def media_types(self) -> List[str]:
        return [m_ for m_ in ('video', 'banner') if self.user['creative'].get(m_)]

    def custom_targeting_key_values(self) -> List[Tuple[str, set]]:
        return [(_c['name'], set(_c['values'])) \
                for _c in self.user.get('targeting', {}).get('custom', [])]

    def cpm_buckets(self) -> List[Dict[str, float]]:
        _type = self.user['rate']['granularity']['type']
        if _type == "custom":
            return self.user['rate']['granularity']['custom']
        return self.app['prebid']['price_granularity'][_type]

    def cpm_names(self) -> List[str]:
        if self._cpm_names is None:
            values = set()
            for bucket in self.cpm_buckets():
                values.update(values_from_bucket(bucket))
            self._cpm_names = ['%.2f' % v_ for v_ in sorted(values)]
        if self.cli['test_run']:
            return self._cpm_names[:self.app['mgr']['test_run']['line_item_limit']]
        return self._cpm_names

    def cpm_names_batched(self) -> Iterable[List[str]]:
        return ichunk(self.cpm_names(), self.app['googleads']['line_items']['max_per_order'])

    def micro_amount(self, cpm: Union[str, float]) -> int:
        return int(float(cpm) * self.app['googleads']['line_items']['micro_cent_factor'])

    def pre_create(self) -> None:
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
            raise ValueError(f'Unknown Time Zone, {e}') from e

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
