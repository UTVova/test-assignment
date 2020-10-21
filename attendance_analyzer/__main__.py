import datetime as dt
import os
import sys
import typing
from xml.etree.ElementTree import ParseError

import click

from attendance_analyzer.reader import XMLPeopleReader

from . import reader
from .helpers import PersonWithTime, parse_datetime
from .logic import GroupingService, PeopleRepository
from .writer import CSVWriter


@click.command(help="Command analyzes attendance of employees basing on xml-file.")
@click.option("--input", "-in", "filename", type=click.Path(exists=True, dir_okay=False), default=os.getenv("input"))
@click.option("--output", "-out", type=click.File("w"), default=os.getenv("output"))
@click.option("--group-employees", "group", is_flag=True, help="Flag for grouping by employees.", default=False)
@click.option(
    "--filter-person",
    "people_to_filter",
    help="Filter records against given full_name. Option may be used multiple times.",
    multiple=True,
)
@click.option(
    "--start-date",
    "start_date",
    help="Filter records against given starting date matching '%d-%m-%Y'.",
)
@click.option(
    "--end-date",
    "end_date",
    help="Filter records against given ending date matching '%d-%m-%Y'.",
)
@click.option(
    "--regex", "datetime_regex", default="%d-%m-%Y %H:%M:%S", help="Regular expression to use for parsing datetime."
)
def main(
    filename: str,
    group: bool,
    datetime_regex: str,
    output: typing.TextIO,
    people_to_filter: tuple,
    start_date: typing.Optional[str] = None,
    end_date: typing.Optional[str] = None,
):
    try:
        start_dt = parse_datetime(start_date, "%d-%m-%Y") if start_date else None
    except ValueError:
        raise click.BadOptionUsage("start_date", "Provided start date does not match '%d-%m-%Y'.")
    try:
        end_dt = dt.datetime.combine(parse_datetime(end_date, "%d-%m-%Y"), dt.time.max) if end_date else None
    except ValueError:
        raise click.BadOptionUsage("end_date", "Provided end date does not match '%d-%m-%Y'.")

    repository = PeopleRepository(reader_obj=XMLPeopleReader(filename, datetime_regex))
    filtered_people_with_full_name_and_time: typing.Iterable[PersonWithTime] = repository.get_filtered_people(
        people_to_filter, start_dt, end_dt
    )
    try:
        grouping_service = GroupingService(filtered_people_with_full_name_and_time)
        csv_writer = CSVWriter(output)
        if group:
            person_date_to_duration_mapping: dict[
                typing.Tuple[dt.date, str], int
            ] = grouping_service.group_people_with_time_by_person_and_day()

            csv_writer.write_out_person_and_date_to_duration_in_seconds_mapping(person_date_to_duration_mapping)
        else:
            date_to_duration_mapping: typing.DefaultDict[
                dt.date, int
            ] = grouping_service.group_people_with_time_by_day()

            csv_writer.write_out_date_to_duration_in_seconds_mapping(date_to_duration_mapping)
    except reader.UnknownPersonFullNameException:
        raise click.ClickException("Attribute full_name is not found in tag person.")
    except reader.UnrecognizableDateTimeException as e:
        raise click.ClickException(f"'{e.text}' does not match datetime pattern '{e.pattern}'.")
    except reader.WrongStructureOfFileException:
        raise click.ClickException("Wrong structure of the given file.")
    except reader.WrongTimeException as e:
        raise click.ClickException(e.text)
    except (ParseError, Exception):
        raise click.BadArgumentUsage(f"Impossible to parse {filename}.")


if __name__ == "__main__":
    sys.exit(main(prog_name="attendance_analyzer"))
