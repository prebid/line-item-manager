from datetime import datetime
from pprint import pformat
from typing import Any, List, Iterable, Optional

from googleads.errors import GoogleAdsServerFault
from jinja2 import Template as J2Template
from retrying import retry
from tqdm import tqdm
from zeep.helpers import serialize_object
import pytz

from .config import config, VERBOSE1, VERBOSE2
from .exceptions import ResourceNotActive, ResourceNotFound
from .operations import Advertiser, AdUnit, Placement, TargetingKey, TargetingValues, \
     CreativeBanner, CreativeVideo, Order, CurrentNetwork, CurrentUser, LineItem, LICA
from .prebid import PrebidBidder
from .template import render_cfg, render_src
from .utils import format_long_list, ichunk

logger = config.getLogger(__name__)

def is_create_retryable_error(exc: Exception) -> bool:
    is_error = isinstance(exc, GoogleAdsServerFault)
    if is_error:
        logger.info('Retrying...')
    return is_error

def log(objname: str, obj: dict=None) -> None:
    logger.log(VERBOSE1, '%s:\n%s', objname, pformat(obj if obj else config.user.get(objname, {})))

def target_fetch(key: str, names: Iterable[str], operator='IS', match_type: str='EXACT',
                 reportableType: str='OFF') -> dict:
    tgt_key = TargetingKey(name=key, reportableType=reportableType).fetchone(create=True)
    recs = []
    for name in names:
        recs.append(dict(
            customTargetingKeyId=tgt_key['id'],
            name=name,
            displayName=name,
            matchType=match_type,
        ))
    tgt_values = TargetingValues(key_id=tgt_key['id'], name=list(names)).fetch(create=True, recs=recs, validate=True)
    return dict(
        key=tgt_key,
        operator=operator,
        values=tgt_values,
        names={v['name']:v for v in tgt_values}
    )

