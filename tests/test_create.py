#!/usr/bin/env python

"""Tests for `line_item_manager` package."""

import copy
from logging import INFO, WARNING, ERROR
import pytest
import shlex
import yaml
from yaml import safe_dump as dump

from googleads import ad_manager
from googleads.errors import GoogleAdsError, GoogleAdsServerFault
from click.testing import CliRunner

from line_item_manager import cli
from line_item_manager import gam_config
from line_item_manager.config import config, VERBOSE1, VERBOSE2
from line_item_manager.exceptions import ResourceNotActive, ResourceNotFound
from line_item_manager.gam_config import GAMConfig
from line_item_manager.utils import load_file, num_hash

from .client import MockAdClient, SINGLE_ORDER_SVC_IDS, SINGLE_ORDER_VIDEO_SVC_IDS, \
     BIDDER_BANNER_SVC_IDS, BIDDER_VIDEO_SVC_IDS, BIDDER_TEST_RUN_VIDEO_SVC_IDS, \
     MISSING_RESOURCE_SVC_IDS, BIDDER_BANNER_SVC_IDS_NO_SIZE_OVERRIDE, \
     BIDDER_VIDEO_BIDDER_KEY_MAP_SVC_IDS

CONFIG_FILE = 'tests/resources/cfg.yml'
KEY_FILE = 'tests/resources/gam_creds.json'
CUSTOM_TARGETING = {7101: ['US']}

EXPECTED_LICA = \
  [[{'creativeId': 4001, 'id': 9001, 'lineItemId': 8001},
    {'creativeId': 4002, 'id': 9002, 'lineItemId': 8001},
    {'creativeId': 4001, 'id': 9001, 'lineItemId': 8002},
    {'creativeId': 4002, 'id': 9002, 'lineItemId': 8002}]]

VIDEO_CREATIVE = {
    'xsi_type': 'VastRedirectCreative',
    'name': 'Prebid InteractiveOffers-video',
    'advertiserId': 1001,
    'size': {'height': 480, 'width': 640},
    'vastXmlUrl': 'https://prebid.adnxs.com/pbc/v1/cache?uuid=%%PATTERN:hb_cache_id_interact%%',
    'vastRedirectType': 'LINEAR',
    'duration': 30000
    }

LI_0 = 9999899367
LI_1 = 9999960551

def mock_id(name: str, rec: object):
    return int('9999' + str(num_hash([name, str(rec)])))

CREATIVE_0 = mock_id('CreativeVideo', VIDEO_CREATIVE)
VIDEO_CREATIVE.update({'size': {'height': 240, 'width': 320}})
CREATIVE_1 = mock_id('CreativeVideo', VIDEO_CREATIVE)

LICA_0_0 = mock_id('LICA', {'lineItemId': LI_0, 'creativeId': CREATIVE_0})
LICA_0_1 = mock_id('LICA', {'lineItemId': LI_0, 'creativeId': CREATIVE_1})
LICA_1_0 = mock_id('LICA', {'lineItemId': LI_1, 'creativeId': CREATIVE_0})
LICA_1_1 = mock_id('LICA', {'lineItemId': LI_1, 'creativeId': CREATIVE_1})

DRY_RUN_EXPECTED_LICA = \
  [[{'lineItemId': LI_0, 'creativeId': CREATIVE_0, 'id': LICA_0_0},
    {'lineItemId': LI_0, 'creativeId': CREATIVE_1, 'id': LICA_0_1},
    {'lineItemId': LI_1, 'creativeId': CREATIVE_0, 'id': LICA_1_0},
    {'lineItemId': LI_1, 'creativeId': CREATIVE_1, 'id': LICA_1_1}]]

BANNER_EXPECTED_LICA = \
  [[{'lineItemId': 8001, 'creativeId': 4001, 'sizes': [{'height': 20, 'width': 1000}], 'id': 9001},
    {'lineItemId': 8002, 'creativeId': 4001, 'sizes': [{'height': 20, 'width': 1000}], 'id': 9001}]]

