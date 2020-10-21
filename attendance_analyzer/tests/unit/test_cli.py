from datetime import datetime

from click.testing import CliRunner
from pytest_mock import MockerFixture

from attendance_analyzer.__main__ import main


def test_main_basic_run(capsys):
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open("custom.xml", "w") as f:
            f.write(
                """<people>
                    <person full_name="ivan"><start>21-12-2011 10:00:00</start><end>21-12-2011 12:00:00</end></person>
                    <person full_name="anna"><start>22-12-2011 0:0:00</start><end>22-12-2011 15:00:00</end></person>
                </people>"""
            )
        result = runner.invoke(main, ["-in", "custom.xml", "-out", "-"])
    assert ["date,duration", "21-12-2011,2:00:00", "22-12-2011,15:00:00"] == result.stdout.split()


def test_filename_usage(mocker: MockerFixture):
    init_method = mocker.patch("attendance_analyzer.reader.XMLPeopleReader.__init__")
    runner = CliRunner()
    with runner.isolated_filesystem(), open("custom.xml", "w"):
        CliRunner().invoke(main, ["-in", "custom.xml", "-out", "-"])
    init_method.assert_called_with("custom.xml", "%d-%m-%Y %H:%M:%S")


def test_datetime_regex_usage(mocker: MockerFixture):
    init_method = mocker.patch("attendance_analyzer.reader.XMLPeopleReader.__init__")
    runner = CliRunner()
    with runner.isolated_filesystem(), open("custom.xml", "w"):
        CliRunner().invoke(main, ["-in", "custom.xml", "-out", "-", "--regex", "%Y-%m-%d %H:%M:%S"])
    init_method.assert_called_with("custom.xml", "%Y-%m-%d %H:%M:%S")


def test_bad_start_date():
    runner = CliRunner()
    with runner.isolated_filesystem(), open("custom.xml", "w"):
        result = CliRunner().invoke(main, ["-in", "custom.xml", "-out", "-", "--start-date", "WRONG"])
    assert "Provided start date does not match '%d-%m-%Y'." in result.stdout


def test_bad_end_date():
    runner = CliRunner()
    with runner.isolated_filesystem(), open("custom.xml", "w"):
        result = runner.invoke(main, ["-in", "custom.xml", "-out", "-", "--end-date", "WRONG"])
    assert "Provided end date does not match '%d-%m-%Y'." in result.stdout


def test_start_date_usage(mocker: MockerFixture):
    method = mocker.patch("attendance_analyzer.logic.PeopleRepository.get_filtered_people")
    runner = CliRunner()
    with runner.isolated_filesystem(), open("custom.xml", "w"):
        runner.invoke(main, ["-in", "custom.xml", "-out", "-", "--start-date", "12-12-2020"])
    method.assert_called_with((), datetime(2020, 12, 12, 0, 0, 0), None)


def test_end_date_usage(mocker: MockerFixture):
    method = mocker.patch("attendance_analyzer.logic.PeopleRepository.get_filtered_people")
    runner = CliRunner()
    with runner.isolated_filesystem(), open("custom.xml", "w"):
        runner.invoke(main, ["-in", "custom.xml", "-out", "-", "--end-date", "12-12-2020"])
    method.assert_called_with((), None, datetime(2020, 12, 12, 23, 59, 59, 999999))


def test_people_to_filter(mocker: MockerFixture):
    method = mocker.patch("attendance_analyzer.logic.PeopleRepository.get_filtered_people")
    runner = CliRunner()
    with runner.isolated_filesystem(), open("custom.xml", "w"):
        runner.invoke(main, ["-in", "custom.xml", "-out", "-", "--filter-person", "a", "--filter-person", "b"])
    method.assert_called_with(("a", "b"), None, None)


def test_group(mocker: MockerFixture):
    method = mocker.patch("attendance_analyzer.logic.GroupingService.group_people_with_time_by_person_and_day")
    runner = CliRunner()
    with runner.isolated_filesystem(), open("custom.xml", "w"):
        runner.invoke(main, ["-in", "custom.xml", "-out", "-", "--group-employees"])
    method.assert_called_once()


def test_not_group(mocker: MockerFixture):
    method = mocker.patch("attendance_analyzer.logic.GroupingService.group_people_with_time_by_day")
    runner = CliRunner()
    with runner.isolated_filesystem(), open("custom.xml", "w"):
        runner.invoke(main, ["-in", "custom.xml", "-out", "-"])
    method.assert_called_once()
