from .app_operations import Advertiser, AdUnit, Placement, TargetingKey, TargetingValues, \
     CreativeBanner, CreativeVideo
from .config import config
from .exceptions import ResourceNotFound
from .template import Template

CREATIVE_CLASS = dict(video=CreativeVideo, banner=CreativeBanner)

def create_line_items():

    template = Template(config)

    # 1. create advertiser if null
    advertiser = Advertiser(name=config.user['advertiser']['name']).fetchone(create=True)

    # 2. fetch each ad_unit_name (raise ResourceNotFound if missing)
    ad_units = []
    for name in config.user['targeting'].get('ad_unit_names', []):
        ad_unit = AdUnit(name=name).fetchone()
        if not ad_unit:
            raise ResourceNotFound(f'Ad Unit named \'{name}\' was not found')
        ad_units.append(ad_unit)

    # 3. fetch each placement_name (raise ResourceNotFound if missing)
    placements = []
    for name in config.user['targeting'].get('placement_names', []):
        placement = Placement(name=name).fetchone()
        if not placement:
            raise ResourceNotFound(f'Placement named \'{name}\' was not found')
        placements.append(placement)

    # 4. create custom targeting keys
    for name, values in config.custom_targeting_key_values():
        key = TargetingKey(name=name).fetchone(create=True)
        custom_targeting_values = TargetingValues(key_id=key['id']).create(names=values,
                                                                           validate=True)
    creatives = dict(video=[], banner=[])
    for bidder_code in config.bidder_codes():
        # 5. create creatives for each media type and size only if null
        for media in [m_ for m_ in ('video', 'banner') if config.user['creative'].get(m_)]:
            cfg = template.render('creative', bidder_code=bidder_code, media_type=media)
            for size in cfg[media]['sizes']:
                params = dict(
                    name=cfg['name'],
                    advertiserId=advertiser['id'],
                    size=size,
                )
                if media == 'video':
                    params.update(dict(
                        vastXmlUrl=cfg['video']['vast_xml_url'],
                    ))
                if media == 'banner':
                    params.update(dict(
                        snippet=cfg['banner']['snippet'],
                        isSafeFrameCompatible=cfg['banner'].get('safe_frame', True),
                    ))
                creatives[media].append(CREATIVE_CLASS[media](**params).fetchone(create=True))

        # 6. create targeting keys
        key = TargetingKey(name=config.targeting_key(bidder_code)).fetchone(create=True)
        targeting_values = TargetingValues(key_id=key['id']).create(names=config.cpm_names(),
                                                                    validate=True)

        # 7. create line items
