""" tests for the visualization program
"""

import unittest
import sys
import os
import shutil
import numpy
        
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

    def test_average_entire_line_visualization(self):
        # Re-use the computation code, and make sure the render is
        # functional
        result = os.path.exists(self.node_root)
        self.assertFalse(result)

        # Add in a group of known test results
        self.add_known_group()
        proc = broaster.ProcessBroaster()

        # Read the files in order
        result = proc.process_in_order(self.node_root)

        # Get the average value of entire line
        # Total data points should match total 'pass' line count
        full_data = []
        for item in result["line_averages"]:
            full_data.extend(item)

        # Plot on a qt graph
        self.app = QtGui.QApplication(sys.argv)
        self.form = visualize.SimpleLineGraph()

        gwid = self.form.mainCurveDialog
        QtTest.QTest.qWaitForWindowShown(self.form) 
        self.assertEqual(self.form.width(), 800)
        self.assertEqual(self.form.height(), 300)

        # Render the graph
        self.form.render_graph(full_data)

        # Get the first and last entries from the graph, make sure they
        # match the raw python list data
        x_data, y_data = self.form.curve.get_data()

        self.assertEqual(y_data[0], full_data[0])
        self.assertEqual(y_data[-1], full_data[-1])

        QtTest.QTest.qWait(10000)

    def test_point_visualization(self):
        # Use the data generated above, and render with points instead
        # of a line
        result = os.path.exists(self.node_root)
        self.assertFalse(result)

        # Add in a group of known test results
        self.add_known_group()
        proc = broaster.ProcessBroaster()

        # Read the files in order
        result = proc.process_in_order(self.node_root)

        # Plot on a qt graph
        self.app = QtGui.QApplication(sys.argv)
        self.form = visualize.SimpleLineGraph()

        # Render the graph
        self.form.render_point_graph(result["total_line_averages"])
        QtTest.QTest.qWait(13000)


    def test_render_with_gaps(self):
        result = os.path.exists(self.node_root)
        self.assertFalse(result)

        # Add in a group of known test results
        self.add_known_group(['1'])
        proc = broaster.ProcessBroaster()

        # Read the files in order
        result = proc.process_in_order(self.node_root)

        # Plot on a qt graph
        self.app = QtGui.QApplication(sys.argv)
        self.form = visualize.SimpleLineGraph()

        # Render the graph
        #print "Does gap: %s" % result["total_line_averages"]
        self.form.render_gaps(result["total_line_averages"])

        # Group 1 of known results has missing data at positions:
        # 8, 96, 100
        # Therefore, there should be 3 curves: 0-7, 9-95, 97-99

        item_list = self.form.plot.get_items()
        self.assertEquals(len(item_list), 4) # curves + grid
        QtTest.QTest.qWait(3000)

    def test_render_average_of_each_pixel(self):
        result = os.path.exists(self.node_root)
        self.assertFalse(result)

        self.add_known_group(['1'])
        proc = broaster.ProcessBroaster()

        result = proc.process_in_order_get_pixels(self.node_root)

        self.app = QtGui.QApplication(sys.argv)
        self.form = visualize.SimpleLineGraph()

        # stored_average divisor needs to match the total number of
        # "pass" entries
        pass_line_count = result["pass"]
        avg_divisor = result["average_divisor"]
        self.assertEqual(pass_line_count, avg_divisor)

        avg_pix_zero = result["average_pixels"][0]
        avg_pix_2047 = result["average_pixels"][2047]

        # Make sure the first and last entries of data match expected
        # values
        self.assertGreater(avg_pix_zero, 28750)
        self.assertLess(avg_pix_zero, 28752)
        self.assertGreater(avg_pix_2047, 28758)
        self.assertLess(avg_pix_2047, 28760)

        self.form.render_gaps(result["average_pixels"])
        QtTest.QTest.qWait(3000)

    def test_pixel_average_large_group_render(self):
        result = os.path.exists(self.node_root)
        self.assertFalse(result)

        self.add_known_group(['3'])
        proc = broaster.ProcessBroaster()

        result = proc.process_in_order_get_pixels(self.node_root)

        self.app = QtGui.QApplication(sys.argv)
        self.form = visualize.SimpleLineGraph()

        self.form.render_gaps(result["average_pixels"])
        QtTest.QTest.qWait(13000)

    def test_heatmap_of_pixel_values(self):

        self.add_known_group(['3'])
        proc = broaster.ProcessBroaster()

        result = proc.collate_pixels(self.node_root)
        
        self.app = QtGui.QApplication(sys.argv)
        self.form = visualize.SimpleHeatMap()
        result = self.form.render_image(result["all_data"])
        self.assertTrue(result)


    def add_known_group(self, grp_list=None):
        """ Copy a group of known test results to the testing node
        directory.
        """
        if grp_list is None:
            grp_list = ['1', '2', '3']

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


if __name__ == "__main__":
    unittest.main()
