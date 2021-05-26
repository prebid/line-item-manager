#!/usr/bin/env python

"""Tests for `line_item_manager` package."""

import yaml

from line_item_manager.yaml_date import date_from_string
from jinja2 import Template as J2Template

def test_yaml_tz():
    dt = date_from_string('11/21/20 12:11', '%m/%d/%y %H:%M', 'Europe/Oslo')
    obj = yaml.safe_load(yaml.safe_dump({'dt': dt}))
    assert obj['dt'].tzinfo.zone == 'Europe/Oslo'

def test_jinja_tz():
    dt = date_from_string('11/21/20 12:11', '%m/%d/%y %H:%M', 'Europe/Oslo')
    obj = yaml.safe_load(J2Template("dt: {{ dt }}").render(dt=dt))
    assert obj['dt'].tzinfo.zone == 'Europe/Oslo'
