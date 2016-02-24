""" Tests for simplistic html visualization of report data.
"""


from boardtester import reporter

class TestHTMLReport:

    def test_replace_pixel_number_axis(self):
        rep = reporter.SimpleReport()

        number_axis = range(0, 511)
        rep.replace("time_labels", number_axis)

        rep.write("test_file.html")

        slurp_file = ""
        with open("test_file.html") as input_file:
            slurp_file = input_file.readlines()

        assert "labels: [0, 1, 2" in slurp_file
        assert "509, 510, 511]," in slurp_file
