from .app_operations import Advertiser, AdUnit, Placement, TargetingKey, TargetingValues, \
     CreativeBanner
from .config import config
from .exceptions import ResourceNotFound

def create_line_items():

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

    # 4. create creatives for each media and size if null
    #   (raise ValueError on advertiser id mismatch if found)

    # 5. create all bidder targeting keys
    for name in config.targeting_keys():
        key = TargetingKey(name=name).fetchone(create=True)
        targeting_values = TargetingValues(key_id=key['id']).create(names=config.cpm_names(),
                                                                    validate=True)

    # 6. create custom targeting keys
    for name, values in config.custom_targeting_key_values():
        key = TargetingKey(name=name).fetchone(create=True)
        custom_targeting_values = TargetingValues(key_id=key['id']).create(names=values,
                                                                           validate=True)

    # 7. create line items