BANNER_EXPECTED_LICA_NO_SIZE_OVERRIDE = \
  [[{'creativeId': 4001, 'id': 9001, 'lineItemId': 8001},
    {'creativeId': 4001, 'id': 9001, 'lineItemId': 8002}]]

# init
config._start_time = pytest.start_time
with open(CONFIG_FILE) as fp:
    user = yaml.safe_load(fp)

class Client(MockAdClient):

    def __init__(self, custom_targeting, service_ids, **kwargs):
        self.kwargs = kwargs
        super().__init__(custom_targeting, service_ids)

    def getCustomTargetingKeysByStatement(self, *args):
        r_ = super().getCustomTargetingKeysByStatement(*args)
        if r_ and self.kwargs.get('invalid_targeting_key'):
            r_['results'][0].update(dict(status='INACTIVE'))
        return r_

    def createCustomTargetingValues(self, *args):
        if args[0][0]['customTargetingKeyId'] == 7101:
            assert [rec['name'] for rec in args[0]] == ['CAN']
        return super().createCustomTargetingValues(*args)

    def performOrderAction(self, *args):
        order_ids = [i_['value'] for i_ in args[1]['values'][0]['value']['values']]
        assert order_ids == [6001]
        return dict(numChanges=1)

@pytest.mark.parametrize("command, err_str", [
  (f'tests/resources/cfg_bad_yaml.yml -k {KEY_FILE} -b interactiveOffers',
   'Check your configfile.'),
  (f'tests/resources/cfg_video.yml -k {KEY_FILE}',
   'You must use --single-order or provide'),
  (f'tests/resources/cfg_video.yml -k {KEY_FILE} -b ix --single-order',
   'Use of --single-order and --bidder-code'),
  (f'tests/resources/cfg_no_pub.yml -k {KEY_FILE} -b ix',
   'Network code must be provided'),
  (f'tests/resources/cfg_no_pub.yml -k {KEY_FILE} -b ix --network-code 1234',
   'Network name must be provided'),
  (f'tests/resources/cfg_video.yml -k {KEY_FILE} -b badcode',
   'Bidder code \'badcode\''),
  (f'tests/resources/cfg_video.yml -k {KEY_FILE} -b ix --network-name badname',
   'Network name found \'Video Publisher\''),
  (f'tests/resources/cfg_validation_error.yml -k {KEY_FILE} -b ix',
   'the following validation errors'),
  (f'tests/resources/cfg_bad_granularity.yml -k {KEY_FILE} -b interactiveOffers',
   '\'custom\' is a required property'),
  (f'tests/resources/cfg_bad_vcpm.yml -k {KEY_FILE} -b interactiveOffers',
   '\'vcpm\' requires using line item type \'standard\''),
  (f'tests/resources/cfg_bad_standard_type.yml -k {KEY_FILE} -b interactiveOffers',
   '\'end_datetime\' is a required property'),
  (f'tests/resources/cfg_bad_timezone.yml -k {KEY_FILE} -b interactiveOffers',
   'Unknown Time Zone, \'BAD_TIME_ZONE\''),
  (f'tests/resources/cfg_bad_param.yml -k {KEY_FILE} -b interactiveOffers',
   'Additional properties are not allowed (\'ad_unit_names\' was unexpected)'),
  (f'tests/resources/cfg_bad_key_properties.yml -k {KEY_FILE} -b interactiveOffers',
   '{\'bad_code\'} must be valid bidder codes'),
  (f'tests/resources/cfg_bad_bidder_keys.yml -k {KEY_FILE} -b interactiveOffers',
   'for \'pubmatic\' must be valid bidder keys'),
])
def test_cli_create_bad(monkeypatch, command, err_str):
    """Test the CLI."""
    client = Client(CUSTOM_TARGETING, BIDDER_VIDEO_SVC_IDS)
    monkeypatch.setattr(ad_manager.AdManagerClient, "LoadFromString", lambda x: client)

    runner = CliRunner()
    result = runner.invoke(cli.create, shlex.split(command))
    assert result.exit_code == 2
    assert err_str in result.output