class GAMLineItems:

    def __init__(self, gam: Any, media_type: str, bidder: PrebidBidder, cpms: List[str]):
        self._advertiser: Optional[dict] = None
        self._creatives: Optional[List[dict]] = None
        self._line_items: Optional[List[dict]] = None
        self._order: Optional[dict] = None
        self._targeting_key: Optional[dict] = None

        self.gam: GAMConfig = gam
        self.media_type = media_type
        self.bidder = bidder
        self.cpms = cpms
        self.atts = dict(
            bidder=bidder,
            media_type=media_type,
        )
        _ = self.advertiser

    @property
    def is_size_override(self) -> bool:
        default = config.app['mgr']['creative'][self.media_type]['size_override']
        return config.user['creative'][self.media_type].get('size_override', default)

    @property
    def advertiser(self) -> dict:
        if self._advertiser is None:
            cfg = render_cfg('advertiser', self.bidder)
            log('advertiser', obj=cfg)
            if cfg.get('id'):
                self._advertiser = Advertiser(id=cfg['id']).fetchone()
                if not 'id' in self._advertiser:
                    raise ResourceNotFound(f"Advertiser id: {cfg['id']} was not found")
            else:
                self._advertiser = \
                  Advertiser(name=cfg['name'],
                             type=cfg.get('type', config.app['mgr']['advertiser']['type'])).fetchone(create=True)
        return self._advertiser

    @retry(retry_on_exception=is_create_retryable_error, stop_max_attempt_number=5, wait_fixed=2000)
    def create_licas(self, recs: List[dict]) -> List[dict]:
        return LICA().create(recs, validate=True)

    def create_licas_batched(self, recs: List[dict]) -> List[dict]:
        out = []
        logger.info(f'Line Item Creative Associations: Writing {len(recs)} records...')
        with tqdm(total=len(recs)) as pbar:
            for subset in ichunk(recs, config.app['mgr']['max_lica_records']):
                out += self.create_licas(subset)
                pbar.update(len(subset))
        return out

    def create(self) -> List[dict]:
        recs = []
        for line_item in self.line_items:
            for creative in self.creatives:
                rec = dict(lineItemId=line_item['id'], creativeId=creative['id'])
                if self.is_size_override:
                    rec.update(dict(sizes=config.user['creative'][self.media_type]['sizes']))
                recs.append(rec)
        return self.create_licas_batched(recs)

    @property
    def creatives(self) -> List[dict]:
        if self._creatives is None:
            cfg = render_cfg('creative', self.bidder, media_type=self.media_type)
            _name = f'creative_{self.media_type}'
            _method = getattr(self, _name)
            log(_name, obj={k:cfg[k] for k in ('name', self.media_type)})
            self._creatives = [_method(i_, cfg, size) \
                               for i_, size in enumerate(cfg[self.media_type]['sizes'])]
        return self._creatives

    def creative_name(self, cfg: dict, index: int):
        if self.is_size_override:
            tmpl = config.app['mgr']['creative']['size_override']['name_template']
            return J2Template(tmpl).render(name=cfg['name'], index=index + 1)
        return cfg['name']

    def creative_banner(self, index: int, cfg: dict, size: dict) -> dict:
        params = dict(
            name=self.creative_name(cfg, index),
            advertiserId=self.advertiser['id'],
            size=config.app['prebid']['creative']['size_override'] if self.is_size_override else size,
            snippet=cfg['banner']['snippet'],
            isSafeFrameCompatible=cfg['banner'].get('safe_frame', True),
        )
        return CreativeBanner(**params).fetchone(create=True)

    def creative_video(self, index: int, cfg: dict, size: dict) -> dict:
        params = dict(
            name=self.creative_name(cfg, index),
            advertiserId=self.advertiser['id'],
            size=config.app['prebid']['creative']['size_override'] if self.is_size_override else size,
            vastXmlUrl=cfg['video']['vast_xml_url'],
            duration=config.user['creative']['video']['duration'],
        )
        return CreativeVideo(**params).fetchone(create=True)

    @property
    def line_items(self) -> List[dict]:
        if self._line_items is None:
            recs = []
            src = config.template_src()
            for i_, cpm in enumerate(self.cpms):
                li_cfg = render_cfg('line_item', self.bidder, cpm=cpm, media_type=self.media_type)
                if (i_ == 0) or (i_ == len(self.cpms) - 1) or config.isLoggingEnabled(VERBOSE2):
                    log('line_item', obj=li_cfg)
                params = dict(
                    micro_amount=config.micro_amount(cpm),
                    cpm=cpm,
                    li=self,
                    li_cfg=li_cfg,
                    user_cfg=config.user,
                )
                recs.append(render_src(src, **params))
            self._line_items = LineItem().create(recs, validate=True)
        return self._line_items

    @property
    def order(self) -> dict:
        if self._order is None:
            cfg = render_cfg('order', self.bidder, media_type=self.media_type,
                             cpm_min=self.cpms[0], cpm_max=self.cpms[-1])
            log('order', obj=cfg)
            self._order = Order(
                name=cfg['name'],
                advertiserId=self.advertiser['id'],
                traffickerId=self.gam.user['id'],
                appliedTeamIds=config.user['order'].get('appliedTeamIds'),
            ).fetchone(create=True)
        return self._order

    @property
    def targeting_key(self) -> dict:
        if self._targeting_key is None:
            reportableType=config.targeting_bidder_key_config().get('reportableType', 'OFF')
            self._targeting_key = target_fetch(
                self.bidder.targeting_key, config.cpm_names(), reportableType=reportableType)
        return self._targeting_key

