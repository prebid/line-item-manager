import pkg_resources
import yaml

from googleads import ad_manager

class Config:

    _client = None

    def __init__(self):
        with open(pkg_resources.resource_filename('line_item_manager',
                                                  'conf.d/settings.yml')) as fp:
            self._app = yaml.safe_load(fp)

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
        with open(filename) as fp:
            self._user = yaml.safe_load(fp)

    @property
    def client(self):
        if self._client is None:
            with open(pkg_resources.resource_filename('line_item_manager',
                                                      'conf.d/googleads.yaml')) as fp:
                _cfg = yaml.safe_load(fp)
            _cfg['ad_manager']['network_code'] = self.cli['network_code'] or \
              self.user['publisher']['network_code']
            _cfg['ad_manager']['path_to_private_key_file'] = self.cli['private_key_file']
            self._client = ad_manager.AdManagerClient.LoadFromString(yaml.dump(_cfg))
        return self._client


config = Config()
