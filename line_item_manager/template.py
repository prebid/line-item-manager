import re
import yaml

from jinja2 import Template as J2Template

from .config import config
from .prebid import PrebidBidder

logger = config.getLogger(__name__)

JINJA_PATTERN = re.compile(r'{{\W*(\w*)\W*}}')

def render_src(src: str, **kwargs) -> dict:
    clean_src = JINJA_PATTERN.sub(r'{{ \1 }}', src)
    return yaml.safe_load(J2Template(clean_src).render(**kwargs))

def render_cfg(objname: str, bidder: PrebidBidder, media_type: str=None,
               cpm: str=None, cpm_min: str=None, cpm_max: str=None) -> dict:
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
