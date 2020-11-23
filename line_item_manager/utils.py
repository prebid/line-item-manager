from datetime import datetime
from pprint import pformat
import pytz


def values_from_bucket(bucket):
    rng = [int(100 * bucket[_k]) for _k in ('min', 'max', 'interval')]
    rng[1] += rng[2] # make stop inclusive
    return {_x / 100 for _x in range(*rng)}

def date_from_string(dtstr, fmt, timezone):
    if not dtstr:
        return None
    return datetime.strptime(dtstr, fmt).replace(tzinfo=pytz.timezone(timezone))

def format_long_list(vals, cnt=3):
    fmt = pformat(vals)
    out = fmt.split('\n')
    if len(out) <= (2 * cnt):
        return fmt
    return ''.join(out[:3]) + ' ...,' + ''.join(out[-3:])

def ichunk(iterable, n):
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
