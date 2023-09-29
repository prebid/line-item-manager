from logging import INFO, WARNING

import pytest
import yaml

from line_item_manager.config import config, VERBOSE1, VERBOSE2
from line_item_manager.prebid import PrebidBidder, prebid
from line_item_manager.utils import package_filename, load_file

CONFIG_FILE = 'tests/resources/cfg.yml'
KEY_FILE = 'tests/resources/gam_creds.json'
TMPL_FILE = 'tests/resources/li_template.yml'
SETTINGS_FILE = 'tests/resources/settings.yml'
SCHEMA_FILE = 'tests/resources/schema.yml'
CONFIG_BIDDER = list(prebid.bidders.keys())[0]

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
      ['InteractiveOffers', 'Index Exchange (Prebid.js)']
    assert config.cpm_names() == ['0.10', '0.20', '0.30', '0.80', '1.30']
    assert [PrebidBidder(c_).targeting_key for c_ in config.bidder_codes()] == \
      ['hb_pb_interactiveOff', 'hb_pb_ix']
    assert config.custom_targeting_key_values() == \
      [{'name': 'country', 'values': {'CAN', 'US'}, 'operator': 'IS', 'reportableType': 'OFF'}]
    assert config.template_src() == open(package_filename('line_item_template.yml')).read()
    assert config.settings_obj() == load_file(package_filename('settings.yml'))
    assert config.schema == load_file(package_filename('schema.yml'))

@pytest.mark.command(f'create {CONFIG_FILE} -k {KEY_FILE} --single-order')
def test_single_order(cli_config):
    assert [PrebidBidder(c_, single_order=config.cli['single_order']).targeting_key \
            for c_ in config.bidder_codes()] == ['hb_pb']
    assert config.user['order']['appliedTeamIds'] == [12345678, 23456789]

def test_fmt_bidder_key():
    assert PrebidBidder(CONFIG_BIDDER).fmt_bidder_key('prefix') == f"prefix_{CONFIG_BIDDER}"
    assert PrebidBidder(CONFIG_BIDDER).fmt_bidder_key('012345678901234') == f"012345678901234_{CONFIG_BIDDER[:4]}"
    assert PrebidBidder('bad', single_order=True).fmt_bidder_key('prefix') == "prefix"

@pytest.mark.command(f'create {CONFIG_FILE} -k {KEY_FILE} -b {CONFIG_BIDDER} -b ix -t')
def test_test_run(cli_config):
    assert config.cpm_names() == ['0.10', '0.20']
    assert config.user['creative']['video']['duration'] == 30000
    assert config.user['creative']['video']['max_duration'] == 30000

@pytest.mark.command(f'create {CONFIG_FILE} -k {KEY_FILE} -b {CONFIG_BIDDER} -b ix --template {TMPL_FILE}')
def test_template(cli_config):
    assert config.template_src() == open(TMPL_FILE).read()

@pytest.mark.command(f'create {CONFIG_FILE} -k {KEY_FILE} -b {CONFIG_BIDDER} -b ix --settings {SETTINGS_FILE}')
def test_settings(cli_config):
    assert config.settings_obj() == load_file(SETTINGS_FILE)

@pytest.mark.command(f'create {CONFIG_FILE} -k {KEY_FILE} -b {CONFIG_BIDDER} -b ix --schema {SCHEMA_FILE}')
def test_schema(cli_config):
    assert config.schema == load_file(SCHEMA_FILE)

@pytest.mark.command(f'create {CONFIG_FILE} -k {KEY_FILE} --network-code 9876 --network-name abcd -b {CONFIG_BIDDER} -b ix')
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

@pytest.mark.command(f'create tests/resources/cfg_is_not_operator.yml -k {KEY_FILE} -b ix -q')
def test_custom_targeting_is_not_reportableType(cli_config):
    assert config.custom_targeting_key_values() == \
      [{'name': 'country', 'values': {'CAN', 'US'}, 'operator': 'IS_NOT', 'reportableType': 'ON'}]
    assert config.targeting_bidder_key_config() == {'reportableType': 'ON'}

@pytest.mark.command(f'create tests/resources/cfg_video_max_duration.yml -k {KEY_FILE} -b ix -q')
def test_video_max_duration(cli_config):
    assert config.user['creative']['video']['duration'] == 60000
    assert config.user['creative']['video']['max_duration'] == 60000

@pytest.mark.command(f'create tests/resources/cfg_video_duration.yml -k {KEY_FILE} -b ix -q')
def test_video_duration(cli_config):
    assert config.user['creative']['video']['duration'] == 15000
    assert config.user['creative']['video']['max_duration'] == 30000
