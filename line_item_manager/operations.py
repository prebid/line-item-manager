import copy
import uuid

from .config import config
from .gam_operations import GAMOperations
from .utils import num_hash

class AppOperations(GAMOperations):

    @property
    def client(self):
        return config.client

    @property
    def version(self):
        return config.app['googleads']['version']

    @property
    def dry_run(self):
        return config.cli['dry_run']

    def create_id(self, rec):
        n_ = num_hash([type(self).__name__, str(rec)])
        return int(''.join([str(config.app['mgr']['dry_run']['id_prefix']), str(n_)]))

    def dry_run_recs(self, recs):
        out = copy.deepcopy(recs)
        _ = [r_.update(dict(id=self.create_id(r_))) for r_ in out]
        return out

    def check(self, rec):
        return rec['name']

    def validate(self, recs, results):
        observed = {self.check(r_) for r_ in results}
        missing = [self.check(r_) for r_ in recs if self.check(r_) not in observed]
        if missing:
            raise ValueError(f'Following items were not found after creation: \'{missing}\'')

class AdUnit(AppOperations):
    service = 'InventoryService'
    method = 'getAdUnitsByStatement'

class Advertiser(AppOperations):
    service = 'CompanyService'
    method = 'getCompaniesByStatement'
    create_method = 'createCompanies'

    def __init__(self, *args, _type='ADVERTISER', **kwargs):
        kwargs['type'] = _type
        super().__init__(*args, **kwargs)

class Creative(AppOperations):
    service = "CreativeService"
    method = 'getCreativesByStatement'
    create_method = 'createCreatives'
    query_fields = ('id', 'name', 'advertiserId', 'width', 'height')

    def __init__(self, *args, **kwargs):
        if 'size' in kwargs:
            kwargs['height'] = kwargs['size']['height']
            kwargs['width'] = kwargs['size']['width']
        super().__init__(*args, **kwargs)

class CreativeVideo(Creative):
    create_fields = ('xsi_type', 'name', 'advertiserId', 'size', 'vastXmlUrl',
                     'vastRedirectType', 'duration')

    def __init__(self, *args, xsi_type='VastRedirectCreative', vastRedirectType='LINEAR',
                 duration=60, **kwargs):
        kwargs['xsi_type'] = xsi_type
        kwargs['vastRedirectType'] = vastRedirectType
        kwargs['duration'] = duration
        super().__init__(*args, **kwargs)

class CreativeBanner(Creative):
    create_fields = ('xsi_type', 'name', 'advertiserId', 'size', 'isSafeFrameCompatible', 'snippet')

    def __init__(self, *args, xsi_type='ThirdPartyCreative', isSafeFrameCompatible=True, **kwargs):
        kwargs['xsi_type'] = xsi_type
        kwargs['isSafeFrameCompatible'] = isSafeFrameCompatible
        super().__init__(*args, **kwargs)

class CurrentNetwork(AppOperations):
    service = 'NetworkService'
    method = 'getCurrentNetwork'

class CurrentUser(AppOperations):
    service = 'UserService'
    method = 'getCurrentUser'

class LICA(AppOperations):
    service = 'LineItemCreativeAssociationService'
    create_method = 'createLineItemCreativeAssociations'

    def check(self, rec):
        return (rec['lineItemId'], rec['creativeId'])

class LineItem(AppOperations):
    service = 'LineItemService'
    method = 'getLineItemsByStatement'
    create_method = 'createLineItems'

class Order(AppOperations):
    service = "OrderService"
    method = 'getOrdersByStatement'
    create_method = 'createOrders'

    def archive(self):
        if self.dry_run:
            return dict(numChanges=len(self.params['id']))
        return self.svc().performOrderAction(
            {'xsi_type': 'ArchiveOrders'}, self.statement().ToStatement())

class Placement(AppOperations):
    service = 'PlacementService'
    method = 'getPlacementsByStatement'

class TargetingKey(AppOperations):
    service = 'CustomTargetingService'
    method = 'getCustomTargetingKeysByStatement'
    create_method = 'createCustomTargetingKeys'

    def __init__(self, *args, name=None, _type='PREDEFINED', **kwargs):
        kwargs['name'] = name
        kwargs['displayName'] = kwargs.get('displayName', name)
        kwargs['type'] = _type
        super().__init__(*args, **kwargs)

class TargetingValues(AppOperations):
    service = 'CustomTargetingService'
    method = 'getCustomTargetingValuesByStatement'
    create_method = 'createCustomTargetingValues'

    def __init__(self, *args, key_id=None, **kwargs):
        kwargs['customTargetingKeyId'] = key_id
        super().__init__(*args, **kwargs)
