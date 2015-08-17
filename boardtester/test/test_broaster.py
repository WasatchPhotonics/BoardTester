""" 
##################
Not getting full coverage?
Remember that this program is designed to test failing hardware. As
such, you need the test device to be in a known functioning state in
order to cover all the conditions.

Specifically, the tests assume you have a correctly operating phidget
relay connected to the device. See the Phidgeter module for tests to
make sure the device is accessible.

##################
"""

import unittest
import sys

from boardtester import broaster

class Test(unittest.TestCase):

    def setUp(self):
        self.usage_str = "usage: python broaster.py"
        self.usage_str += " --iterations N --description \"text\""
        self.usage_str += "\n"
        self.usage_str += "Where N is a number 0-10000\n"
        self.usage_str += "And text is phrase in quotes\n"

    
    def test_run_broaster(self):
        # First check the utils can be used to print the important
        # colored ascii logo
        self.exam_iter = 1
        self.exam_desc = "run broaster test"
        self.sae = broaster.WasatchBroaster_Exam(self.exam_desc)

        butil = broaster.BroasterUtils()
        result = butil.colorama_broaster()
        # Look for the bottom of the ROASTER chars
        self.assertTrue(" \_\|___/  |_| |___|_|_\\" in result)

        self.sae.run(self.exam_iter)

    def test_force_exceptions(self):

        self.exam_iter = 1
        self.exam_desc = "force exceptions test"

        # Setup the exam, but do not run it
        self.sae = broaster.WasatchBroaster_Exam(self.exam_desc)

        # Check if the fail string is in the exception caught return
        # string
        result = self.sae.disconnect(1)
        self.assertTrue("Error disconnect" in result)

        # Get revision on an unopened device triggers exception
        result = self.sae.revision_info(1)
        self.assertTrue("Error get revision" in result)
         
        result = self.sae.lines_info(1)
        self.assertTrue("Error lines info" in result)
    
    def test_process_results(self):
        self.proc = broaster.ProcessBroaster()

        exam_description = "unfindable"
        result = self.proc.find_log(exam_description) 
        self.assertFalse(result) 

        # Now copy over a known exam result file, and make sure it can
        # be found
        
 
if __name__ == "__main__":
    unittest.main()
