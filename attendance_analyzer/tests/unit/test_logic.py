from datetime import date
from datetime import datetime as dt

import pytest

from attendance_analyzer import logic
from attendance_analyzer.helpers import PersonWithTime
from attendance_analyzer.logic import GroupingService
from attendance_analyzer.tests.unit.helpers import DEFAULT_DATETIME_PATTERN, FakeFile

DEFAULT_TESTING_XML = """
    <people>
        <person full_name="ivan"><start>21-12-2011 10:00:00</start><end>21-12-2011 10:01:00</end></person>
        <person full_name="ivan"><start>21-12-2011 10:01:00</start><end>21-12-2011 10:02:00</end></person>
        <person full_name="ivan"><start>21-12-2011 10:02:00</start><end>21-12-2011 10:03:00</end></person>
        <person full_name="ivan"><start>21-12-2011 10:03:00</start><end>21-12-2011 10:04:00</end></person>
        <person full_name="anna"><start>21-12-2011 10:00:00</start><end>21-12-2011 10:01:00</end></person>
        <person full_name="anna"><start>21-12-2011 10:01:00</start><end>21-12-2011 10:02:00</end></person>
        <person full_name="anna"><start>21-12-2011 10:02:00</start><end>21-12-2011 10:03:00</end></person>
        <person full_name="anna"><start>21-12-2011 10:03:00</start><end>21-12-2011 10:04:00</end></person>
    </people>
    """


def test_simple_getting_people_from_file():
    fake_file = FakeFile(
        """
    <people>
        <person full_name="ivan"><start>21-12-2011 10:54:47</start><end>21-12-2011 10:55:47</end></person>
        <person full_name="anna"><start>21-12-2011 10:54:47</start><end>21-12-2011 10:56:47</end></person>
    </people>
    """.encode()
    )
    assert list(logic.PeopleRepository(fake_file, DEFAULT_DATETIME_PATTERN).get_all_people()) == [
        PersonWithTime("ivan", dt(2011, 12, 21, 10, 54, 47), dt(2011, 12, 21, 10, 55, 47)),
        PersonWithTime("anna", dt(2011, 12, 21, 10, 54, 47), dt(2011, 12, 21, 10, 56, 47)),
    ]


@pytest.mark.parametrize(
    "test_string,datetime_regex,people_full_names,start_dt,end_dt,result",
    [
        pytest.param(
            DEFAULT_TESTING_XML,
            DEFAULT_DATETIME_PATTERN,
            None,
            None,
            None,
            [
                PersonWithTime(name, dt(2011, 12, 21, 10, minute, 0), dt(2011, 12, 21, 10, minute + 1, 0))
                for minute in (0, 1, 2, 3)
                for name in ("ivan", "anna")
            ],
            id="simple",
        ),
        pytest.param(
            DEFAULT_TESTING_XML,
            DEFAULT_DATETIME_PATTERN,
            ("ivan",),
            None,
            None,
            [
                PersonWithTime(name, dt(2011, 12, 21, 10, minute, 0), dt(2011, 12, 21, 10, minute + 1, 0))
                for minute in (0, 1, 2, 3)
                for name in ("ivan",)
            ],
            id="filter out anna",
        ),
        pytest.param(
            DEFAULT_TESTING_XML,
            DEFAULT_DATETIME_PATTERN,
            None,
            dt(2011, 12, 21, 10, 2, 0),
            None,
            [
                PersonWithTime(name, dt(2011, 12, 21, 10, minute, 0), dt(2011, 12, 21, 10, minute + 1, 0))
                for minute in (2, 3)
                for name in ("ivan", "anna")
            ],
            id="filter from 2011-12-21 10:02",
        ),
        pytest.param(
            DEFAULT_TESTING_XML,
            DEFAULT_DATETIME_PATTERN,
            ("ivan",),
            dt(2011, 12, 21, 10, 2, 0),
            None,
            [
                PersonWithTime(name, dt(2011, 12, 21, 10, minute, 0), dt(2011, 12, 21, 10, minute + 1, 0))
                for minute in (2, 3)
                for name in ("ivan",)
            ],
            id="filter from 2011-12-21 10:02 for ivan",
        ),
        pytest.param(
            DEFAULT_TESTING_XML,
            DEFAULT_DATETIME_PATTERN,
            None,
            dt(2011, 12, 21, 10, 1, 0),
            dt(2011, 12, 21, 10, 2, 0),
            [
                PersonWithTime(name, dt(2011, 12, 21, 10, minute, 0), dt(2011, 12, 21, 10, minute + 1, 0))
                for minute in (1,)
                for name in ("ivan", "anna")
            ],
            id="filter from 2011-12-21 10:01 to 2011-12-21 10:02",
        ),
        pytest.param(
            """
            <people>
                <person full_name="ivan"><start>21-12-2011 10:00:00</start><end>21-12-2011 23:59:59</end></person>
                <person full_name="ivan"><start>21-12-2011 0:0:00</start><end>21-12-2011 23:59:59</end></person>
            </people>
            """,
            DEFAULT_DATETIME_PATTERN,
            None,
            dt(2011, 12, 21),
            dt(2011, 12, 21, 23, 59, 59, 999999),
            [
                PersonWithTime("ivan", dt(2011, 12, 21, 10, 0, 0), dt(2011, 12, 21, 23, 59, 59)),
                PersonWithTime("ivan", dt(2011, 12, 21), dt(2011, 12, 21, 23, 59, 59)),
            ],
            id="filter from 2011-12-21 0:00:00 to 2011-12-21 23:59:59.999999",
        ),
    ],
)
def test_getting_people_from_file_with_params(test_string, datetime_regex, people_full_names, start_dt, end_dt, result):
    assert set(
        logic.PeopleRepository(FakeFile(test_string.encode()), datetime_regex).get_filtered_people(
            people_full_names, start_dt, end_dt
        )
    ) == set(result)


def test_grouping_by_day():
    service = GroupingService(
        [
            PersonWithTime(name, dt(2011, 12, day, 10, 0, 0), dt(2011, 12, day, 10, 15, 0))
            for day in (1, 2, 3)
            for name in ("ivan", "anna")
        ]
    )
    assert service.group_people_with_time_by_day() == {
        date(2011, 12, 1): 1800,
        date(2011, 12, 2): 1800,
        date(2011, 12, 3): 1800,
    }


def test_grouping_by_day_and_person():
    service = GroupingService(
        [
            PersonWithTime(name, dt(2011, 12, day, 10, 0, 0), dt(2011, 12, day, 10, 15, 0))
            for day in (1, 2, 3)
            for name in ("ivan", "anna")
        ]
    )
    assert service.group_people_with_time_by_person_and_day() == {
        (date(2011, 12, day), name): 900 for day in (1, 2, 3) for name in ("ivan", "anna")
    }
