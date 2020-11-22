from .config import config
from .gam_config import GAMLineItems
from .utils import ichunk, format_long_list

logger = config.getLogger(__name__)

def create_line_items(gam):

    for bidder_code in config.bidder_codes():
        logger.info('#' * 80)
        logger.info('Bidder: name="%s", code="%s"', config.bidder_name(bidder_code), bidder_code)
        logger.info('Key: "%s", Values: %s',
                    config.targeting_key(bidder_code), format_long_list(config.cpm_names()))

        for media_type in [m_ for m_ in ('video', 'banner') if config.user['creative'].get(m_)]:
            logger.info('#' * 80)
            logger.info('Media Type: "%s"', media_type)

            for cpms in ichunk(config.cpm_names(),
                               config.app['googleads']['line_items']['max_per_order']):
                logger.info('Line Items: CPMs(min=%s, max=%s, cnt=%d)',
                            cpms[0], cpms[-1], len(cpms))

                gam_li = GAMLineItems(gam, media_type, bidder_code, cpms)

                logger.info('Line Item Creative Associations: Creative Count=%d',
                            len(gam_li.creatives))

                _ = gam_li.create()