@pytest.mark.parametrize("command, err_str", [
  ('tests/resources/cfg_video.yml -k tests/resources/gam_creds_bad_json.json -b ix', 'Check your private key file.'),
  (f'tests/resources/cfg_video.yml -k {KEY_FILE} -b ix', 'Check your private key file.'),
])
def test_cli_no_mock_create_bad(command, err_str):
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli.create, shlex.split(command))
    assert result.exit_code == 2
    assert err_str in result.output

def test_cli_client_exception(monkeypatch):
    command = f'tests/resources/cfg_video.yml -k {KEY_FILE} -b ix'
    def raise_exception(self):
        raise Exception
    monkeypatch.setattr(ad_manager.AdManagerClient, "LoadFromString", raise_exception)
    runner = CliRunner()
    result = runner.invoke(cli.create, shlex.split(command))
    assert result.exit_code == 2
    assert "Check your private key file. Not able to successfully" in result.output

def test_cli_network_exception(monkeypatch):
    command = f'tests/resources/cfg_video.yml -k {KEY_FILE} -b ix'
    def raise_exception(self):
        raise GoogleAdsError('Test Network')
    client = Client(CUSTOM_TARGETING, BIDDER_VIDEO_SVC_IDS)
    monkeypatch.setattr(ad_manager.AdManagerClient, "LoadFromString", lambda x: client)
    monkeypatch.setattr(gam_config.CurrentNetwork, "fetchone", raise_exception)
    runner = CliRunner()
    result = runner.invoke(cli.create, shlex.split(command))
    assert result.exit_code == 2
    assert "Check your network code and permissions" in result.output

@pytest.mark.parametrize("command", [
  (f'tests/resources/cfg_video.yml -k {KEY_FILE} -b interactiveOffers'),
])
def test_cli_create_good(monkeypatch, command):
    client = Client(CUSTOM_TARGETING, BIDDER_VIDEO_SVC_IDS)
    monkeypatch.setattr(ad_manager.AdManagerClient, "LoadFromString", lambda x: client)
    runner = CliRunner()
    result = runner.invoke(cli.create, shlex.split(command))

    assert result.exit_code == 0

@pytest.mark.parametrize("exc_type, err_str", [
  ('GAE', 'Google Ads Error, Test GAM Error'),
  ('RNF', 'Not able to find the following resource:\n  - Test'),
  ('RNA', 'Resource is not active:\n  - Test'),
  ('KI', 'User Interrupt'),
])
def test_cli_ads_error(caplog, monkeypatch, exc_type, err_str):
    command = f'tests/resources/cfg_video.yml -k {KEY_FILE} -b interactiveOffers'
    def raise_exception(self):
        if exc_type == 'GAE':
            raise GoogleAdsError('Test GAM Error')
        if exc_type == 'RNA':
            raise ResourceNotActive('Test')
        if exc_type == 'RNF':
            raise ResourceNotFound('Test')
        if exc_type == 'KI':
            raise KeyboardInterrupt()
    client = Client(CUSTOM_TARGETING, BIDDER_VIDEO_SVC_IDS)
    monkeypatch.setattr(ad_manager.AdManagerClient, "LoadFromString", lambda x: client)
    monkeypatch.setattr(cli.GAMConfig, "create_line_items", raise_exception)
    caplog.set_level(WARNING)
    runner = CliRunner()
    _ = runner.invoke(cli.create, shlex.split(command))

    assert err_str in caplog.text

def test_cli_cleanup_exception(caplog, monkeypatch):
    command = f'tests/resources/cfg_video.yml -k {KEY_FILE} -b interactiveOffers'
    def raise_exception(self):
        raise GoogleAdsError('Test GAM Error')
    client = Client(CUSTOM_TARGETING, BIDDER_VIDEO_SVC_IDS)
    monkeypatch.setattr(ad_manager.AdManagerClient, "LoadFromString", lambda x: client)
    monkeypatch.setattr(cli.GAMConfig, "create_line_items", raise_exception)
    monkeypatch.setattr(cli.GAMConfig, "cleanup", raise_exception)
    caplog.set_level(ERROR)
    runner = CliRunner()
    _ = runner.invoke(cli.create, shlex.split(command))

    assert 'Google Ads Error, Test GAM Error' in caplog.text

