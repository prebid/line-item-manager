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

class CurrentNetwork(AppOperations):
    service = 'NetworkService'
    method = 'getCurrentNetwork'
