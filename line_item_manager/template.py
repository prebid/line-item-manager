import copy
from jinja2 import Template as J2Template
import yaml

from .config import config

class Template:
    def __init__(self):
        self._params = dict(
            time=config.start_time.strftime("%m/%d/%Y-%H:%M:%S")
        )

    def package_file(self, name, **kwargs):
        with open(config.package_filename(name)) as fp:
            return yaml.safe_load(J2Template(fp.read()).render(**kwargs))

    def single_order_params(self):
        p_ = {k:k for k in config.app['prebid']['bidders']['keys']}
        p_.update({'bidder_code': '',
                  'bidder_name': config.app['line_item_manager']['single_order']['bidder_name']})
        return p_

    def bidder_params(self, code):
        p_ = {k:config.fmt_bidder_key(k, code) for k in config.app['prebid']['bidders']['keys']}
        p_.update({'bidder_code': code,
                   'bidder_name': config.bidder_data()[code]['bidder-name']})
        return p_

    def render(self, objname, bidder_code=None, media_type=None, cpm=None, cpm_min=None, cpm_max=None):
        params = copy.deepcopy(self._params)
        if bidder_code:
            params.update(self.single_order_params() if config.cli['single_order'] else self.bidder_params(bidder_code))
        if media_type:
            params['media_type'] = media_type
        if cpm:
            params['cpm'] = cpm
        if cpm_min:
            params['cpm_min'] = cpm_min
        if cpm_max:
            params['cpm_max'] = cpm_max
        objstr = J2Template(yaml.safe_dump(config.user[objname])).render(**params)
        return yaml.safe_load(objstr)
