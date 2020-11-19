import copy
import uuid

from .config import config
from .gam_operations import GAMOperations

log = config.getLogger('operations')

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

    def id_dry_run(self):
        if 'name' in self.params:
            return self.params['name']
        return ''

    def create_dry_run(self):
        rec = copy.deepcopy(self.create_params)
        rec['id'] = f"DRY-{self.id_dry_run()}-{uuid.uuid4().hex[:8]}"
        return [rec]

class CreateMixIn:
    def create_dry_run(self):
        return self._create_dry_run

    def check(self, rec):
        return rec['name']

    def create(self, recs):
        if self.dry_run:
            if 'name' in recs[0]:
                _ = [rec.update({'id': f"{rec['name']}-{_i}"}) for _i, rec in enumerate(recs)]
            self._create_dry_run = recs
        results = super().create(recs)
        expected = {self.check(_r) for _r in recs}
        created = {self.check(_r) for _r in results}
        missing = [_n for _n in expected if _n not in created]
        if missing:
            raise ValueError(f'Following items were not found after creation: \'{missing}\'')
        return results

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

    def id_dry_run(self):
        return f"{self.params['name']}-{self.params['height']}X{self.params['width']}"

    def __init__(self, *args, **kwargs):
        if 'size' in kwargs:
            kwargs['height'] = kwargs['size']['height']
            kwargs['width'] = kwargs['size']['width']
        super().__init__(*args, **kwargs)

class CreativeVideo(Creative):
    create_fields = ('xsi_type', 'name', 'advertiserId', 'size', 'vastXmlUrl', 'vastRedirectType', 'duration')

    def __init__(self, *args, xsi_type='VastRedirectCreative', vastRedirectType='LINEAR', duration=60, **kwargs):
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

class LICA(CreateMixIn, AppOperations):
    service = 'LineItemCreativeAssociationService'
    create_method = 'createLineItemCreativeAssociations'

    def check(self, rec):
        return (rec['lineItemId'], rec['creativeId'])

class LineItem(CreateMixIn, AppOperations):
    service = 'LineItemService'
    method = 'getLineItemsByStatement'
    create_method = 'createLineItems'

class Order(AppOperations):
    service = "OrderService"
    method = 'getOrdersByStatement'
    create_method = 'createOrders'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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

    def create_dry_run(self):
        return self._create_dry_run

    def values(self, name, matchType='EXACT'):
        return dict(
            customTargetingKeyId=self.params['customTargetingKeyId'],
            name=name,
            displayName=name,
            matchType=matchType
        )

    def create(self, names=None):
        results = self.fetch()
        cur_names = {_r['name'] for _r in results}
        recs = [self.values(_n) for _n in names if _n not in cur_names]
        if recs:
            if self.dry_run:
                _ = [rec.update({'id': f"{rec['name']}-{_i}"}) for _i, rec in enumerate(recs)]
                self._create_dry_run = recs
            results += super().create(recs)
        cur_names = {_r['name'] for _r in results}
        missing = [_n for _n in names if _n not in cur_names]
        if missing:
            raise ValueError(f'Following names were not found after creation: \'{missing}\'')
        return results
