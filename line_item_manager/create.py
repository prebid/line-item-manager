from config import config

from app_operations import CurrentNetwork

gam = dict(
    advertiser=None,
    ad_units=[],
    placements=[],
    video=dict(creatives=[]),
    banner=dict(creatives=[]),
)

def create():
    pass
    # 1. create advertiser if null
    # 2. fetch each ad_unit_name (raise ResourceNotFound if missing)
    # 3. fetch each placement_name (raise ResourceNotFound if missing)
    # 4. create creatives for each media and size
    #   (raise ValueError on advertiser id mismatch)