def test_cli_missing_resource(caplog, monkeypatch):
    command = f'tests/resources/cfg_video.yml -k {KEY_FILE} -b interactiveOffers'
    svc_ids = copy.deepcopy(BIDDER_VIDEO_SVC_IDS)
    svc_ids.update(MISSING_RESOURCE_SVC_IDS)
    client = Client(CUSTOM_TARGETING, svc_ids)
    monkeypatch.setattr(ad_manager.AdManagerClient, "LoadFromString", lambda x: client)
    caplog.set_level(ERROR)
    runner = CliRunner()
    _ = runner.invoke(cli.create, shlex.split(command))

    assert 'Unexpected result' in caplog.text
    assert 'not found after creation: \'[\'CAN\']\'' in caplog.text

@pytest.mark.command(f'create tests/resources/cfg_video.yml -k {KEY_FILE} --single-order')
def test_video_single_order(monkeypatch, cli_config):
    svc_ids = copy.deepcopy(SINGLE_ORDER_SVC_IDS)
    svc_ids.update(SINGLE_ORDER_VIDEO_SVC_IDS)
    client = Client(CUSTOM_TARGETING, svc_ids)
    monkeypatch.setattr(ad_manager.AdManagerClient, "LoadFromString", lambda x: client)
    gam = GAMConfig()
    gam.create_line_items()

    assert gam.network['displayName'] == "Video Publisher"
    assert len(gam.li_objs) == 1
    assert load_file('tests/resources/video_single_order_expected.yml') == \
      gam.li_objs[0].line_items
    assert EXPECTED_LICA == gam.lica_objs
    gam.cleanup()

@pytest.mark.command(f'create tests/resources/cfg_video.yml -k {KEY_FILE} -b interactiveOffers')
def test_archive_error(caplog, monkeypatch, cli_config):
    class ThisClient(Client):
        def performOrderAction(self, *args):
            return dict(numChanges=0)

    client = ThisClient(CUSTOM_TARGETING, BIDDER_VIDEO_SVC_IDS)
    monkeypatch.setattr(ad_manager.AdManagerClient, "LoadFromString", lambda x: client)
    caplog.set_level(ERROR)
    gam = GAMConfig()
    gam.create_line_items()
    gam.cleanup()

    assert 'Order archive, [6001], of 1 changes, reported 0 changes' in caplog.text

@pytest.mark.command(f'create tests/resources/cfg_video.yml -v -v -n -k {KEY_FILE} -b interactiveOffers')
def test_dry_run(monkeypatch, cli_config):
    client = Client(CUSTOM_TARGETING, BIDDER_VIDEO_SVC_IDS)
    monkeypatch.setattr(ad_manager.AdManagerClient, "LoadFromString", lambda x: client)
    gam = GAMConfig()
    gam.create_line_items()
    gam.cleanup()

    assert len(gam.li_objs) == 1
    assert load_file('tests/resources/video_expected_dry_run.yml') == \
      gam.li_objs[0].line_items
    assert DRY_RUN_EXPECTED_LICA == gam.lica_objs

@pytest.mark.command(f'create tests/resources/cfg_video.yml -t -k {KEY_FILE} -b interactiveOffers')
def test_test_run(monkeypatch, cli_config):
    svc_ids = copy.deepcopy(BIDDER_VIDEO_SVC_IDS)
    svc_ids.update(BIDDER_TEST_RUN_VIDEO_SVC_IDS)
    client = Client(CUSTOM_TARGETING, svc_ids)
    monkeypatch.setattr(ad_manager.AdManagerClient, "LoadFromString", lambda x: client)
    gam = GAMConfig()
    gam.create_line_items()

    assert len(gam.li_objs) == 1
    assert load_file('tests/resources/video_expected_test_run.yml') == \
      gam.li_objs[0].line_items
    assert EXPECTED_LICA == gam.lica_objs

