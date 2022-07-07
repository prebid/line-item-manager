import copy
from yaml import safe_dump as dump, safe_load as loads

SVC_IDS = dict(
    NetworkService={
        dump(dict()): 1501,
    },
    CompanyService={
        dump(dict(id=1001)): 1001,
        dump(dict(name="Prebid-InteractiveOffers")): 1001,
    },
    InventoryService={
        dump(dict(name="ad unit 1")): 2001,
        dump(dict(name="ad unit 2")): 2002,
    },
    PlacementService={
        dump(dict(name="placement 1")): 3001,
        dump(dict(name="placement 2")): 3002,
    },
    UserService={
        dump(dict()): 5001,
    },
    CustomTargetingService={
        dump(dict(name="country")): 7101,
        dump(dict(customTargetingKeyId=7101, name="US")): 7301,
        dump(dict(customTargetingKeyId=7101, name="CAN")): 7302,
        dump(dict(name="hb_pb_interactiveOff")): 7201,
        dump(dict(customTargetingKeyId=7201, name="1.25")): 7401,
        dump(dict(customTargetingKeyId=7201, name="1.50")): 7402,
    },
    LineItemCreativeAssociationService={
        dump(dict(lineItemId=8001, creativeId=4001)): 9001,
        dump(dict(lineItemId=8001, creativeId=4002)): 9002,
        dump(dict(lineItemId=8002, creativeId=4001)): 9001,
        dump(dict(lineItemId=8002, creativeId=4002)): 9002,
    },
)

SINGLE_ORDER_SVC_IDS = dict(
    CompanyService={
        dump(dict(name="Prebid-Top Bid")): 1001,
    },
    CustomTargetingService={
        dump(dict(name="country")): 7101,
        dump(dict(customTargetingKeyId=7101, name="US")): 7301,
        dump(dict(customTargetingKeyId=7101, name="CAN")): 7302,
        dump(dict(name="hb_pb")): 7501,
        dump(dict(customTargetingKeyId=7501, name="1.25")): 7601,
        dump(dict(customTargetingKeyId=7501, name="1.50")): 7602,
    },
)

MISSING_RESOURCE_SVC_IDS = dict(
    CustomTargetingService={
        dump(dict(name="country")): 7101,
        dump(dict(customTargetingKeyId=7101, name="US")): 7301,
        dump(dict(name="hb_pb")): 7501,
        dump(dict(customTargetingKeyId=7501, name="1.25")): 7601,
        dump(dict(customTargetingKeyId=7501, name="1.50")): 7602,
    },
)

SINGLE_ORDER_VIDEO_SVC_IDS = dict(
    CreativeService={
        dump(dict(
            name="Prebid Top Bid-video",
            advertiserId=1001,
            size={'height': 480, 'width': 640},
            vastXmlUrl= \
            'https://prebid.adnxs.com/pbc/v1/cache?uuid=%%PATTERN:hb_cache_id%%',
        )): 4001,
        dump(dict(
            name="Prebid Top Bid-video",
            advertiserId=1001,
            size={'height': 240, 'width': 320},
            vastXmlUrl= \
            'https://prebid.adnxs.com/pbc/v1/cache?uuid=%%PATTERN:hb_cache_id%%',
        )): 4002,
    },
    OrderService={
        dump(dict(
            name="Prebid-Top Bid-video-01/02/2020-08:09:10 1.25-1.50",
            advertiserId=1001,
            traffickerId=5001,
        )): 6001,
    },
    LineItemService={
        dump(dict(
            name="Prebid-Top Bid-video-01/02/2020-08:09:10 @ 1.25",
            orderId=6001,
        )): 8001,
        dump(dict(
            name="Prebid-Top Bid-video-01/02/2020-08:09:10 @ 1.50",
            orderId=6001,
        )): 8002,
    },
)

BIDDER_VIDEO_SVC_IDS = dict(
    CreativeService={
        dump(dict(
            name="Prebid InteractiveOffers-video",
            advertiserId=1001,
            size={'height': 480, 'width': 640},
            vastXmlUrl= \
            'https://prebid.adnxs.com/pbc/v1/cache?uuid=%%PATTERN:hb_cache_id_interact%%',
        )): 4001,
        dump(dict(
            name="Prebid InteractiveOffers-video",
            advertiserId=1001,
            size={'height': 240, 'width': 320},
            vastXmlUrl= \
            'https://prebid.adnxs.com/pbc/v1/cache?uuid=%%PATTERN:hb_cache_id_interact%%',
        )): 4002,
    },
    OrderService={
        dump(dict(
            name="Prebid-InteractiveOffers-video-01/02/2020-08:09:10 1.25-1.50",
            advertiserId=1001,
            traffickerId=5001,
        )): 6001,
    },
    LineItemService={
        dump(dict(
            name="Prebid-InteractiveOffers-video-01/02/2020-08:09:10 @ 1.25",
            orderId=6001,
        )): 8001,
        dump(dict(
            name="Prebid-InteractiveOffers-video-01/02/2020-08:09:10 @ 1.50",
            orderId=6001,
        )): 8002,
    },
)

BIDDER_VIDEO_SVC_IDS_SIZE_OVERRIDE = dict(
    CreativeService={
        dump(dict(
            name="Prebid InteractiveOffers-video Copy:1",
            advertiserId=1001,
            size={'height': 1, 'width': 1},
            vastXmlUrl= \
            'https://prebid.adnxs.com/pbc/v1/cache?uuid=%%PATTERN:hb_cache_id_interact%%',
        )): 4001,
        dump(dict(
            name="Prebid InteractiveOffers-video Copy:2",
            advertiserId=1001,
            size={'height': 1, 'width': 1},
            vastXmlUrl= \
            'https://prebid.adnxs.com/pbc/v1/cache?uuid=%%PATTERN:hb_cache_id_interact%%',
        )): 4002,
    },
)

