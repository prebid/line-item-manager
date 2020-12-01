import shlex

from click.testing import CliRunner
import pytest

from line_item_manager import cli

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

