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
    def __init__(self):
        super(SimpleHeatMap, self).__init__()
        self.setupUI()
        self.show()

    def setupUI(self, defaults=None):
        """ Place a guiqwt imagedialog on the widget.
        """
        self.mainImageDialog = plot.ImageDialog(toolbar=True, 
             options=dict(show_xsection=True, show_ysection=True,
                          show_contrast=True))

        self.plot = self.mainImageDialog.get_plot()
    
        self.vbox = QtGui.QVBoxLayout()
        self.vbox.addWidget(self.mainImageDialog)
        self.setLayout(self.vbox)
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
       
    def update_image(self, data_list):
        """ Re-use the existing single image on the heatmap.
        """
        try:
            self.image.set_data(data_list)
        except:
            bmi = builder.make.image
            self.image = bmi(data_list)
            self.plot.add_item(self.image)
    
        self.plot.replot()
        return True

        
class SimpleLineGraph(QtGui.QWidget):
    """ Various wrappers and helper functions for generating single line
    curves, and multiple curves with gap data from the same data source.
    """
    def __init__(self):
        super(SimpleLineGraph, self).__init__()
        self.setupUI()
        self.show()

    def setupUI(self):
        """ Use the CurveDialog widget from guiqwt, place on the main
        widget. Set local variables for re-use.
        """
        self.mainCurveDialog = plot.CurveDialog(toolbar=True,
            wintitle="Main Dialog")

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
    Specifically, this means breaking out all of the functions from main
    into this application object so they can have a narrow interface,
    suitable for unit testing.
    """
    def __init__(self):
        super(VisualizeApplication, self).__init__()
        self.parser = self.create_parser()

    def parse_args(self, argv):
        self.args = self.parser.parse_args(argv)
        return self.args

    def create_parser(self):
        desc = "guiqwt visualizations of boardtester processing"
        parser = argparse.ArgumentParser(description=desc)
    
        parser.add_argument("-n", "--node", required=True,
            help="Entire node to process of exam results")
    
        parser.add_argument("-g", "--graph", required=False,
            default="gaps", 
            choices=["gaps", "heatmap", "gain", "offset"],
            help="Visualization to generate from node data")

        parser.add_argument("-c", "--autoclose", required=False,
            help="Shut down the window after a delay")
        
        parser.add_argument("-t", "--testing", action="store_true",
            help="exit code 3 instead of showing the gui, for unittest")
        
        return parser

    def add_offset_controls(self):
        """ Add gui controls for viewing different versions of the
        heatmap based on the csv offset extraction.
        """
        self.shm = SimpleHeatMap()

        offsetGroup = QtGui.QFrame()
        offsetLayout = QtGui.QHBoxLayout(offsetGroup)

        self.labelOffset = QtGui.QLabel("Current offset is: ")
        self.spinBoxOffset = QtGui.QSpinBox() 
        self.spinBoxOffset.setMinimum(0)
        self.spinBoxOffset.setMaximum(255)
        self.sliderOffset = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.sliderOffset.setMinimum(0)
        self.sliderOffset.setMaximum(255)

        offsetLayout.addWidget(self.labelOffset)
        offsetLayout.addWidget(self.spinBoxOffset)
        offsetLayout.addWidget(self.sliderOffset)
        
        spacer = QtGui.QWidget()
        spacer.setSizePolicy(QtGui.QSizePolicy.Expanding,
                             QtGui.QSizePolicy.Expanding)
        offsetLayout.addWidget(spacer)

        self.shm.vbox.addWidget(offsetGroup)

        self.sliderOffset.valueChanged.connect(self.spinBoxOffset.setValue)
        self.spinBoxOffset.valueChanged.connect(self.sliderOffset.setValue)
        self.spinBoxOffset.valueChanged.connect(self.update_offset)


    def update_offset(self, offset):
        """ Given an input offset number, load that file and display.
        """
        proc = broaster.ProcessBroaster()
        csv_filename = "boardtester/test/known_results/" \
                       + "PRLW047_sorted_20140730/" \
                       + "PRL_Offset_%s_Gain_0_254.csv" % offset
        result = proc.csv_to_pixels(csv_filename)
        self.shm.update_image(result["all_data"])

    def run(self):
        """ Create the Qt application if required, execute the specific
        processing collation steps for the designated graph mode. Then
        exit with the app.exec if the unittest has not created the qt 
        application.
        """

        if not self.args.testing:
            app = QtGui.QApplication(sys.argv)

        proc = broaster.ProcessBroaster()
        
        if self.args.graph == "gaps":

            result = proc.process_in_order(self.args.node)
            slg = SimpleLineGraph()
            slg.render_gaps(result["total_line_averages"])

        elif self.args.graph == "heatmap":

            result = proc.collate_pixels(self.args.node)
            shm = SimpleHeatMap()
            shm.render_image(result["all_data"])

        elif self.args.graph == "gain":
            csv_filename = "boardtester/test/known_results/" \
                           + "PRL_Gain_0_255_Offset_128.csv"
            result = proc.csv_to_pixels(csv_filename)
            shm = SimpleHeatMap()
            shm.render_image(result["all_data"])
        

        elif self.args.graph == "offset":
            self.form = self.add_offset_controls() 
            self.update_offset(255)
            

        if not self.args.testing:
            sys.exit(app.exec_())



def main(argv=None): 
    """ main calls the wrapper code around the application objects with
    as little framework as possible. See:
    https://groups.google.com/d/msg/comp.lang.python/j_tFS3uUFBY/\
        ciA7xQMe6TMJ
    """
    
    if argv is None: 
        from sys import argv as sys_argv 
        argv = sys_argv 
    else:
        # Strip out the program name to match the unittest setup
        argv = argv[1:]

    exit_code = 0
    try:
        visapp = VisualizeApplication()
        visapp.parse_args(argv)
        visapp.run()
    except SystemExit, exc:
        exit_code = exc.code

    return exit_code 

if __name__ == '__main__': 
    exit_code = main(sys.argv) 
    sys.exit(exit_code) 

