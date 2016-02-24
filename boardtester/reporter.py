""" Simplistic functions for replacing html components with data to be rendered.
"""

class SimpleReport(object):
    def __init__(self, filename="test_file.html"):
        self.filename = filename
        self.template = ""

        with open(self.template_file) as in_file:
            self.template = in_file.readlines()

    def replace(self, template_str, new_str):
        self.template.replace(template_str, new_str)
