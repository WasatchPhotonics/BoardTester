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
   
    def test_find_log_no_results(self):
        # Give an invalid exam results directory, make sure it says not
        # found
        proc = broaster.ProcessBroaster("No_records")
        result = proc.find_log("test text here")
        self.assertEquals("invalid exam root", result)
 
    def test_find_log(self):

        exam_description = "unfindable"
        self.proc = broaster.ProcessBroaster()
        filename = self.proc.find_log(exam_description) 
        self.assertEquals("not found", filename)

        # Now copy over a known exam result file, and make sure it can
        # be found

        new_path = "%s/9/" % self.node_root
        os.makedirs(new_path)
        result = os.path.exists(new_path)
        self.assertTrue(result)

        kd = "boardtester/test/known_results/9/9_system_info.txt"
        dst_file = "%s/9_system_info.txt" % new_path
        shutil.copyfile(kd, dst_file)
        result = os.path.exists(dst_file)
        self.assertTrue(result)

        exam_description = "actual test"
        result = self.proc.find_log(exam_description) 
        lf = "exam_results/test_example_node/9/exam_log.txt"
        self.assertEqual(lf, result)

    def test_process_log(self):
        # Create a known exam log, process results
        self.proc = broaster.ProcessBroaster()
        new_path = "%s/9/" % self.node_root
        os.makedirs(new_path)

        kd = "boardtester/test/known_results/9/9_system_info.txt"
        dst_file = "%s/9_system_info.txt" % new_path
        shutil.copyfile(kd, dst_file)

        kd = "boardtester/test/known_results/9/exam_log.txt"
        dst_file = "%s/exam_log.txt" % new_path
        shutil.copyfile(kd, dst_file)

        exam_description = "actual test"
        filename = self.proc.find_log(exam_description) 

        result = self.proc.process_log(filename)
        self.assertEqual(result, "36 Fail, 32 Pass")

    def test_single_process_mti_log(self):
        # Create a known exam log, look for acquire failures
        proc = broaster.ProcessBroaster()
        new_path = "%s/1/" % self.node_root
        os.makedirs(new_path)
        
        kd = "boardtester/test/known_results/1/1_system_info.txt"
        dst_file = "%s/1_system_info.txt" % new_path
        shutil.copyfile(kd, dst_file)

        kd = "boardtester/test/known_results/1/exam_log.txt"
        dst_file = "%s/exam_log.txt" % new_path
        shutil.copyfile(kd, dst_file)

        exam_description = "MTI 2048 pixels, 100 group 1"
        filename = proc.find_log(exam_description) 

        results = proc.process_mti_log(filename)

        self.assertEqual(results["fail"], 3)
        self.assertEqual(results["pass"], 97)

        self.assertLess(results["entire_pixel_average"], 30000)
        self.assertGreater(results["entire_pixel_average"], 28000)

    def test_combined_process_mti_log(self):
        # Make sure test node is clear
        result = os.path.exists(self.node_root)
        self.assertFalse(result)

        # Add in a group of known test results
        self.add_known_group()
        proc = broaster.ProcessBroaster()

        # Process as a group, summarize results in dict form
        result = proc.process_mti_group(self.node_root)
        self.assertEqual(result["overall_result"], "23 Fail, 277 Pass")

        self.assertLess(result["failure_rate"], 7.7)
        self.assertGreater(result["failure_rate"], 7.6)



    def add_known_group(self):
        # Copy a group of known test results to the testing node
        # directory
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

    def test_average_entire_line_value_trend(self):
        # Make sure test node is clear
        result = os.path.exists(self.node_root)
        self.assertFalse(result)

        # Add in a group of known test results
        self.add_known_group()
        proc = broaster.ProcessBroaster()

        # Read the files in order
        result = proc.process_in_order(self.node_root)

        # Total data points should match total 'pass' line count
        pass_line_count = result["pass"]
        total_num_averages = len(result["total_line_averages"])
        self.assertEqual(total_num_averages, pass_line_count)

        # Make sure the first and last entries of data match expected
        # values
        first_item = result["total_line_averages"][0]
        last_item = result["total_line_averages"][-1]
        self.assertGreater(first_item, 28725)
        self.assertLess(first_item, 28726)
        self.assertGreater(last_item, 28801)
        self.assertLess(last_item, 28802)

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

    def test_overlay_visualization(self):
        # Use the data generated above, and render with a line that is
        # all data. Where the averages report a zero for no data,
        # instead print the previous entry. The inverse happens on the
        # second pass. A new line is created where every zero point is a
        # line with no pen, and a marker. Then set the axis to min + max
        # of actual non-zero data plus a margin. That way it shows the
        # 900+ out of 1000 with data, and the 33-ish entries that were
        # the device not booting up also show
        # 
        # Hmm.. maybe a better solution is to split on numpy.nan entries
        # and just render a bunch of curves that have their boundaries
        # at the 0/nan entries?
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
        self.form.render_combined_graph(result["total_line_averages"])
        QtTest.QTest.qWait(13000)

#all of the pixel line values, then build a series of graphs, second one
#is an average of all values of each pixel. 
#Third uses pyqtgraph waterfal to
#create a style of heat map. 
#Just get the data in guiqwt for now and
#manually edit the display parameters for visualization.   
# A test that shows a fitted curve over the average of each line curve

if __name__ == "__main__":
    unittest.main()
