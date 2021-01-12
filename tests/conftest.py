from datetime import datetime
import shlex

import pytest

from line_item_manager import cli
from line_item_manager.config import config
from line_item_manager.gam_operations import client as gam_client

def pytest_configure():
    pytest.start_time = datetime(2020, 1, 2, 8, 9, 10)

@pytest.fixture
def cli_config(request):
    # patch
    cli_str = request.node.get_closest_marker('command').args[0]
    cli_args = shlex.split(cli_str)
    cmd = cli_args[0]
    ctx = cli.create.make_context(cmd, cli_args[1:])
    if cmd == 'create':
        configfile = ctx.params.pop('configfile')
        config.cli = ctx.params
        config.set_user_configfile(configfile)
        config.set_client_factory(gam_client)
        config.pre_create()
        return dict(
            ctx=ctx,
            configfile=configfile,
            kwargs=ctx.params,
        )
    if cmd == 'show':
        resource = ctx.params.pop('resource')
        return dict(
            ctx=ctx,
            resource=resource,
            kwargs=ctx.params
        )
    return None
