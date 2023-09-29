import copy
from typing import List, Optional, Tuple, Union

from googleads import ad_manager

from .config import config
from .gam_operations import GAMOperations
from .utils import num_hash

class AppOperations(GAMOperations):
    """Operations using GAM abstract class."""

    @property
    def client(self) -> Optional[ad_manager.AdManagerClient]:
        """Get GAM client.

        Returns:
          GAM client
        """
        return config.client

    @property
    def version(self) -> str:
        """Get preferred GAM API version

        Returns:
           version string
        """
        return config.app['googleads']['version']

    @property
    def dry_run(self) -> bool:
        """Get dry run state.

        Returns:
          True if doing a dry run
        """
        return config.cli.get('dry_run', False)

    def create_id(self, rec: dict) -> int:
        """Create ID from reference rec.

        Args:
          rec: reference

        Returns:
          Integer hash as ID
        """
        n_ = num_hash([type(self).__name__, str(rec)])
        return int(''.join([str(config.app['mgr']['dry_run']['id_prefix']), str(n_)]))

    def dry_run_recs(self, recs: List[dict]) -> List[dict]:
        """Recs that are returned on create when doing a dry run.

        Args:
          recs: reference recs

        Returns:
          Reference recs with dummy IDs
        """
        out = copy.deepcopy(recs)
        _ = [r_.update(dict(id=self.create_id(r_))) for r_ in out]
        return out

    def check(self, rec: dict) -> Union[str, Tuple[int, int]]:
        """Record attribute used for existence checks.

        Args:
          rec: reference rec

        Returns:
          Record attribute
        """
        return rec['name']

    def validate(self, recs: List[dict], results: List[dict]) -> None:
        """Raise value error if records are missing.

        Args:
          recs: reference recs
          results: operation results
        """
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

    def __init__(self, *args, **kwargs):
        if 'type' in kwargs:
            kwargs['type'] = kwargs['type']
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

    def __init__(self, *args, xsi_type: str='VastRedirectCreative', vastRedirectType: str='LINEAR',
                 duration: int, **kwargs):
        kwargs['xsi_type'] = xsi_type
        kwargs['vastRedirectType'] = vastRedirectType
        kwargs['duration'] = duration if duration else \
          config.app['prebid']['creative']['video']['max_duration']
        super().__init__(*args, **kwargs)

class CreativeBanner(Creative):
    create_fields = ('xsi_type', 'name', 'advertiserId', 'size', 'isSafeFrameCompatible', 'snippet')

    def __init__(self, *args, xsi_type: str='ThirdPartyCreative',
                 isSafeFrameCompatible: bool=True, **kwargs):
        kwargs['xsi_type'] = xsi_type
        kwargs['isSafeFrameCompatible'] = isSafeFrameCompatible
        super().__init__(*args, **kwargs)

class CurrentNetwork(AppOperations):
    use_statement = False
    service = 'NetworkService'
    method = 'getCurrentNetwork'

class CurrentUser(AppOperations):
    use_statement = False
    service = 'UserService'
    method = 'getCurrentUser'

class LICA(AppOperations):
    service = 'LineItemCreativeAssociationService'
    create_method = 'createLineItemCreativeAssociations'
    method = 'getLineItemCreativeAssociationsByStatement'

    def check(self, rec: dict) -> Tuple[int, int]:
        return (rec['lineItemId'], rec['creativeId'])

class LineItem(AppOperations):
    service = 'LineItemService'
    method = 'getLineItemsByStatement'
    create_method = 'createLineItems'

class Order(AppOperations):
    service = "OrderService"
    method = 'getOrdersByStatement'
    create_method = 'createOrders'
    query_fields = ('id', 'name', 'advertiserId', 'traffickerId')

    def __init__(self, *args, **kwargs):
        if 'appliedTeamIds' in kwargs and kwargs['appliedTeamIds'] is None:
            del kwargs['appliedTeamIds']
        super().__init__(*args, **kwargs)

    def archive(self) -> dict:
        if self.dry_run:
            return dict(numChanges=len(self.params['id']))
        return self.svc().performOrderAction(
            {'xsi_type': 'ArchiveOrders'},
            self.statement().ToStatement()) # type: ignore[union-attr]

class Placement(AppOperations):
    service = 'PlacementService'
    method = 'getPlacementsByStatement'

class TargetingKey(AppOperations):
    service = 'CustomTargetingService'
    method = 'getCustomTargetingKeysByStatement'
    create_method = 'createCustomTargetingKeys'
    query_fields = ('name', )

    def __init__(self, *args, name: str=None, _type: str='PREDEFINED', **kwargs):
        if not name is None:
            kwargs['name'] = name
        kwargs['displayName'] = kwargs.get('displayName', name)
        kwargs['type'] = _type
        super().__init__(*args, **kwargs)

class TargetingValues(AppOperations):
    service = 'CustomTargetingService'
    method = 'getCustomTargetingValuesByStatement'
    create_method = 'createCustomTargetingValues'

    def __init__(self, *args, key_id: int=None, **kwargs):
        kwargs['customTargetingKeyId'] = key_id
        super().__init__(*args, **kwargs)
