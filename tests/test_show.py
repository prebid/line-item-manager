import os.path
import shlex

from click.testing import CliRunner
import pytest

import line_item_manager
from line_item_manager import cli

CONF_DIR = os.path.join(os.path.dirname(line_item_manager.__file__), 'conf.d')

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

@pytest.mark.parametrize("command, filename",
 [
  ('config', 'line_item_manager.yml'),
  ('template', 'line_item_template.yml'),
  ('settings', 'settings.yml'),
  ('schema', 'schema.yml'),
 ]
)
def test_cli_show_package_file(command, filename):
    runner = CliRunner()
    result = runner.invoke(
        cli.show,
        shlex.split(command)
    )
    assert result.exit_code == 0
    with open(os.path.join(CONF_DIR, filename)) as fp:
        assert result.output == fp.read() + '\n'
