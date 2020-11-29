#!/usr/bin/env python

"""Tests for `line_item_manager` package."""

from datetime import datetime, timezone
import pytest

from line_item_manager.utils import ichunk, format_long_list, date_from_string

def test_ichunk():
    assert list(ichunk(range(10), 3)) == [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]]

def test_format_long_list():
    assert format_long_list([f'abc_{i_}' for i_ in range(10)]) == \
      "['abc_0', 'abc_1', 'abc_2', ..., 'abc_7', 'abc_8', 'abc_9']"
    assert format_long_list([f'abc_{i_}' for i_ in range(4)]) == \
      "['abc_0', 'abc_1', 'abc_2', 'abc_3']"

def test_date_from_string():
    assert date_from_string('11/21/20 12:11', '%m/%d/%y %H:%M', 'UTC') == \
      datetime(2020, 11, 21, 12, 11, tzinfo=timezone.utc)
