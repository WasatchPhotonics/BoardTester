""" visualize - graphical representation of broaster generated data

Uses pyqt and guiqwt for fast, configurable graphs.
"""

import sys
import numpy

from guiqwt import plot
from guiqwt import styles
from guiqwt import curve
from guiqwt import builder

from PyQt4 import QtGui, QtCore, QtSvg

from boardtester import broaster

class SimpleLineGraph(QtGui.QWidget):
    def __init__(self):
        super(SimpleLineGraph, self).__init__()

        self.setupUI()
        self.show()

    def setupUI(self):
        self.mainCurveDialog = plot.CurveDialog(toolbar=True,
            edit=True, wintitle="Main Dialog")

        self.plot = self.mainCurveDialog.get_plot()
        
        self.chart_param = styles.CurveParam()
        self.chart_param.label = "Data"
        self.chart_param.line.color = "Blue"
        
        self.curve = curve.CurveItem(self.chart_param)

        
        self.plot.add_item(self.curve)
        #self.plot.set_axis_limits(0, 0, 65535)
        #self.plot.set_axis_limits(2, 0, len(self.x))
        #self.plot.set_axis_title(0, "Intensity (auto)")
        #self.plot.set_axis_title(2, "Pixel")

        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.mainCurveDialog)
        self.setLayout(vbox)

        self.setGeometry(100, 100, 800, 300)
        
    def render_graph(self, data_list):
        """ With a one dimensional list, update the existing curve,
        refresh the graph.
        """
        x_axis = range(len(data_list))
        self.curve.set_data(x_axis, data_list)
        self.plot.do_autoscale()

    def render_point_graph(self, data_list):
        """ With one dimesional data list, create a new curve that is
        displayed with points, this is designed to then let the user
        specify a top and bottom scale to show the data and the gaps in
        the data.
        """

        data_x = range(len(data_list))
        data_y = data_list
        bmc = builder.make.curve
        self.point_curve = bmc(data_x, data_y, linestyle="NoPen",
            linewidth=0.1, marker="Diamond", markersize=5.0)

        #self.point_curve.set_data(data_x, data_y)
        
        self.plot.add_item(self.point_curve)
        self.plot.do_autoscale()

    def total_averages(self):
        # Add in a group of known test results
        proc = broaster.ProcessBroaster()

        #self.node_root = "exam_results/test_example_node"
        self.node_root = "exam_results/kali"
        result = proc.process_in_order(self.node_root)

        # Total data points should match total 'pass' line count
        #self.render_graph(result["total_line_averages"])
        self.render_point_graph(result["total_line_averages"])
        
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    grp = SimpleLineGraph()
    grp.total_averages()
    sys.exit(app.exec_())