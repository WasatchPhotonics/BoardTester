""" tests for the visualization program
"""

import unittest
import os
import shutil
        
from PyQt4 import QtGui, QtTest

from boardtester import broaster
from boardtester import visualize

class Test(unittest.TestCase):

    def setUp(self):
        # Clean any old directories
        self.node_root = "exam_results/test_example_node"
        if os.path.exists(self.node_root):
            shutil.rmtree(self.node_root)
        result = os.path.exists(self.node_root)
        self.assertFalse(result)

    def add_known_group(self, grp_list=None):
        """ Helper function to copy a group of known test results to 
        the testing node directory.
        """
        if grp_list is None:
            grp_list = ["1", "2", "3"]

        for item in grp_list:
            new_path = "%s/%s/" % (self.node_root, item)
            os.makedirs(new_path)

            kd = "boardtester/test/known_results/"
            kd += "%s/%s_system_info.txt" % (item, item)
            dst_file = "%s/%s_system_info.txt" % (new_path, item)
            shutil.copyfile(kd, dst_file)

            kd = "boardtester/test/known_results/"
            kd += "%s/exam_log.txt" % item
            dst_file = "%s/exam_log.txt" % new_path
            shutil.copyfile(kd, dst_file)


    def test_curve_render_continuous(self):
        self.add_known_group(["3"])
        proc = broaster.ProcessBroaster()

        result = proc.process_in_order(self.node_root)

        full_data = []
        for item in result["line_averages"]:
            full_data.extend(item)

        # Plot on a qt graph
        self.app = QtGui.QApplication([])
        self.form = visualize.SimpleLineGraph()

        QtTest.QTest.qWaitForWindowShown(self.form) 
        self.assertEqual(self.form.width(), 800)
        self.assertEqual(self.form.height(), 300)

        # Render the graph
        result = self.form.render_graph(full_data)
        self.assertTrue(result)


    def test_curve_render_gaps(self):
        self.add_known_group(["3"])
        proc = broaster.ProcessBroaster()

        result = proc.process_in_order(self.node_root)

        self.app = QtGui.QApplication([])
        self.form = visualize.SimpleLineGraph()

        self.form.render_gaps(result["total_line_averages"])
        self.assertTrue(result)

    def test_heatmap_of_pixel_values(self):

        self.add_known_group(["3"])
        proc = broaster.ProcessBroaster()

        result = proc.collate_pixels(self.node_root)
        
        self.app = QtGui.QApplication([])
        self.form = visualize.SimpleHeatMap()
        result = self.form.render_image(result["all_data"])
        self.assertTrue(result)

    def test_visualization_command_line_interface(self):
        # These tests are based on the this page:
        # http://dustinrcollins.com/testing-python-command-line-apps
        # Now args should fail with system exit
        visapp = visualize.VisualizeApplication() 
        with self.assertRaises(SystemExit):
            visapp.parse_args([])

        # Add graph type but no node name, expect failure
        with self.assertRaises(SystemExit):
            visapp.parse_args(["-g", "heatmap"])

        args = visapp.parse_args(["-n", "non-existing-node"])
        self.assertIsNotNone(args.node)

        args = visapp.parse_args(["-n", "non-existing-node", "-t"])
        self.assertIsNotNone(args.testing)


    def test_main(self):
        result = visualize.main()
        self.assertEquals(2, result)

        # This shoudl be test results only
        argv = ["-n", "exam_results/kali", "-t"]
        result = visualize.main(argv)
        self.assertEquals(0, result)


 
if __name__ == "__main__":
    unittest.main()
