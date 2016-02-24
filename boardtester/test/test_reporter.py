""" Tests for simplistic html visualization of report data.
"""


from boardtester import reporter

class TestHTMLReport:

    def test_replace_pixel_number_axis(self):
        rep = reporter.SimpleReport()

        number_axis = range(0, 512)
        str_axis = str(number_axis)
        str_axis = str_axis.replace("[", "")
        str_axis = str_axis.replace("]", "")
        rep.replace("${time_labels}", str_axis)

        rep.write()

        slurp_file = ""

        with open("test_file.html") as in_file:
            for new_line in in_file.readlines():
                slurp_file += new_line

        assert "labels: [0, 1, 2" in slurp_file
        assert "509, 510, 511]," in slurp_file

    def test_replace_single_line(self):

        rep = reporter.SimpleReport()

        pixel_data = range(0, 512)
        str_axis = str(pixel_data)
        str_axis = str_axis.replace("[", "")
        str_axis = str_axis.replace("]", "")
        rep.replace("${pixel_data}", str_axis)

        rep.write()

        slurp_file = ""

        with open("test_file.html") as in_file:
            for new_line in in_file.readlines():
                slurp_file += new_line

        assert "data: [0, 1, 2" in slurp_file
        assert "509, 510, 511]," in slurp_file

    def test_both_replacements(self):
        rep = reporter.SimpleReport()

        number_axis = range(0, 512)
        str_axis = str(number_axis)
        str_axis = str_axis.replace("[", "")
        str_axis = str_axis.replace("]", "")
        rep.replace("${time_labels}", str_axis)

        pixel_data = range(0, 512)
        str_axis = str(pixel_data)
        str_axis = str_axis.replace("[", "")
        str_axis = str_axis.replace("]", "")
        rep.replace("${pixel_data}", str_axis)

        rep.write()

        slurp_file = ""

        with open("test_file.html") as in_file:
            for new_line in in_file.readlines():
                slurp_file += new_line

        assert "data: [0, 1, 2" in slurp_file
        assert "509, 510, 511]," in slurp_file

        assert "labels: [0, 1, 2" in slurp_file
        assert "509, 510, 511]," in slurp_file
