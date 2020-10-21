from datetime import datetime as dt

import pytest

from attendance_analyzer import helpers


def test_parse_datetime():
    assert helpers.parse_datetime("02-01-2020 03:04:05", "%d-%m-%Y %H:%M:%S") == dt(2020, 1, 2, 3, 4, 5)


def test_parse_datetime_raises_value_error_with_wrong_text_for_parsing():
    with pytest.raises(ValueError):
        assert helpers.parse_datetime("DOES NOT MATCH", "%d-%m-%Y %H:%M:%S")


def test_parse_datetime_raises_value_error_with_not_matching_pattern():
    with pytest.raises(ValueError):
        assert helpers.parse_datetime("02-01-2020 03:04:05", "%d-%m-%Y")
