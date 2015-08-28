""" visualize - graphical representation of broaster generated data

Uses pyqt and guiqwt for fast, configurable graphs.
"""

import sys
import numpy

from guiqwt import plot
from guiqwt import styles
from guiqwt import curve

from PyQt4 import QtGui, QtCore, QtSvg

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

        data_x = numpy.linspace(0,2048,2048)
        data_y = numpy.linspace(0,2048,2048)
        self.curve.set_data(data_x, data_y)
        
        self.plot.add_item(self.curve)
        #self.plot.set_axis_limits(0, 0, 65535)
        #self.plot.set_axis_limits(2, 0, len(self.x))
        #self.plot.set_axis_title(0, "Intensity (auto)")
        #self.plot.set_axis_title(2, "Pixel")


        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.mainCurveDialog)
        self.setLayout(vbox)
        
    def render_graph(self, data_list):
        """ With a one dimenstional list, update the existing curve,
        refresh the graph.
        """
        x_axis = range(len(data_list))
        self.curve.set_data(x_axis, data_list)
        self.plot.do_autoscale()

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    grp = SimpleLineGraph()
    sys.exit(app.exec_())
