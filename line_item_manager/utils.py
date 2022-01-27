from hashlib import sha1
import pkg_resources
from pprint import pformat
from typing import Any, Dict, Iterable, List

import yaml

def load_file(filename: str) -> dict:
    """Load a yaml file returning the represented dict.

    Args:
      filename: full path of file

    Returns:
      A dict based on specified yaml file
    """
    with open(filename) as fp:
        return yaml.safe_load(fp)

def load_package_file(name: str) -> dict:
    """Load a yaml package file returning the represented dict.

    Args:
      name: base name of the package file

    Returns:
      A dict based on specified yaml packaged file
    """
    return load_file(package_filename(name))

def package_filename(name: str) -> str:
    """Get fullpath of a package filename specified by the base filename.

    Args:
      name: base name of the package file

    Returns:
      Fullpath of the package file
    """
    return pkg_resources.resource_filename('line_item_manager',
                                           f'conf.d/{name}') # type: ignore[misc]

def read_package_file(name: str) -> str:
    """Get contents of a package file specified by name.

    Args:
      name: base name of the package file

    Returns:
      Contents of the package file as a string
    """
    with open(package_filename(name)) as fp:
        return fp.read()

def num_hash(obj: Any, digits: int=6) -> int:
    """Get an integer hash with specified number of digits.

    Args:
      obj: object to hash
      digits: number of digits in returned hash

    Returns:
      A hashed integer with specified number of digits
    """
    return int(sha1(str(obj).encode('utf-8')).hexdigest(), 16) % 10**digits

def values_from_bucket(bucket: Dict[str, float]) -> set:
    """Get set of price formatted values specified by min, max and interval.

    Args:
      bucket: dict containing min, max and interval values

    Returns:
      Formatted set of values from min to max by interval
    """
    rng = [round(100 * bucket[_k]) for _k in ('min', 'max', 'interval')]
    rng[1] += rng[2] # make stop inclusive
    return {_x / 100 for _x in range(*rng)}

def format_long_list(vals: list, cnt: int=3) -> str:
    """Pretty format with head, tail, and ellipsis to indicate omissions.

    Args:
      vals: sequence of values to be formatted
      cnt: size of the head and tail

    Returns:
      A pretty formatted string with omissions
    """
    fmt = pformat(vals)
    out = fmt.split('\n')
    if len(out) <= (2 * cnt):
        return fmt
    return ''.join(out[:cnt]) + ' ...,' + ''.join(out[-cnt:])

def ichunk(iterable: Iterable[Any], n: int) -> Iterable[List[Any]]:
    """Yield n sized chunks, with tail chunk truncated.

    Args:
      iterable: sequence of values to be chunked
      n: size of chunks

    Returns:
      Yield an iterable of n sized chunks as lists

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
