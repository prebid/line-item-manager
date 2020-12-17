import shlex

from click.testing import CliRunner
import pytest

from line_item_manager import cli

@pytest.mark.parametrize("command, echo_str",
 [
  ('--version', 'line-item-manager version'),
  ('', '[OPTIONS] COMMAND [ARGS]'),
 ]
)
def test_version(command, echo_str):
    runner = CliRunner()
    result = runner.invoke(
        cli.cli,
        shlex.split(command)
    )
    assert result.exit_code == 0
    assert echo_str in result.output
