from jinja2 import Template as J2Template
import yaml

from .config import config

def package_file(name, **kwargs):
    with open(config.package_filename(name)) as fp:
        return yaml.safe_load(J2Template(fp.read()).render(**kwargs))

def render_src(src, **kwargs):
    return yaml.safe_load(J2Template(src).render(**kwargs))

def render_cfg(objname, bidder_code=None, media_type=None, cpm=None, cpm_min=None, cpm_max=None):
    codestr = '' if config.cli['single_order'] else bidder_code
    params = dict(
        time=config.start_time.strftime("%m/%d/%Y-%H:%M:%S"),
        run_mode='Test: ' if config.cli['test_run'] else ''
    )
    params.update(config.bidder_params(codestr))
    params['bidder_code'] = codestr
    params['bidder_name'] = config.app['line_item_manager']['single_order']['bidder_name'] if \
      config.cli['single_order'] else config.bidder_data()[bidder_code]['bidder-name']
    if media_type:
        params['media_type'] = media_type
    if cpm:
        params['cpm'] = cpm
    if cpm_min:
        params['cpm_min'] = cpm_min
    if cpm_max:
        params['cpm_max'] = cpm_max
    return render_src(yaml.safe_dump(config.user[objname]), **params)


