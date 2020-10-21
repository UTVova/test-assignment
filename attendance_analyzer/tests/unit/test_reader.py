from datetime import datetime as dt
from xml.etree.ElementTree import ParseError

import pytest

from attendance_analyzer import reader
from attendance_analyzer.helpers import PersonWithTime
from attendance_analyzer.reader import WrongTimeException, XMLPeopleReader
from attendance_analyzer.tests.unit.helpers import DEFAULT_DATETIME_PATTERN, FakeFile


def test_reader_returns_people_with_time():
    fake_file = FakeFile(
        """
    <people>
        <person full_name="ivan"><start>21-12-2011 10:54:47</start><end>21-12-2011 10:55:47</end></person>
        <person full_name="anna"><start>21-12-2011 10:54:47</start><end>21-12-2011 10:56:47</end></person>
    </people>
    """.encode()
    )
    assert list(XMLPeopleReader(fake_file, DEFAULT_DATETIME_PATTERN).read_attendance()) == [
        PersonWithTime("ivan", dt(2011, 12, 21, 10, 54, 47), dt(2011, 12, 21, 10, 55, 47)),
        PersonWithTime("anna", dt(2011, 12, 21, 10, 54, 47), dt(2011, 12, 21, 10, 56, 47)),
    ]


def test_reader_returns_people_with_time_with_changed_datetime_pattern():
    fake_file = FakeFile(
        """
    <people>
        <person full_name="ivan"><start>2011-21-12 10:54:47</start><end>2011-21-12 10:55:47</end></person>
        <person full_name="anna"><start>2011-21-12 10:54:47</start><end>2011-21-12 10:56:47</end></person>
    </people>
    """.encode()
    )
    assert list(XMLPeopleReader(fake_file, "%Y-%d-%m %H:%M:%S").read_attendance()) == [
        PersonWithTime("ivan", dt(2011, 12, 21, 10, 54, 47), dt(2011, 12, 21, 10, 55, 47)),
        PersonWithTime("anna", dt(2011, 12, 21, 10, 54, 47), dt(2011, 12, 21, 10, 56, 47)),
    ]


@pytest.mark.parametrize(
    "text,exception_class",
    [
        pytest.param(
            """<people>
                <person full_name="ivan"><start>21-12-2011 10:54:47</start><end>21-12-2011 10:55</end></person>
            </people>""",
            reader.UnrecognizableDateTimeException,
            id="no seconds in end",
        ),
        pytest.param(
            """<people>
            <person><start>21-12-2011 10:54:47</start><end>21-12-2011 10:55:47</end>
            </person>""",
            reader.UnknownPersonFullNameException,
            id="no </people>",
        ),
        pytest.param(
            """<people>
            <person full_name="ivan"><start>21-12-2011 10:54:47</start><end>21-12-2011 10:55:47</person>
            </people>""",
            ParseError,
            id="no </end>",
        ),
        pytest.param(
            """<people>
            <person full_name="ivan"><start>21-12-2011 10:54:47</start></person>
            </people>""",
            reader.WrongStructureOfFileException,
            id="no end",
        ),
        pytest.param(
            """<people>
            <person full_name="ivan"><start>21-12-2011 10:54:47</start><end>21-12-2011 10:55:47</end>
            </people>""",
            ParseError,
            id="no </person>",
        ),
        pytest.param(
            """<people>
            <person full_name="ivan"><start></start><end>21-12-2011 10:55:47</end></person>
            </people>""",
            reader.UnrecognizableDateTimeException,
            id="empty start",
        ),
        pytest.param("""<pepe""", ParseError, id="strange tag"),
        pytest.param(
            """<people>
            <person full_name="ivan"><start>01-01-2020 10:00:00</start><end>01-01-2000 10:00:00</end></person>
            </people>""",
            WrongTimeException,
            id="wrong time in tags",
        ),
    ],
)
def test_reader_raises_on_wrong_format_of_people(text, exception_class):
    with pytest.raises(exception_class):
        list(XMLPeopleReader(FakeFile(text.encode()), DEFAULT_DATETIME_PATTERN).read_attendance())
