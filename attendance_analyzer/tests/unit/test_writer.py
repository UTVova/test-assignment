import sys
from datetime import date

import pytest

from attendance_analyzer.writer import CSVWriter


@pytest.fixture(scope="module")
def csv_writer():
    return CSVWriter(sys.stdout)


@pytest.mark.parametrize(
    "_dict,output_as_list",
    [
        ({date(2020, 1, 1): 60}, ["01-01-2020,0:01:00"]),
        ({date(2020, 1, 1): 60, date(2020, 1, 2): 90350}, ["01-01-2020,0:01:00", '02-01-2020,"1 day, 1:05:50"']),
    ],
)
def test_write_out_date_to_duration_in_seconds_mapping(capsys, _dict, output_as_list):
    writer = CSVWriter(sys.stdout)
    writer.write_out_date_to_duration_in_seconds_mapping(_dict)
    out = capsys.readouterr().out.split("\r\n")
    assert ["date,duration", *output_as_list] == list(filter(str.__len__, out))  # filter out empty strings


@pytest.mark.parametrize(
    "_dict,output_as_list",
    [
        ({(date(2020, 1, 1), "ivan"): 60}, ["01-01-2020,ivan,0:01:00"]),
        ({(date(2020, 1, 1), "anna"): 3600}, ["01-01-2020,anna,1:00:00"]),
        (
            {(date(2020, 1, 1), "ivan"): 60, (date(2020, 1, 2), "anna"): 90350},
            ["01-01-2020,ivan,0:01:00", '02-01-2020,anna,"1 day, 1:05:50"'],
        ),
        pytest.param(
            {(date(2020, 1, 3), "ivan"): 60, (date(2020, 1, 2), "anna"): 60, (date(2020, 1, 1), "anna"): 60},
            ["01-01-2020,anna,0:01:00", "02-01-2020,anna,0:01:00", "03-01-2020,ivan,0:01:00"],
            id="sorted",
        ),
    ],
)
def test_write_out_person_and_date_to_duration_in_seconds_mapping(capsys, _dict, output_as_list):
    writer = CSVWriter(sys.stdout)
    writer.write_out_person_and_date_to_duration_in_seconds_mapping(_dict)
    out = capsys.readouterr().out.split("\r\n")
    assert ["date,name,duration", *output_as_list] == list(filter(str.__len__, out))  # filter out empty strings
