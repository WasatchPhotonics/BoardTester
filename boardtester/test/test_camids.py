""" 
Verify functionality of camids command line tool.
"""

import unittest
import sys
import os
import shutil
import time

from boardtester import camids

class Test(unittest.TestCase):

    def setUp(self):
        # Clean any old directories
        self.exam_iter = 1
        self.exam_desc = "run camids test"

    
    def test_color_camids(self):
        # First check the utils can be used to print the important
        # colored ascii logo
        camutil = camids.CamIDSUtils()
        result = camutil.colorama_camids()

        # Look for the bottom of the CAMIDS text
        #print "result \n%s" % result
        self.assertTrue("|_____|_____/|_____/" in result)


    def test_ueye_available(self):
        # Convenience test to verify that uEye software is installed on
        # the system
        ueye_exec = "C:\Program Files\IDS\uEye\Program\uEyeCockpit.exe"
        result = os.path.isfile(ueye_exec)
        self.assertTrue(result)

    def test_click_mouse(self):
        # Given a random coordinate, move the mouse there, click the
        # button. Use the start menu in the lower left, verify that the
        # start menu appears
        self.ids = camids.WasatchCamIDS_Exam(self.exam_desc)
        result = self.ids.move_and_click(10, 1060, wait_interval=1)
        self.assertTrue(result)

    def test_start_stop_ueye(self):
        self.ids = camids.WasatchCamIDS_Exam(self.exam_desc)

        # List the current running processes, make sure ueye is not one
        # of them
        self.assertFalse(self.ids.check_for_ueye())

        # Start ueye
        self.assertTrue(self.ids.start_ueye())

        # Make sure ueye is running
        self.assertTrue(self.ids.check_for_ueye())

        # Stop ueye
        self.assertTrue(self.ids.stop_ueye())
        time.sleep(5)

        # List the current running processes, make sure ueye is not one
        # of them
        self.assertFalse(self.ids.check_for_ueye())

    def test_screenshot(self):
        # Take a screenshot of the screen, verify it is good by being at
        # least N bytes
        self.ids = camids.WasatchCamIDS_Exam(self.exam_desc)

        filename = "test_screenshot.png"
        self.assertTrue(self.ids.save_screenshot(filename))
        result = os.path.isfile(filename)
        self.assertTrue(result)

        size = os.path.getsize(filename)
        self.assertGreater(size, 100000)

    def test_run_camids(self):
        # Given a iteration of 1 and test description, make sure the
        # directory structure is created, and the screenshots are saved
        # to file

        import time
        readable_time = time.time()

        self.exam_desc = "camids run test %s" % readable_time
        
        self.ids = camids.WasatchCamIDS_Exam(self.exam_desc)
        result = self.ids.run(1)

        start_str = "Starting exam 1 of 1"
        endin_str = "Exams complete, results in"

        self.assertTrue(start_str in result)
        self.assertTrue(endin_str in result)

        filename = "%s/1_screenshot.png" % self.ids.ex.exam_dir
        result = os.path.isfile(filename)
        self.assertTrue(result)


    def test_start_stop_LargeAnimalOCT(self):
        """ Make sure the oct software can be started and stopped as
        part of the test procedure.
        """
        self.ids = camids.WasatchCamIDS_Exam(self.exam_desc)

        # List the current running processes, make sure laoct is not one
        # of them
        self.assertFalse(self.ids.check_for_LAOCT())

        # Start 
        self.assertTrue(self.ids.start_LAOCT())

        # Make sure running
        self.assertTrue(self.ids.check_for_LAOCT())

        # Stop 
        self.assertTrue(self.ids.stop_LAOCT())
        time.sleep(5)

        # List the current running processes, make sure ueye is not one
        # of them
        self.assertFalse(self.ids.check_for_LAOCT())



if __name__ == "__main__":
    unittest.main()

