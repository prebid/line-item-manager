#!/usr/bin/env python

"""Tests for `line_item_manager` package."""

import copy
from logging import INFO, WARNING
import pytest
import shlex
import yaml
from yaml import safe_dump as dump

from googleads import ad_manager
from click.testing import CliRunner

from line_item_manager import cli
from line_item_manager.config import config, VERBOSE1, VERBOSE2
from line_item_manager.exceptions import ResourceNotFound
from line_item_manager.gam_config import GAMConfig

from .client import MockAdClient, SINGLE_ORDER_SVC_IDS, SINGLE_ORDER_VIDEO_SVC_IDS, \
     BIDDER_BANNER_SVC_IDS, BIDDER_VIDEO_SVC_IDS, rec_from_statement

CONFIG_FILE = 'tests/resources/cfg.yml'
KEY_FILE = 'tests/resources/gam_creds.json'
CUSTOM_TARGETING = {7101: ['US']}

# init
config._start_time = pytest.start_time
with open(CONFIG_FILE) as fp:
    user = yaml.safe_load(fp)

class Client(MockAdClient):

    def createCustomTargetingValues(self, *args):
        if args[0][0]['customTargetingKeyId'] == 7101:
            assert [rec['name'] for rec in args[0]] == ['CAN']
        return super().createCustomTargetingValues(*args)

    def performOrderAction(self, *args):
        order_ids = [i_['value'] for i_ in args[1]['values'][0]['value']['values']]
        assert order_ids == [6001]
        return dict(numChanges=1)

@pytest.mark.parametrize("command, err_str",
 [
  (f'tests/resources/cfg_bad_yaml.yml -k {KEY_FILE} -b interactiveOffers', 'Check your configfile.'),
  (f'tests/resources/cfg_video.yml -k {KEY_FILE}', 'You must use --single-order or provide'),
  (f'tests/resources/cfg_video.yml -k {KEY_FILE} -b ix --single-order', 'Use of --single-order and --bidder-code'),
  (f'tests/resources/cfg_no_pub.yml -k {KEY_FILE} -b ix', 'Network code must be provided'),
  (f'tests/resources/cfg_no_pub.yml -k {KEY_FILE} -b ix --network-code 1234', 'Network name must be provided'),
  (f'tests/resources/cfg_video.yml -k {KEY_FILE} -b badcode', 'Bidder code \'badcode\''),
  (f'tests/resources/cfg_video.yml -k {KEY_FILE} -b ix --network-name badname', 'Network name found \'Video Publisher\''),
  (f'tests/resources/cfg_validation_error.yml -k {KEY_FILE} -b ix', 'the following validation errors'),
 ]
)
def test_cli_create_bad(monkeypatch, command, err_str):
    """Test the CLI."""
    client = Client(CUSTOM_TARGETING, BIDDER_VIDEO_SVC_IDS)
    monkeypatch.setattr(ad_manager.AdManagerClient, "LoadFromString", lambda x: client)

    runner = CliRunner()
    result = runner.invoke(cli.create, shlex.split(command))
    assert result.exit_code == 2
    assert err_str in result.output

def test_cli_create_good(monkeypatch):
    client = Client(CUSTOM_TARGETING, BIDDER_VIDEO_SVC_IDS)
    monkeypatch.setattr(ad_manager.AdManagerClient, "LoadFromString", lambda x: client)

    runner = CliRunner()
    result = runner.invoke(
        cli.create,
        shlex.split(f'tests/resources/cfg_video.yml -k {KEY_FILE} -b interactiveOffers')
    )
    assert result.exit_code == 0

@pytest.mark.parametrize("command",
 [
  ('config'),
  ('bidders'),
 ]
)
def test_cli_show_good(command):
    runner = CliRunner()
    result = runner.invoke(
        cli.show,
        shlex.split(command)
    )
    assert result.exit_code == 0

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
    assert config.load_file('tests/resources/video_single_order_expected.yml') == \
      gam.li_objs[0].line_items
    gam.cleanup()

@pytest.mark.command(f'create tests/resources/cfg_video.yml -k {KEY_FILE} -b interactiveOffers')
def test_video_one_bidder(monkeypatch, cli_config):
    client = Client(CUSTOM_TARGETING, BIDDER_VIDEO_SVC_IDS)
    monkeypatch.setattr(ad_manager.AdManagerClient, "LoadFromString", lambda x: client)
    gam = GAMConfig()
    gam.create_line_items()

    assert len(gam.li_objs) == 1
    assert config.load_file('tests/resources/video_expected.yml') == gam.li_objs[0].line_items

@pytest.mark.command(f'create tests/resources/cfg_banner.yml -k {KEY_FILE} -b interactiveOffers')
def test_banner_one_bidder(monkeypatch, cli_config):
    client = Client(CUSTOM_TARGETING, BIDDER_BANNER_SVC_IDS)
    monkeypatch.setattr(ad_manager.AdManagerClient, "LoadFromString", lambda x: client)
    gam = GAMConfig()
    gam.create_line_items()

    assert len(gam.li_objs) == 1
    assert config.load_file('tests/resources/banner_expected.yml') == gam.li_objs[0].line_items

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

@pytest.mark.command(f'create {CONFIG_FILE} -b interactiveOffers -b ix')
def test_bidders(cli_config):
    assert config.network_code == user['publisher']['network_code']
    assert config.network_name == user['publisher']['network_name']
    assert config.media_types() == ['video', 'banner']
    assert config.start_time == pytest.start_time
    assert not config.isLoggingEnabled(VERBOSE1)
    assert [config.bidder_name(c_) for c_ in config.bidder_codes()] == \
      ['InteractiveOffers', 'Index Exchange']
    assert config.cpm_names() == ['0.10', '0.20', '0.30', '0.80', '1.30']
    assert [config.targeting_key(c_) for c_ in config.bidder_codes()] == \
      ['hb_pb_interactiveOff', 'hb_pb_ix']

@pytest.mark.command(f'create {CONFIG_FILE} --single-order')
def test_single_order(cli_config):
    assert [config.targeting_key(c_) for c_ in config.bidder_codes()] == ['hb_pb']

@pytest.mark.command(f'create {CONFIG_FILE} -b oneVideo -b ix')
def test_fmt_bidder_key(cli_config):
    assert config.fmt_bidder_key('prefix', '') == 'prefix'
    assert config.fmt_bidder_key('prefix', '01234567890123456789') == 'prefix_0123456789012'

@pytest.mark.command(f'create {CONFIG_FILE} -b oneVideo -b ix -t')
def test_test_run(cli_config):
    assert config.cpm_names() == ['0.10', '0.20']

@pytest.mark.command(f'create {CONFIG_FILE} --network-code 9876 --network-name abcd -b oneVideo -b ix')
def test_network_meta(cli_config):
    assert config.network_code == 9876
    assert config.network_name == 'abcd'

@pytest.mark.command(f'create {CONFIG_FILE} -b ix -v')
def test_verbose1(cli_config):
    assert config.isLoggingEnabled(VERBOSE1)
    assert not config.isLoggingEnabled(VERBOSE2)

@pytest.mark.command(f'create {CONFIG_FILE} -b ix -v -v')
def test_verbose2(cli_config):
    assert config.isLoggingEnabled(VERBOSE1)
    assert config.isLoggingEnabled(VERBOSE2)

@pytest.mark.command(f'create {CONFIG_FILE} -b ix -q')
def test_quiet(cli_config):
    assert config.isLoggingEnabled(WARNING)
    assert not config.isLoggingEnabled(INFO)
