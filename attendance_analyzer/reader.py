import datetime as dt
import typing
from xml.etree import ElementTree as ETree

from .helpers import PersonWithTime, parse_datetime

__all__ = (
    "UnknownPersonFullNameException",
    "UnrecognizableDateTimeException",
    "WrongStructureOfFileException",
    "WrongTimeException",
    "PeopleReader",
    "XMLPeopleReader",
)

EVENT_START, EVENT_END = "start", "end"
TAG_START, TAG_END, TAG_PERSON, TAG_PEOPLE = "start", "end", "person", "people"

FilePath = str


class UnknownPersonFullNameException(Exception):
    pass


class UnrecognizableDateTimeException(Exception):
    def __init__(self, pattern: str, text: str):
        super().__init__()
        self.pattern = pattern
        self.text = text


class WrongStructureOfFileException(Exception):
    pass


class WrongTimeException(Exception):
    def __init__(self, text: str):
        super().__init__()
        self.text = text


class PeopleReader:
    def __init__(self, filename: typing.Union[FilePath, typing.IO], datetime_regex: str):
        self._filename = filename
        self._datetime_regex = datetime_regex

    def read_attendance(self) -> typing.Iterable[PersonWithTime]:
        raise NotImplementedError


class XMLPeopleReader(PeopleReader):
    def read_attendance(self) -> typing.Iterable[PersonWithTime]:
        """
        Used to read and convert given source(path or file) with xml to collection of PersonWithTime
        :raises xml.etree.ElementTree.ParseError when parsing has gone wrong
        :raises UnrecognizableDateTime when datetime_regex couldn't be used to match datetime in start or end tag
        :raises UnknownPersonFullNameException when person tag has no full_name attribute
        :raises StopIteration when people tag is not closed
        :raises WrongFormatOfFileException when format of given xml file is wrong
        :raises WrongTimeException when time in <start> comes after time in <end>
        """
        # use iterparse not to load the whole ElementTree and to read tags as they're parsed
        xml = ETree.iterparse(self._filename, events=(EVENT_START, EVENT_END))
        element: ETree.Element
        person_full_name: typing.Optional[str] = None
        start_time: typing.Optional[dt.datetime] = None
        end_time: typing.Optional[dt.datetime] = None
        while True:
            event, element = next(xml)
            if element.tag == TAG_PERSON:
                if event == EVENT_START:
                    start_time: typing.Optional[dt.datetime] = None
                    end_time: typing.Optional[dt.datetime] = None
                    person_full_name = element.attrib.get("full_name", None)

                    if person_full_name is None:
                        raise UnknownPersonFullNameException

                elif event == EVENT_END:  # <person> closed
                    if any(attr is None for attr in (person_full_name, start_time, end_time)):
                        raise WrongStructureOfFileException

                    if start_time > end_time:
                        raise WrongTimeException(
                            f"Time in start tag ({start_time.strftime('%d-%m-%Y %H:%M:%S')}) "
                            f"cannot come after time in end tag({end_time.strftime('%d-%m-%Y %H:%M:%S')})."
                        )

                    yield PersonWithTime(person_full_name, start_time, end_time)
                    # clear <person> and its children
                    element.clear()

            elif element.tag == TAG_START:
                text = element.text if element.text else ""
                try:
                    start_time = parse_datetime(text, self._datetime_regex)
                except ValueError:
                    raise UnrecognizableDateTimeException(self._datetime_regex, text)

            elif element.tag == TAG_END and event == EVENT_END:
                text = element.text if element.text else ""
                try:
                    end_time = parse_datetime(text, self._datetime_regex)
                except ValueError:
                    raise UnrecognizableDateTimeException(self._datetime_regex, text)

            elif element.tag == TAG_PEOPLE and event == EVENT_END:
                break
