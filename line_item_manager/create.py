from .app_operations import Advertiser, AdUnit, Placement
from .config import config
from .exceptions import ResourceNotFound

gam = dict(
    advertiser=None,
    ad_units=[],
    placements=[],
    video=dict(creatives=[]),
    banner=dict(creatives=[]),
)

def create_line_items():

    # 1. create advertiser if null
    gam['advertiser'] = Advertiser(name=config.user['advertiser']['name']).fetchone(create=True)

    # 2. fetch each ad_unit_name (raise ResourceNotFound if missing)
    for name in config.user['targeting'].get('ad_unit_names', []):
        ad_unit = AdUnit(name=name).fetchone()
        if not ad_unit:
            raise ResourceNotFound(f'Ad Unit named \'{name}\' was not found')
        gam['ad_units'].append(ad_unit)

    # 3. fetch each placement_name (raise ResourceNotFound if missing)
    for name in config.user['targeting'].get('placement_names', []):
        placement = Placement(name=name).fetchone()
        if not placement:
            raise ResourceNotFound(f'Placement named \'{name}\' was not found')
        gam['placements'].append(placement)

    # 4. create creatives for each media and size if null
    #   (raise ValueError on advertiser id mismatch if found)

    # 5. create all bidder targeting keys if null
