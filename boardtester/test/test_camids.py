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
        if os.path.exists(self.node_root):
            shutil.rmtree(self.node_root)
        result = os.path.exists(self.node_root)
        self.assertFalse(result)

    
    def test_run_camids(self):
        # First check the utils can be used to print the important
        # colored ascii logo
        self.exam_iter = 1
        self.exam_desc = "run camids test"
        #self.ids = camids.WasatchCamIDS_Exam(self.desc)

        camutil = camids.CamIDSUtils()
	result = camutil.colorama_camids()
        # Look for the bottom of the CAMIDS cameras
	print "result \n%s" % result
        self.assertTrue("J__||____||______F  J______F" in result)
        #self.sae.run(self.exam_iter)


if __name__ == "__main__":
    unittest.main()