BIDDER_TEST_RUN_VIDEO_SVC_IDS = dict(
    OrderService={
        dump(dict(
            name="Test: Prebid-InteractiveOffers-video-01/02/2020-08:09:10 1.25-1.50",
            advertiserId=1001,
            traffickerId=5001,
        )): 6001,
    },
    LineItemService={
        dump(dict(
            name="Test: Prebid-InteractiveOffers-video-01/02/2020-08:09:10 @ 1.25",
            orderId=6001,
        )): 8001,
        dump(dict(
            name="Test: Prebid-InteractiveOffers-video-01/02/2020-08:09:10 @ 1.50",
            orderId=6001,
        )): 8002,
    },
)

BIDDER_BANNER_SVC_IDS = dict(
    CreativeService={
        dump(dict(
            name="Prebid InteractiveOffers-banner Copy:1",
            advertiserId=1001,
            size={'height': 1, 'width': 1},
        )): 4001,
    },
    OrderService={
        dump(dict(
            name="Prebid-InteractiveOffers-banner-01/02/2020-08:09:10 1.25-1.50",
            advertiserId=1001,
            traffickerId=5001,
        )): 6001,
    },
    LineItemService={
        dump(dict(
            name="Prebid-InteractiveOffers-banner-01/02/2020-08:09:10 @ 1.25",
            orderId=6001,
        )): 8001,
        dump(dict(
            name="Prebid-InteractiveOffers-banner-01/02/2020-08:09:10 @ 1.50",
            orderId=6001,
        )): 8002,
    },
)

BIDDER_BANNER_SVC_IDS_NO_SIZE_OVERRIDE = dict(
    CreativeService={
        dump(dict(
            name="Prebid InteractiveOffers-banner",
            advertiserId=1001,
            size={'height': 20, 'width': 1000},
        )): 4001,
    },
)

BIDDER_VIDEO_BIDDER_KEY_MAP_SVC_IDS = dict(
    CustomTargetingService={
        dump(dict(name="country")): 7101,
        dump(dict(customTargetingKeyId=7101, name="US")): 7301,
        dump(dict(customTargetingKeyId=7101, name="CAN")): 7302,
        dump(dict(name="io_custom_key")): 7201,
        dump(dict(customTargetingKeyId=7201, name="1.25")): 7401,
        dump(dict(customTargetingKeyId=7201, name="1.50")): 7402,
    },
    CreativeService={
        dump(dict(
            name="Prebid InteractiveOffers-video",
            advertiserId=1001,
            size={'height': 480, 'width': 640},
            vastXmlUrl= \
            'https://prebid.adnxs.com/pbc/v1/cache?uuid=%%PATTERN:io_custom_cache_id%%',
        )): 4001,
        dump(dict(
            name="Prebid InteractiveOffers-video",
            advertiserId=1001,
            size={'height': 240, 'width': 320},
            vastXmlUrl= \
            'https://prebid.adnxs.com/pbc/v1/cache?uuid=%%PATTERN:io_custom_cache_id%%',
        )): 4002,
    },
)

def rec_from_statement(statement):
    rec = {}
    for i_ in statement['values']:
        if i_['value']['xsi_type'] == 'SetValue':
            value = [v['value'] for v in i_['value']['values']]
        else:
            value = i_['value']['value']
        rec[i_['key']] = value
    return rec

def svc_id(svc_recs, rec):
    _id = None
    for key, val in svc_recs.items():
        if loads(key).items() <= rec.items():
            assert _id is None
            _id = val
    return _id

def byStatement(self, *args):
    rec = rec_from_statement(args[0])
    _id = svc_id(self.svc_ids[self.service], rec)
    if not _id:
        return {}
    rec.update({'id': _id})
    return dict(results=[rec])

def create(self, *args):
    recs = copy.deepcopy(args[0])
    out = []
    for rec in recs:
        id_ = svc_id(self.svc_ids[self.service], rec)
        if id_:
            rec.update({'id': id_})
            out.append(rec)
    return out

class MockAdClient:

    def __init__(self, custom_targeting, service_ids):
        self.custom_targeting = copy.deepcopy(custom_targeting)
        self.svc_ids = copy.deepcopy(SVC_IDS)
        self.svc_ids.update(service_ids)

    def GetService(self, service, version=None):
        self.service = service
        return self

    def getCurrentUser(self, *args):
        return dict(id=svc_id(self.svc_ids[self.service], dict()))

    def getCurrentNetwork(self, *args):
        return dict(
            id=svc_id(self.svc_ids[self.service], dict()),
            displayName="Video Publisher",
            effectiveRootAdUnitId=1511,
        )

    def getCreativesByStatement(self, *args):
        return {}

    def getCustomTargetingValuesByStatement(self, *args):
        rec = rec_from_statement(args[0])
        recs = []
        for val in self.custom_targeting.get(rec['customTargetingKeyId'], []):
            if val in set(rec['name']):
                r_ = copy.deepcopy(rec)
                r_.update(dict(name=val))
                r_.update({'id': svc_id(self.svc_ids[self.service], r_)})
                recs.append(r_)
        return dict(results=recs)

for i_ in ('AdUnits', 'Placements', 'Companies', 'Orders', 'CustomTargetingKeys'):
    setattr(MockAdClient, f'get{i_}ByStatement', byStatement)

for i_ in ('Creatives', 'LineItems', 'LineItemCreativeAssociations', 'CustomTargetingValues'):
    setattr(MockAdClient, f'create{i_}', create)
