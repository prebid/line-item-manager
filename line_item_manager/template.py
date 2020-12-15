import re
import yaml

from jinja2 import Template as J2Template

from .config import config

logger = config.getLogger(__name__)

JINJA_PATTERN = re.compile(r'{{\W*(\w*)\W*}}')

def render_src(src, **kwargs):
    clean_src = JINJA_PATTERN.sub(r'{{ \1 }}', src)
    return yaml.safe_load(J2Template(clean_src).render(**kwargs))

def render_cfg(objname, bidder_code=None, media_type=None, cpm=None,
               cpm_min=None, cpm_max=None):
    codestr = '' if config.cli['single_order'] else bidder_code
    params = dict(
        time=config.start_time.strftime("%m/%d/%Y-%H:%M:%S"),
        run_mode='Test: ' if config.cli['test_run'] else '',
        bidder_code=codestr,
        bidder_name=config.bidder_name(bidder_code),
    )
    params.update(config.bidder_params(codestr))
    if media_type:
        params['media_type'] = media_type
    if cpm:
        params['cpm'] = cpm
    if cpm_min:
        params['cpm_min'] = cpm_min
    if cpm_max:
        params['cpm_max'] = cpm_max
    return render_src(yaml.safe_dump(config.user[objname]), **params)
