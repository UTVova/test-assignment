from __future__ import annotations

import datetime as dt
import typing
from collections import defaultdict
from functools import partial

from .helpers import PersonWithTime
from .reader import PeopleReader, XMLPeopleReader

FilePath = str


class PeopleRepository:
    def __init__(
        self,
        filename: typing.Optional[typing.Union[FilePath, typing.IO]] = None,
        datetime_regex: typing.Optional[str] = None,
        reader_obj: typing.Optional[PeopleReader] = None,
    ):
        assert (filename is not None and datetime_regex is not None) or reader_obj
        self._filename = filename
        self._datetime_regex = datetime_regex
        self._reader = reader_obj if reader_obj else XMLPeopleReader(filename, datetime_regex)
        self._people: typing.Optional[typing.Iterable[PersonWithTime]] = None

    @staticmethod
    def _filter_person_against_full_names_and_datetime(
        person: PersonWithTime,
        full_names_for_filtering: set,
        start_dt: typing.Optional[dt.datetime] = None,
        end_dt: typing.Optional[dt.datetime] = None,
    ) -> bool:
        if full_names_for_filtering and person.full_name not in full_names_for_filtering:
            return False  # skip further checks
        elif start_dt and start_dt > person.start:
            return False
        elif end_dt and end_dt < person.end:
            return False
        return True

    def get_all_people(self) -> typing.Iterable[PersonWithTime]:
        if self._people is None:
            self._people = self._reader.read_attendance()
        return self._people

    def get_filtered_people(
        self,
        people_full_names: typing.Optional[typing.Tuple[str]] = None,
        start_dt: typing.Optional[dt.datetime] = None,
        end_dt: typing.Optional[dt.datetime] = None,
    ) -> typing.Iterable[PersonWithTime]:
        return filter(
            partial(
                self._filter_person_against_full_names_and_datetime,
                full_names_for_filtering=set(people_full_names) if people_full_names else set(),
                start_dt=start_dt,
                end_dt=end_dt,
            ),
            self.get_all_people(),
        )


class GroupingService:
    def __init__(self, people: typing.Iterable[PersonWithTime]):
        self._people = people

    def group_people_with_time_by_day(self) -> typing.DefaultDict[dt.date, int]:
        """People are grouped by day"""
        result: typing.DefaultDict[dt.date, int] = defaultdict(int)
        for person_with_time in self._people:
            result[person_with_time.start.date()] += int(
                (person_with_time.end - person_with_time.start).total_seconds()
            )
        return result

    def group_people_with_time_by_person_and_day(self) -> dict[typing.Tuple[dt.date, str], int]:
        """People are grouped by full_name from tag and day"""
        result: dict[typing.Tuple[dt.date, str], int] = defaultdict(int)
        for person_with_time in self._people:
            result[(person_with_time.start.date(), person_with_time.full_name)] += int(
                (person_with_time.end - person_with_time.start).total_seconds()
            )
        return result
