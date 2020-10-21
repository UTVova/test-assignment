from click.testing import CliRunner

from attendance_analyzer.__main__ import main


def test_output_without_grouping():
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

        runner.invoke(main, ["-in", "custom.xml", "-out", "out.csv"])
        with open("out.csv") as f:
            assert ["date,duration", "21-12-2011,2:00:00", "22-12-2011,15:00:00"] == f.read().split()


def test_output_with_grouping():
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open("custom.xml", "w") as f:
            f.write(
                """<people>
                <person full_name="ivan"><start>21-12-2011 10:00:00</start><end>21-12-2011 12:00:00</end></person>
                <person full_name="anna"><start>22-12-2011 0:0:00</start><end>22-12-2011 15:00:00</end></person>
                <person full_name="ivan"><start>23-12-2011 10:00:00</start><end>23-12-2011 12:00:00</end></person>
                <person full_name="anna"><start>24-12-2011 0:0:00</start><end>24-12-2011 15:00:00</end></person>
            </people>"""
            )
        result = runner.invoke(main, ["-in", "custom.xml", "-out", "-", "--group-employees"])
        desirable_output = [
            "date,name,duration",
            "21-12-2011,ivan,2:00:00",
            "22-12-2011,anna,15:00:00",
            "23-12-2011,ivan,2:00:00",
            "24-12-2011,anna,15:00:00",
        ]
        assert desirable_output == result.stdout.split()

        runner.invoke(main, ["-in", "custom.xml", "-out", "one_more.csv", "--group-employees"])
        with open("one_more.csv") as f:
            assert desirable_output == f.read().split()
