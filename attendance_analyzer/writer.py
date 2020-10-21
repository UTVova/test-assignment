import csv
import datetime as dt
import typing


class CSVWriter:
    def __init__(self, output):
        self._output: typing.IO = output
        self._writer = None

    def _write_to_csv(self, rows: typing.Iterable[str]):
        if not self._writer:
            self._writer = csv.writer(self._output)
        self._writer.writerows(rows)

    def write_out_person_and_date_to_duration_in_seconds_mapping(
        self, person_date_to_duration_in_sec: dict[typing.Tuple[dt.date, str], int]
    ):
        header = ("date", "name", "duration")
        rows = (
            (date.strftime("%d-%m-%Y"), name, str(dt.timedelta(seconds=person_date_to_duration_in_sec[(date, name)])))
            for date, name in sorted(person_date_to_duration_in_sec.keys())
        )
        self._write_to_csv(
            (
                header,
                *rows,
            )
        )

    def write_out_date_to_duration_in_seconds_mapping(self, date_to_duration_in_sec_mapping: dict[dt.date, int]):
        header = ("date", "duration")
        rows = (
            (date.strftime("%d-%m-%Y"), str(dt.timedelta(seconds=date_to_duration_in_sec_mapping[date])))
            for date in sorted(date_to_duration_in_sec_mapping.keys())
        )
        self._write_to_csv(
            (
                header,
                *rows,
            )
        )
