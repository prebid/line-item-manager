from .config import config
from .gam_operations import GAMOperations

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

class AdUnit(AppOperations):
    service = 'InventoryService'
    method = 'getAdUnitsByStatement'

class Advertiser(AppOperations):
    service = 'CompanyService'
    method = 'getCompaniesByStatement'
    create_method = 'createCompanies'

    def __init__(self, *args, **kwargs):
        kwargs['type'] = 'ADVERTISER'
        super().__init__(*args, **kwargs)

class CurrentNetwork(AppOperations):
    service = 'NetworkService'
    method = 'getCurrentNetwork'

class Placement(AppOperations):
    service = 'PlacementService'
    method = 'getPlacementsByStatement'

