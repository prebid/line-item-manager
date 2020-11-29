#!/usr/bin/env python

"""Tests for `line_item_manager` package."""

import copy
from datetime import datetime
from logging import INFO, WARNING
import pytest
import shlex
from typing import Dict
import yaml

from googleads import ad_manager
from click.testing import CliRunner

from line_item_manager import cli
from line_item_manager.config import config, VERBOSE1, VERBOSE2
from line_item_manager.gam_config import GAMConfig
from line_item_manager.operations import TargetingKey
from line_item_manager.utils import num_hash

CONFIG_FILE = 'tests/resources/cfg.yml'
KEY_FILE = 'tests/resources/gam_creds.json'

def svc_id(svc_name, rec):
    return num_hash([svc_name, rec])

def rec_from_statement(statement):
    return {i_['key']:i_['value']['value'] for i_ in statement['values']}

def results_from_statement(svc_name, statement):
    rec = rec_from_statement(statement)
    rec.update({'id': svc_id(svc_name, rec)})
    return dict(results=[rec])

def byStatement(self, *args):
    return results_from_statement(self.service, args[0])

def create(self, *args):
    recs = copy.deepcopy(args[0])
    _ = [rec.update({'id': svc_id(self.service, rec)}) for rec in recs]
    return recs

class MockAdClient:
    custom_targeting: Dict = {}

    def GetService(self, service, version=None):
        self.service = service
        return self

    def getCurrentUser(self, *args):
        return dict(id=svc_id(self.service, 'CurrentUser'))

    def getCreativesByStatement(self, *args):
        return {}

    def getCustomTargetingValuesByStatement(self, *args):
        rec = rec_from_statement(args[0])
        for key, vals in self.custom_targeting.items():
            if rec['customTargetingKeyId'] == \
              svc_id(self.service, TargetingKey(name=key).params):
                recs = []
                for val in vals:
                    r_ = copy.deepcopy(rec)
                    r_.update(dict(name=val))
                    r_.update({'id': svc_id(self.service, rec)})
                    recs.append(r_)
                return dict(results=recs)
        return []

for i_ in ('AdUnits', 'Placements', 'Companies', 'Orders', 'CustomTargetingKeys'):
    setattr(MockAdClient, f'get{i_}ByStatement', byStatement)

for i_ in ('Creatives', 'LineItems', 'LineItemCreativeAssociations', 'CustomTargetingValues'):
    setattr(MockAdClient, f'create{i_}', create)

with open(CONFIG_FILE) as fp:
    user = yaml.safe_load(fp)

@pytest.mark.command(f'create {CONFIG_FILE} -k {KEY_FILE} -b interactiveOffers -b ix')
def test_create(monkeypatch, cli_config):
    # TODO:
    # - missing ad unit
    # - missing placement
    # - archive
    # - network name check
    class TestAdClient(MockAdClient):
        custom_targeting = {'country': ['US']}

        def createCustomTargetingValues(self, *args):
            if args[0][0]['customTargetingKeyId'] == \
              svc_id(self.service, TargetingKey(name='country').params):
                assert [rec['name'] for rec in args[0]] == ['CAN']
            return super().createCustomTargetingValues(*args)

    monkeypatch.setattr(ad_manager.AdManagerClient, "LoadFromString", lambda x: TestAdClient())
    gam = GAMConfig()
    gam.create_line_items()

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

def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    # import pdb; pdb.set_trace()
    # ctx = cli.create.make_context('create', shlex.split('{CONNFIG_FILE} -k {CONNFIG_FILE}'))
    # result = runner.invoke(cli.create, ['--help'])
    # result = runner.invoke(cli.show, ['bidders'])
    result = runner.invoke(cli.create, shlex.split('--help'))
    assert result.exit_code == 0
    # assert 'line_item_manager.cli.main' in result.output
    # help_result = runner.invoke(cli.main, ['--help'])
    # assert help_result.exit_code == 0
    # assert '--help  Show this message and exit.' in help_result.output
