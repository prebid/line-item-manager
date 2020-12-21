from logging import INFO, WARNING

import pytest
import yaml

from line_item_manager.config import config, VERBOSE1, VERBOSE2
from line_item_manager.prebid import PrebidBidder

CONFIG_FILE = 'tests/resources/cfg.yml'
KEY_FILE = 'tests/resources/gam_creds.json'

config._start_time = pytest.start_time

with open(CONFIG_FILE) as fp:
    user = yaml.safe_load(fp)

@pytest.mark.command(f'create {CONFIG_FILE} -k {KEY_FILE} -b interactiveOffers -b ix')
def test_bidders(cli_config):
    assert config.network_code == user['publisher']['network_code']
    assert config.network_name == user['publisher']['network_name']
    assert config.media_types() == ['video', 'banner']
    assert config.start_time == pytest.start_time
    assert not config.isLoggingEnabled(VERBOSE1)
    assert [PrebidBidder(c_).name for c_ in config.bidder_codes()] == \
      ['InteractiveOffers', 'Index Exchange']
    assert config.cpm_names() == ['0.10', '0.20', '0.30', '0.80', '1.30']
    assert [PrebidBidder(c_).targeting_key for c_ in config.bidder_codes()] == \
      ['hb_pb_interactiveOff', 'hb_pb_ix']

@pytest.mark.command(f'create {CONFIG_FILE} -k {KEY_FILE} --single-order')
def test_single_order(cli_config):
    assert [PrebidBidder(c_, single_order=config.cli['single_order']).targeting_key \
            for c_ in config.bidder_codes()] == ['hb_pb']

def test_fmt_bidder_key():
    assert PrebidBidder('oneVideo').fmt_bidder_key('prefix') == "prefix_oneVideo"
    assert PrebidBidder('oneVideo').fmt_bidder_key('012345678901234') == "012345678901234_oneV"
    assert PrebidBidder('bad', single_order=True).fmt_bidder_key('prefix') == "prefix"

@pytest.mark.command(f'create {CONFIG_FILE} -k {KEY_FILE} -b oneVideo -b ix -t')
def test_test_run(cli_config):
    assert config.cpm_names() == ['0.10', '0.20']

@pytest.mark.command(f'create {CONFIG_FILE} -k {KEY_FILE} --network-code 9876 --network-name abcd -b oneVideo -b ix')
def test_network_meta(cli_config):
    assert config.network_code == 9876
    assert config.network_name == 'abcd'

@pytest.mark.command(f'create {CONFIG_FILE} -k {KEY_FILE} -b ix -v')
def test_verbose1(cli_config):
    assert config.isLoggingEnabled(VERBOSE1)
    assert not config.isLoggingEnabled(VERBOSE2)

@pytest.mark.command(f'create {CONFIG_FILE} -k {KEY_FILE} -b ix -v -v')
def test_verbose2(cli_config):
    assert config.isLoggingEnabled(VERBOSE1)
    assert config.isLoggingEnabled(VERBOSE2)

@pytest.mark.command(f'create {CONFIG_FILE} -k {KEY_FILE} -b ix -q')
def test_quiet(cli_config):
    assert config.isLoggingEnabled(WARNING)
    assert not config.isLoggingEnabled(INFO)

@pytest.mark.command(f'create tests/resources/cfg_granularity_high.yml -k {KEY_FILE} -b ix -q')
def test_granularity(cli_config):
    assert config.cpm_names() == ['%.2f' % (v_ / 100) for v_ in range(1, 2001, 1)]