@pytest.mark.command(f'create tests/resources/cfg_video.yml -k {KEY_FILE} -b interactiveOffers')
def test_video_one_bidder(monkeypatch, cli_config):
    client = Client(CUSTOM_TARGETING, BIDDER_VIDEO_SVC_IDS)
    monkeypatch.setattr(ad_manager.AdManagerClient, "LoadFromString", lambda x: client)
    gam = GAMConfig()
    gam.create_line_items()

    assert len(gam.li_objs) == 1
    assert load_file('tests/resources/video_expected.yml') == gam.li_objs[0].line_items
    assert EXPECTED_LICA == gam.lica_objs

@pytest.mark.command(f'create tests/resources/cfg_video_company_by_id.yml -k {KEY_FILE} -b interactiveOffers')
def test_video_one_bidder(monkeypatch, cli_config):
    client = Client(CUSTOM_TARGETING, BIDDER_VIDEO_SVC_IDS)
    monkeypatch.setattr(ad_manager.AdManagerClient, "LoadFromString", lambda x: client)
    gam = GAMConfig()
    gam.create_line_items()

    assert len(gam.li_objs) == 1
    assert load_file('tests/resources/video_expected.yml') == gam.li_objs[0].line_items
    assert EXPECTED_LICA == gam.lica_objs

@pytest.mark.command(f'create tests/resources/cfg_video_one_custom_value.yml -k {KEY_FILE} -b interactiveOffers')
def test_video_one_bidder_custom_criteria(monkeypatch, cli_config):
    client = Client(CUSTOM_TARGETING, BIDDER_VIDEO_SVC_IDS)
    monkeypatch.setattr(ad_manager.AdManagerClient, "LoadFromString", lambda x: client)
    gam = GAMConfig()
    gam.create_line_items()

    assert len(gam.li_objs) == 1
    assert load_file('tests/resources/video_expected_one_custom_value.yml') == gam.li_objs[0].line_items
    assert EXPECTED_LICA == gam.lica_objs

@pytest.mark.command(f'create tests/resources/cfg_video.yml -k {KEY_FILE} -b interactiveOffers')
def test_video_one_bidder_invalid_targeting_key(monkeypatch, cli_config):
    client = Client(CUSTOM_TARGETING, BIDDER_VIDEO_SVC_IDS, invalid_targeting_key=True)
    monkeypatch.setattr(ad_manager.AdManagerClient, "LoadFromString", lambda x: client)
    gam = GAMConfig()

    with pytest.raises(ResourceNotActive) as e_:
        gam.create_line_items()
    assert "'hb_pb_interactiveOff' is not active" in str(e_)

@pytest.mark.command(f'create tests/resources/cfg_video_bidder_key_map.yml -k {KEY_FILE} -b interactiveOffers')
def test_video_one_bidder_key_map(monkeypatch, cli_config):
    svc_ids = copy.deepcopy(BIDDER_VIDEO_SVC_IDS)
    svc_ids.update(BIDDER_VIDEO_BIDDER_KEY_MAP_SVC_IDS)
    client = Client(CUSTOM_TARGETING, svc_ids)
    monkeypatch.setattr(ad_manager.AdManagerClient, "LoadFromString", lambda x: client)
    gam = GAMConfig()
    gam.create_line_items()

    assert len(gam.li_objs) == 1
    assert load_file('tests/resources/video_expected.yml') == gam.li_objs[0].line_items
    assert EXPECTED_LICA == gam.lica_objs

@pytest.mark.command(f'create tests/resources/cfg_banner.yml -k {KEY_FILE} -b interactiveOffers')
def test_banner_one_bidder(monkeypatch, cli_config):
    client = Client(CUSTOM_TARGETING, BIDDER_BANNER_SVC_IDS)
    monkeypatch.setattr(ad_manager.AdManagerClient, "LoadFromString", lambda x: client)
    gam = GAMConfig()
    gam.create_line_items()

    assert len(gam.li_objs) == 1
    assert load_file('tests/resources/banner_expected.yml') == gam.li_objs[0].line_items
    assert BANNER_EXPECTED_LICA == gam.lica_objs

