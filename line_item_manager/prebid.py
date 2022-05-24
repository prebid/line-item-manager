import certifi
import csv
from typing import  Any, Dict, Optional
from urllib import request
import ssl

from .utils import load_package_file

SETTINGS: dict = load_package_file('settings.yml')['prebid']
BIDDERS: dict = SETTINGS['bidders']

class Prebid:
    """Prebid specific."""

    def __init__(self):
        """Initialize Prebid."""
        self._bidders = None

    @property
    def bidders(self) -> Dict[str, Any]:
        """Read remote bidders CSV metadata file.

        Returns:
          A dict keyed by bidder code
        """
        if self._bidders is None:
            context = ssl.create_default_context(cafile=certifi.where())
            reader = csv.DictReader([l.decode('utf-8') for l in request.urlopen(
                BIDDERS['data'], context=context).readlines()])
            self._bidders = {row['bidder-code']:row for row in reader}
        return self._bidders
prebid = Prebid()

class PrebidBidder:
    """Prebid Bidder."""

    def __init__(self, code: str, override_map: Dict[str, str]=None,
                 single_order: bool=False):
        """Initialize PrebidBidder.

        Args:
          code: bidder code
          override_map: mapping of bidder keys to override values
          single_order: True if single order
        """
        self.code = code
        self.name = BIDDERS['single_order']['name'] if single_order \
          else prebid.bidders[code]['bidder-name']
        self.override_map = override_map or {}
        self.single_order = single_order
        self._params: Optional[Dict[str, str]] = None

    @property
    def codestr(self) -> str:
        """String representation.

        Returns:
          Empty string if single order else code
        """
        return '' if self.single_order else self.code

    @staticmethod
    def validate_override_map(key_map: Optional[dict]) -> None:
        """Validate an override map checking for valid bidders and keys.

        Args:
          key_map: override map to validate
        """
        if not key_map:
            return
        valid_properties = set(prebid.bidders.keys())
        valid_properties.add(BIDDERS['targeting_key'])
        if not set(key_map.keys()).issubset(valid_properties):
            raise ValueError(f"'bidder_key_map' properties, " \
                             f"{set(key_map.keys())} must be valid bidder codes")
        valid_keys = set(BIDDERS['keys'])
        for k, v in key_map.items():
            if not set(v.keys()).issubset(valid_keys):
                raise ValueError(f"'bidder_key_map' properties, {set(v.keys())}, " \
                                 f"for '{k}' must be valid bidder keys")

    @property
    def params(self) -> Dict[str, str]:
        """Attribute of bidder specific parameters keyed by prefixes.

        Returns:
          Dict of bidder specific parameters
        """
        if self._params is None:
            self._params = \
              {k:self.override_map.get(k, self.fmt_bidder_key(k)) for k in BIDDERS['keys']}
        return self._params

    @property
    def targeting_key(self) -> str:
        """Get bidder specific targeting key.

        Returns:
          Bidder targeting key
        """
        return self.params[BIDDERS['targeting_key']]

    def fmt_bidder_key(self, prefix: str) -> str:
        """Get formatted bidder key with character limit.

        Args:
          prefix: bidder parameters prefix

        Returns:
          Formatted bidder key
        """
        if not self.codestr:
            return prefix
        return f'{prefix}_{self.codestr}'[:BIDDERS['key_char_limit']]
