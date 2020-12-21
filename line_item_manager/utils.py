from datetime import datetime
from hashlib import sha1
import pkg_resources
from pprint import pformat
import pytz
from typing import Any, Dict, Iterable, Optional

import yaml

def load_file(filename: str) -> dict:
    with open(filename) as fp:
        return yaml.safe_load(fp)

def load_package_file(name: str) -> dict:
    return load_file(package_filename(name))

def package_filename(name: str) -> str:
    return pkg_resources.resource_filename('line_item_manager', f'conf.d/{name}')

def read_package_file(name: str) -> str:
    with open(package_filename(name)) as fp:
        return fp.read()

def num_hash(obj: Any, digits: int=6) -> int:
    return int(sha1(str(obj).encode('utf-8')).hexdigest(), 16) % 10**digits

def values_from_bucket(bucket: Dict[str, float]) -> set:
    rng = [int(100 * bucket[_k]) for _k in ('min', 'max', 'interval')]
    rng[1] += rng[2] # make stop inclusive
    return {_x / 100 for _x in range(*rng)}

def date_from_string(dtstr: str, fmt: str, timezone: str) -> Optional[datetime]:
    if not dtstr:
        return None
    return datetime.strptime(dtstr, fmt).replace(tzinfo=pytz.timezone(timezone))

def format_long_list(vals: list, cnt: int=3) -> str:
    fmt = pformat(vals)
    out = fmt.split('\n')
    if len(out) <= (2 * cnt):
        return fmt
    return ''.join(out[:3]) + ' ...,' + ''.join(out[-3:])

def ichunk(iterable: Iterable[Any], n: int) -> Iterable[Any]:
    """Yield n sized chunks, with tail chunk truncated.

    >>> list(ichunk([], 3))
    []
    >>> list(ichunk([1], 3))
    [[1]]
    >>> list(ichunk(range(3), 3))
    [[0, 1, 2]]
    >>> list(ichunk(range(10), 3))
    [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]]
    """
    _iter = iter(iterable)
    while True:
        out = []
        for _ in range(n):
            try:
                out.append(next(_iter))
            except StopIteration:
                if out:
                    yield out
                return
        yield out