@pytest.mark.command(f'create tests/resources/cfg_video_priority_8.yml -k {KEY_FILE} -b interactiveOffers')
def test_video_priority_8(monkeypatch, cli_config):
    client = Client(CUSTOM_TARGETING, BIDDER_VIDEO_SVC_IDS)
    monkeypatch.setattr(ad_manager.AdManagerClient, "LoadFromString", lambda x: client)
    gam = GAMConfig()
    gam.create_line_items()

    assert len(gam.li_objs) == 1
    assert {8} == {i_['priority'] for i_ in gam.li_objs[0].line_items}
    assert EXPECTED_LICA == gam.lica_objs

@pytest.mark.command(f'create tests/resources/cfg_video.yml -k {KEY_FILE} -b interactiveOffers')
def test_missing_ad_unit_resource(monkeypatch, cli_config):
    svc_ids = copy.deepcopy(BIDDER_VIDEO_SVC_IDS)
    svc_ids.update(dict(InventoryService={dump(dict(name="ad unit 1")): 2001}))
    client = Client(CUSTOM_TARGETING, svc_ids)
    monkeypatch.setattr(ad_manager.AdManagerClient, "LoadFromString", lambda x: client)
    gam = GAMConfig()

    with pytest.raises(ResourceNotFound) as e_:
        gam.create_line_items()
    assert "'ad unit 2' was not found" in str(e_)

@pytest.mark.command(f'create tests/resources/cfg_video.yml -k {KEY_FILE} -b interactiveOffers')
def test_missing_placement_resource(monkeypatch, cli_config):
    svc_ids = copy.deepcopy(BIDDER_VIDEO_SVC_IDS)
    svc_ids.update(dict(PlacementService={dump(dict(name="placement 2")): 3002}))
    client = Client(CUSTOM_TARGETING, svc_ids)
    monkeypatch.setattr(ad_manager.AdManagerClient, "LoadFromString", lambda x: client)
    gam = GAMConfig()

    with pytest.raises(ResourceNotFound) as e_:
        gam.create_line_items()
    assert "'placement 1' was not found" in str(e_)

@pytest.mark.command(f'create tests/resources/cfg_video_no_targeting.yml -k {KEY_FILE} -b interactiveOffers')
def test_video_no_targeting_video(monkeypatch, cli_config):
    client = Client(CUSTOM_TARGETING, BIDDER_VIDEO_SVC_IDS)
    monkeypatch.setattr(ad_manager.AdManagerClient, "LoadFromString", lambda x: client)
    gam = GAMConfig()
    gam.create_line_items()

    assert len(gam.li_objs) == 1
    assert load_file('tests/resources/video_expected_no_targeting.yml') == \
      gam.li_objs[0].line_items
    assert EXPECTED_LICA == gam.lica_objs

@pytest.mark.command(f'create tests/resources/cfg_banner_vcpm.yml -k {KEY_FILE} -b interactiveOffers')
def test_banner_safe_frame_vcpm(monkeypatch, cli_config):
    svc_ids = copy.deepcopy(BIDDER_BANNER_SVC_IDS)
    svc_ids.update(BIDDER_BANNER_SVC_IDS_NO_SIZE_OVERRIDE)
    client = Client(CUSTOM_TARGETING, svc_ids)
    monkeypatch.setattr(ad_manager.AdManagerClient, "LoadFromString", lambda x: client)
    gam = GAMConfig()
    gam.create_line_items()

    assert len(gam.li_objs) == 1
    assert load_file('tests/resources/banner_vcpm_expected.yml') == gam.li_objs[0].line_items
    assert BANNER_EXPECTED_LICA_NO_SIZE_OVERRIDE == gam.lica_objs

@pytest.mark.command(f'create tests/resources/cfg_sponsorship.yml -k {KEY_FILE} -b interactiveOffers')
def test_sponsorship_priority(monkeypatch, cli_config):
    client = Client(CUSTOM_TARGETING, BIDDER_BANNER_SVC_IDS)
    monkeypatch.setattr(ad_manager.AdManagerClient, "LoadFromString", lambda x: client)
    gam = GAMConfig()
    gam.create_line_items()

    assert len(gam.li_objs) == 1
    assert load_file('tests/resources/sponsorship_expected.yml') == gam.li_objs[0].line_items
    assert BANNER_EXPECTED_LICA == gam.lica_objs
