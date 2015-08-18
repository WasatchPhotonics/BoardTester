""" 
Verify functionality of camids command line tool.
"""

import unittest
import sys
import os
import shutil

from boardtester import camids

class Test(unittest.TestCase):

    def setUp(self):
        # Clean any old directories
        self.node_root = "exam_results/test_ids_example_node"
        self.exam_iter = 1
        self.exam_desc = "run camids test"
        if os.path.exists(self.node_root):
            shutil.rmtree(self.node_root)
        result = os.path.exists(self.node_root)
        self.assertFalse(result)

    
    def test_color_camids(self):
        # First check the utils can be used to print the important
        # colored ascii logo
        camutil = camids.CamIDSUtils()
        result = camutil.colorama_camids()

        # Look for the bottom of the CAMIDS text
	      #print "result \n%s" % result
        self.assertTrue("|_____|_____/|_____/" in result)


    def test_run_camids(self):
        self.ids = camids.WasatchCamIDS_Exam(self.exam_desc)
        result = self.ids.run(self.exam_iter)

        start_str = "Starting exam 1 of 1"
        endin_str = "Exams complete, results in"

        self.assertTrue(start_str in result)
        self.assertTrue(endin_str in result)


    def test_ueye_available(self):
        # Convenience test to verify that uEye software is installed on the system
        ueye_exec = "C:\Program Files\IDS\uEye\Program\uEyeCockpit.exe"
        result = os.path.isfile(ueye_exec)
        self.assertTrue(result)

    def test_click_mouse(self):
        # Given a random coordinate, move the mouse there, click the button
        # Use the start menu in the lower left, verify that the start menu appears
        self.ids = camids.WasatchCamIDS_Exam(self.exam_desc)
        result = self.ids.move_and_click(10, 1060, wait_interval=1)
        self.assertTrue(result)

    def test_start_stop_ueye(self):
        # List the current running processes, make sure ueye is not one of them
        self.assertFalse(self.ids.check_for_ueye())

        # Start ueye
        self.assertFalse(self.ids.start_ueye())

        # Make sure ueye is running
        self.assertTrue(self.ids.check_for_ueye())

        # Stop ueye
        self.assertFalse(self.ids.stop_ueye())

        # List the current running processes, make sure ueye is not one of them
        self.assertFalse(self.ids.check_for_ueye())

if __name__ == "__main__":
    unittest.main()
