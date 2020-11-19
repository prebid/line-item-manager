from .config import config
from .gam_config import GAMLineItems
from .utils import ichunk

log = config.getLogger(__name__)

def create_line_items(gam):
    for bidder_code in config.bidder_codes():
        for media_type in [m_ for m_ in ('video', 'banner') if config.user['creative'].get(m_)]:
            for cpms in ichunk(config.cpm_names(),
                               config.app['googleads']['line_items']['max_per_order']):
                gam_li = GAMLineItems(gam, media_type, bidder_code, cpms)
                associations = gam_li.create()
