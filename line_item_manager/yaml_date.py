from datetime import datetime
from typing import Optional
import pytz
import yaml

YAML_TAG = u'!datetime_tz'

class DateTimeTZ(datetime):
    def __new__(cls, *args, **kwargs):
        return datetime.__new__(cls, *args, **kwargs)
    def __str__(self, include_tag=True):
        """Represent time zone name for encoding which is needed by googleads"""
        tag = f'{YAML_TAG} ' if include_tag else ''
        return f'{tag}{super().__str__()};{self.tzinfo.zone}'

def tz_constructor(loader: yaml.loader.SafeLoader, node: yaml.nodes.ScalarNode) -> datetime:
    dt_str, timezone = loader.construct_scalar(node).split(';')
    return datetime.fromisoformat(dt_str).replace(tzinfo=pytz.timezone(timezone))

def tz_representer(dumper: yaml.dumper.SafeDumper, data: DateTimeTZ) -> yaml.nodes.ScalarNode:
    return dumper.represent_scalar(YAML_TAG, f'{data.__str__(include_tag=False)}')

yaml.representer.SafeRepresenter.add_representer(DateTimeTZ, tz_representer)
yaml.constructor.SafeConstructor.add_constructor(YAML_TAG, tz_constructor)

def date_from_string(dtstr: str, fmt: str, timezone: str) -> Optional[DateTimeTZ]:
    """Get datetime object from a date string.

    Args:
      dtstr: input date string
      fmt: datetime format string
      timezone: time zone string

    Returns:
      A DateTimeTZ object if date string is provide else None
    """
    if not dtstr:
        return None
    dt = datetime.strptime(dtstr, fmt)
    return DateTimeTZ(dt.year, dt.month, dt.day, dt.hour, dt.minute).\
      replace(tzinfo=pytz.timezone(timezone))