class GAMConfig:

    def __init__(self):
        _ = [log(i_) for i_ in ('targeting', 'rate')]
        self._ad_units: Optional[List[dict]] = None
        self._bidders: Optional[List[PrebidBidder]] = None
        self._li_objs: List[GAMLineItems] = []
        self._lica_objs: List[List[dict]] = []
        self._network: Optional[dict] = None
        self._placements: Optional[List[dict]] = None
        self._targeting_custom: Optional[List[dict]] = None
        self._user: Optional[dict] = None

        self._success = False

    @property
    def li_objs(self) -> List[GAMLineItems]:
        return self._li_objs

    @property
    def lica_objs(self) -> List[List[dict]]:
        return self._lica_objs

    @property
    def ad_units(self) -> List[dict]:
        if self._ad_units is None:
            self._ad_units = []
            for name in config.user.get('targeting', {}).get('ad_unit_names', []):
                ad_unit = AdUnit(name=name).fetchone()
                if not ad_unit:
                    raise ResourceNotFound(f'Ad Unit named \'{name}\' was not found')
                self._ad_units.append(ad_unit)
        return self._ad_units

    def add_li_obj(self, media_type: str, bidder: PrebidBidder, cpms: List[str]) -> GAMLineItems:
        self._li_objs.append(GAMLineItems(self, media_type, bidder, cpms))
        return self._li_objs[-1]

    def archive(self) -> None:
        order_ids = [i_.order['id'] for i_ in self._li_objs]
        if order_ids:
            logger.info('Auto-archiving Orders:\n%s', pformat(order_ids))
            response = Order(id=order_ids).archive()
            changes = response['numChanges'] if 'numChanges' in response else None
            if not changes == len(order_ids):
                logger.error('Order archive, %s, of %d changes, reported %s changes',
                             order_ids, len(order_ids), changes)

    @property
    def bidders(self) -> List[PrebidBidder]:
        if self._bidders is None:
            self._bidders = []
            for code in config.bidder_codes():
                bidder = PrebidBidder(
                    code,
                    override_map=config.user.get('bidder_key_map', {}).get(code, {}),
                    single_order=config.cli['single_order']
                    )
                tgt_key = serialize_object(TargetingKey(name=bidder.targeting_key).fetchone())
                if tgt_key and not tgt_key.get('status', 'ACTIVE') == 'ACTIVE':
                    raise ResourceNotActive(f"Bidder Targeting Key name \'{tgt_key['name']}\' "
                                            "is not active.  You must activate before re-running.")
                self._bidders.append(bidder)
        return self._bidders

    def cleanup(self) -> None:
        if not self.success and not config.cli['skip_auto_archive']:
            self.archive()

    def check_resources(self) -> None:
        _ = self.ad_units
        _ = self.placements
        _ = self.bidders

    def create_line_items(self) -> None:
        self.check_resources()
        for bidder in self.bidders:
            logger.info('#' * 80)
            logger.info('Bidder: name="%s", code="%s"', bidder.name, bidder.code)
            logger.info('Key: "%s", Values: %s', bidder.targeting_key,
                        format_long_list(config.cpm_names()))
            for media_type in config.media_types():
                logger.info('#' * 60)
                logger.info('Media Type: "%s"', media_type)
                for cpms in config.cpm_names_batched():
                    logger.info('Line Items: CPMs(min=%s, max=%s, count=%d)',
                                cpms[0], cpms[-1], len(cpms))
                    li_ = self.add_li_obj(media_type, bidder, cpms)
                    logger.info('Line Item Creative Associations: Creative Count=%d',
                                len(li_.creatives))
                    self._lica_objs.append(li_.create())

    @property
    def network(self) -> dict:
        if self._network is None:
            self._network = CurrentNetwork().fetchone()
        return self._network

    @property
    def placements(self) -> List[dict]:
        if self._placements is None:
            self._placements = []
            for name in config.user.get('targeting', {}).get('placement_names', []):
                placement = Placement(name=name).fetchone()
                if not placement:
                    raise ResourceNotFound(f'Placement named \'{name}\' was not found')
                self._placements.append(placement)
        return self._placements

    @property
    def success(self) -> bool:
        return self._success

    @success.setter
    def success(self, val: bool) -> None:
        self._success = val

    @property
    def targeting_custom(self) -> List[dict]:
        if self._targeting_custom is None:
            self._targeting_custom = [target_fetch(
                D_['name'],
                D_['values'],
                operator=D_['operator'],
                reportableType=D_['reportableType']) \
                for D_ in config.custom_targeting_key_values()]
        return self._targeting_custom

    @property
    def user(self) -> dict:
        if self._user is None:
            self._user = CurrentUser().fetchone()
        return self._user
