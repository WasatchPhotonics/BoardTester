""" visualize - graphical representation of broaster generated data

Uses pyqt and guiqwt for fast, configurable graphs.
"""

import sys
import argparse

from guiqwt import plot
from guiqwt import styles
from guiqwt import curve
from guiqwt import builder

from PyQt4 import QtGui, QtCore, QtSvg

from boardtester import broaster

class SimpleHeatMap(QtGui.QWidget):
    """ Wrappers for creating guiqwt heatmaps from list data.
    """
    def __init__(self, autoclose=False):
        super(SimpleHeatMap, self).__init__()
        self.setupUI()
        if autoclose:
            self.closeTimer = QtCore.QTimer()
            self.closeTimer.timeout.connect(self.closeEvent)
            self.closeTimer.start(2000)
        self.show()

    def setupUI(self):
        """ Place a guiqwt imagedialog on the widget.
        """
        self.mainImageDialog = plot.ImageDialog(toolbar=True, edit=True,
            wintitle="Image Dialog")

        self.plot = self.mainImageDialog.get_plot()
    
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.mainImageDialog)
        self.setLayout(vbox)
        self.setGeometry(100, 100, 800, 800)
       
    def render_image(self, data_list):
        """ With a two dimensional data set, create and imageitem and
        add it to the image widget.
        """ 
        bmi = builder.make.image
        self.image = bmi(data_list)
        self.plot.add_item(self.image)
        self.plot.do_autoscale()
        return True

        
class SimpleLineGraph(QtGui.QWidget):
    """ Various wrappers and helper functions for generating single line
    curves, and multiple curves with gap data from the same data source.
    """
    def __init__(self, autoclose=False):
        super(SimpleLineGraph, self).__init__()
        self.setupUI()
        self.show()
        if autoclose:
            self.closeTimer = QtCore.QTimer()
            self.closeTimer.timeout.connect(self.close)
            self.closeTimer.start(2000)


    def setupUI(self):
        """ Use the CurveDialog widget from guiqwt, place on the main
        widget. Set local variables for re-use.
        """
        self.mainCurveDialog = plot.CurveDialog(toolbar=True,
            edit=True, wintitle="Main Dialog")

        self.plot = self.mainCurveDialog.get_plot()
        
        self.chart_param = styles.CurveParam()
        self.chart_param.label = "Data"
        self.chart_param.line.color = "Blue"

        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.mainCurveDialog)
        self.setLayout(vbox)

        self.setGeometry(100, 100, 800, 300)
        
    def render_graph(self, data_list):
        """ With a one dimensional list, create new curve, add it to the
        graph, replot the graph.
        """
        x_axis = range(len(data_list))
        self.curve = curve.CurveItem(self.chart_param)
        self.curve.set_data(x_axis, data_list)
        self.plot.add_item(self.curve)
        self.plot.do_autoscale()
        return True

    def render_gaps(self, data_list):
        """ One dimenstional data, where the list has -9999 where no
        data was collected. Create a series of non-continguous graphs
        from the mixed intensity/nan data.
        """
        bmc = builder.make.curve

        orig_position = 0
        y_axis = []
        x_axis = []

        # Walk through every point in the list, creating new arrays for
        # curve x axis and intensity, breaking at -9999
        while orig_position < len(data_list):
            curr_value = data_list[orig_position]

            if curr_value != -9999:
                y_axis.append(curr_value)
                x_axis.append(orig_position)
    
            else:
                new_curve = bmc(x_axis, y_axis, color="red")
                self.plot.add_item(new_curve)
                y_axis = []
                x_axis = []
        
            orig_position += 1
       
        # Add the final curve if it contains data
        if len(x_axis) != 0:
            new_curve = bmc(x_axis, y_axis, color="red")
            self.plot.add_item(new_curve)
 
        self.plot.do_autoscale()
        return True

class VisualizeApplication(object):
    """ Wrapper around application control code based on:
    https://groups.google.com/d/msg/comp.lang.python/j_tFS3uUFBY/\
        ciA7xQMe6TMJ
    """
    def __init__(self):
        super(VisualizeApplication, self).__init__()
        self.parser = self.create_parser()

    def parse_args(self, argv):
        return self.parser.parse_args(argv)

    def create_parser(self):
        desc = "guiqwt visualizations of boardtester processing"
        parser = argparse.ArgumentParser(description=desc)
    
        parser.add_argument("-n", "--node", required=True,
            help="Entire node to process of exam results")
    
        parser.add_argument("-t", "--graph", required=False,
            help="Visualization to generate from node data")

        parser.add_argument("-c", "--autoclose", required=False,
            help="Shut down the window after a delay")
        
        return parser

    def run(self):
        """ Create and execute the application with the input args.
        """
        app = QtGui.QApplication(sys.argv)
        proc = broaster.ProcessBroaster()
        result = proc.process_in_order("exam_results/kali")

        grp = SimpleLineGraph(autoclose=True)
        grp.render_gaps(result["total_line_averages"])
        sys.exit(app.exec_())

def main(argv=None): 
    if argv is None: 
        from sys import argv as sys_argv 
        argv = sys_argv 
    
    exit_code = 0
    try:
        visapp = VisualizeApplication()
        visapp.parse_args(argv)
        visapp.run()
    except SystemExit, exc:
        exit_code = exc.code

    #exit_code = 0 
    #try: 
        #frob_app = FrobApplication() 
        #frob_app.parse_args(argv) 
        #frob_app.main() 
    #except SystemExit, exc: 
        #exit_code = exc.code 
    #parser = create_parser()
    #args = parser.parse_args()
    #result = proc.process_in_order(args.node)

    #grp = SimpleLineGraph()
    #grp.render_gaps(result["total_line_averages"])

    return exit_code 

if __name__ == '__main__': 
    exit_code = __main__(sys.argv) 
    sys.exit(exit_code) 

#def main():
#    parser = create_parser()
#    args = parser.parse_args()
#
#    app = QtGui.QApplication(sys.argv)
#
#    if args.graph is None:
#        proc = broaster.ProcessBroaster()
#        result = proc.process_in_order(args.node)
#
#        grp = SimpleLineGraph()
#        grp.render_gaps(result["total_line_averages"])
#
#    #result = proc.collate_pixels("exam_results/kali")
#    #shm = SimpleHeatMap()
#    #shm.render_image(result["all_data"])
#
#    sys.exit(app.exec_())
#
#if __name__ == "__main__":
#    main()
