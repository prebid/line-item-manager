import re
import yaml

from jinja2 import Template as J2Template

from .config import config
from .prebid import PrebidBidder

logger = config.getLogger(__name__)

JINJA_PATTERN = re.compile(r'{{\W*(\w*)\W*}}')

def render_src(src: str, **kwargs) -> dict:
    """Get object from jinja rendered yaml removing non-word chars from variable references.

    Args:
      src: templated source string
      kwargs: key-value pairs referenced in template

    Returns:
      A dict of the jinja rendered src
    """
    clean_src = JINJA_PATTERN.sub(r'{{ \1 }}', src)
    return yaml.safe_load(J2Template(clean_src).render(**kwargs))

def render_cfg(objname: str, bidder: PrebidBidder, media_type: str=None,
               cpm: str=None, cpm_min: str=None, cpm_max: str=None) -> dict:
    """Get jinja rendered object of a top level user config object.

    Args:
      objname: top level object name in user provided config
      bidder: a bidder instance
      media_type: media type value
      cpm: cpm value
      cpm_min: cpm minimum value
      cpm_max: cpm maximum value


    Returns:
      A dict of the jinja rendered src
    """
    params = dict(
        time=config.start_time.strftime("%m/%d/%Y-%H:%M:%S"),
        run_mode='Test: ' if config.cli['test_run'] else '',
        bidder_code=bidder.codestr,
        bidder_name=bidder.name,
    )
    params.update(bidder.params)
    if media_type:
        params['media_type'] = media_type
    if cpm:
        params['cpm'] = cpm
    if cpm_min:
        params['cpm_min'] = cpm_min
    if cpm_max:
        params['cpm_max'] = cpm_max
    return render_src(yaml.safe_dump(config.user[objname]), **params)
