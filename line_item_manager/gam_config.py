from typing import Dict

from .config import config
from .exceptions import ResourceNotFound
from .operations import Advertiser, AdUnit, Placement, TargetingKey, TargetingValues, \
     CreativeBanner, CreativeVideo, Order, CurrentNetwork, CurrentUser, LineItem, LICA
from .template import Template

def target(key, values):
    tgt_key = TargetingKey(name=key).fetchone(create=True)
    tgt_values = TargetingValues(key_id=tgt_key['id']).create(names=values)
    return dict(
        key=tgt_key,
        values=tgt_values,
        names={v['name']:v for v in tgt_values}
    )

class GAMConfig:

    _advertiser: Dict = {}
    _ad_units = None
    _network: Dict = {}
    _placements = None
    _targeting_custom = None
    _user: Dict = {}

    def __init__(self):
        self.template = Template()

    @property
    def ad_units(self):
        if self._ad_units is None:
            self._ad_units = []
            for name in config.user['targeting'].get('ad_unit_names', []):
                ad_unit = AdUnit(name=name).fetchone()
                if not ad_unit:
                    raise ResourceNotFound(f'Ad Unit named \'{name}\' was not found')
                self._ad_units.append(ad_unit)
        return self._ad_units

    @property
    def advertiser(self):
        if not self._advertiser:
            self._advertiser = Advertiser(name=config.user['advertiser']['name']).fetchone(create=True)
        return self._advertiser

    @property
    def network(self):
        if not self._network:
            self._network = CurrentNetwork().fetch()
        return self._network

    @property
    def placements(self):
        if self._placements is None:
            self._placements = []
            for name in config.user['targeting'].get('placement_names', []):
                placement = Placement(name=name).fetchone()
                if not placement:
                    raise ResourceNotFound(f'Placement named \'{name}\' was not found')
                self._placements.append(placement)
        return self._placements

    @property
    def targeting_custom(self):
        if self._targeting_custom is None:
            self._targeting_custom = [target(k, v) for k, v in config.custom_targeting_key_values()]
        return self._targeting_custom

    @property
    def user(self):
        if not self._user:
            self._user = CurrentUser().fetch()
        return self._user

class GAMLineItems:

    _creatives = None
    _order = None
    _targeting_key = None
    _line_items = None

    def __init__(self, gam: GAMConfig, media_type, bidder_code, cpms):
        self.gam = gam
        self.media_type = media_type
        self.bidder_code = bidder_code
        self.cpms = cpms
        self.template = Template()
        self.atts = dict(
            bidder_code=bidder_code,
            media_type=media_type,
        )

    @property
    def line_items(self):
        if self._line_items is None:
            recs = []
            for cpm in self.cpms:
                li_cfg = self.template.render('line_item', cpm=cpm, **self.atts)
                params = dict(
                    microAmount=int(float(cpm) * \
                                    config.app['googleads']['line_items']['micro_cent_factor']),
                    cpm=cpm,
                    li=self,
                    li_cfg=li_cfg,
                    user_cfg=config.user,
                )
                recs.append(self.template.package_file('templates/line_item_video.yml', **params))
            self._line_items = LineItem().create(recs)
        return self._line_items

    def create(self):
        recs = []
        for line_item in self.line_items:
            for creative in self.creatives:
                recs.append(dict(lineItemId=line_item['id'], creativeId=creative['id']))
        return LICA().create(recs)

    @property
    def creatives(self):
        if self._creatives is None:
            cfg = self.template.render('creative', **self.atts)
            _method = getattr(self, f'creative_{self.media_type}')
            self._creatives = [_method(cfg, size) for size in cfg[self.media_type]['sizes']]
        return self._creatives

    def creative_banner(self, cfg, size):
        params = dict(
            name=cfg['name'],
            advertiserId=self.gam.advertiser['id'],
            size=size,
            snippet=cfg['banner']['snippet'],
            isSafeFrameCompatible=cfg['banner'].get('safe_frame', True),
        )
        return CreativeBanner(**params).fetchone(create=True)

    def creative_video(self, cfg, size):
        params = dict(
            name=cfg['name'],
            advertiserId=self.gam.advertiser['id'],
            size=size,
            vastXmlUrl=cfg['video']['vast_xml_url'],
        )
        return CreativeVideo(**params).fetchone(create=True)

    @property
    def order(self):
        if self._order is None:
            cfg = self.template.render('order', cpm_min=self.cpms[0], cpm_max=self.cpms[-1], **self.atts)
            self._order = Order(name=cfg['name'], advertiserId=self.gam.advertiser['id'],
                                traffickerId=self.gam.user['id']).fetchone(create=True)
        return self._order

    @property
    def targeting_key(self):
        if self._targeting_key is None:
            self._targeting_key = target(config.targeting_key(self.bidder_code), config.cpm_names())
        return self._targeting_key
