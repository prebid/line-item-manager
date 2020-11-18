from .config import config
from .exceptions import ResourceNotFound
from .gam_config import GAMLineItems
from .operations import Advertiser, AdUnit, Placement, TargetingKey, TargetingValues, \
     CreativeBanner, CreativeVideo, Order, CurrentUser, LineItem
from .utils import ichunk

log = config.getLogger(__name__)

def create_line_items(gam):
    for bidder_code in config.bidder_codes():
        for media_type in [m_ for m_ in ('video', 'banner') if config.user['creative'].get(m_)]:
            for cpms in ichunk(config.cpm_names(), config.app['googleads']['line_items']['max_per_order']):
                line_items = GAMLineItems(gam, media_type, bidder_code, cpms).create()
