import pkg_resources
import yaml

from googleads import ad_manager

class Config:

    _client = None
    _schema = None

    def __init__(self):
        self._app = self.load_package_file('settings.yml')

    @property
    def app(self):
        return self._app

    @property
    def cli(self):
        return self._cli

    @cli.setter
    def cli(self, obj):
        self._cli = obj

    @property
    def user(self):
        return self._user

    @user.setter
    def user_configfile(self, filename):
        self._user = self.load_file(filename)

    @property
    def network_code(self):
        return self.cli['network_code'] or self.user.get('publisher', {}).get('network_code')

    @property
    def network_name(self):
        return self.cli['network_name'] or self.user.get('publisher', {}).get('network_name')

    @property
    def client(self):
        if self._client is None:
            _cfg = self.load_package_file('googleads.yaml')
            _cfg['ad_manager']['network_code'] = self.network_code
            _cfg['ad_manager']['path_to_private_key_file'] = self.cli['private_key_file']
            self._client = ad_manager.AdManagerClient.LoadFromString(yaml.dump(_cfg))
        return self._client

    @property
    def schema(self):
        if self._schema is None:
            self._schema = self.load_package_file('schema.yml')
        return self._schema

    def load_file(self, filename):
        with open(filename) as fp:
            return yaml.safe_load(fp)

    def load_package_file(self, filename):
        return self.load_file(pkg_resources.resource_filename('line_item_manager',
                                                              f'conf.d/{filename}'))

config = Config()
