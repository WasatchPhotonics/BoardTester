""" Simplistic functions for replacing html components with data to be rendered.
"""

class SimpleReport(object):
    def __init__(self, filename="test_file.html"):
        self.template_file = "reports/templates/analyze.html"
        self.template = ""
        self.output_file = filename

        with open(self.template_file) as in_file:
            for new_line in in_file.readlines():
                self.template += new_line

        #print "full template ", self.template

    def replace(self, template_str, new_str):
        self.template = self.template.replace(template_str, new_str)

    def write(self):
        with open(self.output_file, "wb") as out_file:
            out_file.writelines(self.template)

