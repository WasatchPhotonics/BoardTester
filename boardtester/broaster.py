""" collect data with automated hardware power cycling

usage:
    python broaster.py --iterations 10 --description "short test"

Uses phidgeter to control a relay placing the device in a known power
state. Performs checks of device functionality and stores for later
analysis.

You may notice return values from certain functions are not checked.
This is part of the test strategy, as it allows the same messages
printed to log files to be printed to the test runner for string
comparison. Later plans include converting this to log file intercept
using testfixtures.LogCapture
"""

import sys    
import time
import argparse
import colorama
from colorama import init, Fore, Back, Style

from wpexam.exam import Exam
from wasatchusb import camera
from wasatchusb.utils import FindDevices
from phidgeter import relay

class WasatchBroaster_Exam(object):
    
    def __init__(self, exam_name):
        print "exam name is [%s]" % exam_name
        self.ex = Exam(exam_name) 
        self.vid = 0x24aa
        self.pid = 0x0009

    def run(self, max_runs=100):
        """ Main loop for the broaster exam. Turns on the device, waits,
        stores communication results, turns off the device. Repeat."""
        
        # This variable is key - sometimes the boards take 30+ seconds
        # to appear on the usb bus.  
        sleep_duration = 10.1

        count = 1
        while count < max_runs+1:
            print "Starting exam %s of %s ..." % (count, max_runs),
            self.power_on(count, wait_interval=sleep_duration)

            self.bus_info(count)
            self.revision_info(count)
            self.lines_info(count)

            self.disconnect(count)
            self.power_off(count, wait_interval=sleep_duration)

            count += 1
            print "done"

        print "Processed %s exams." % max_runs
        print "Exams complete, results in: %s" % self.ex.exam_dir


    def disconnect(self, count):
        """ Disconnect the usb device if still connected.
        """
        discon_str = " Start of disconnection "
        try:
            result = self.device.disconnect()
            discon_str += " result [%s]" % result
        except:
            discon_str = "Error disconnect: %s" % str(sys.exc_info())
            
        self.append_to_log(self.ex, count, discon_str)
        return discon_str

    def revision_info(self, count):
        """ Actually connect to the device, get the firmware revisions
        """
        revision_str = " Start of revision info " 
        try:
            device = camera.CameraUSB()
            self.device = device
            result = device.connect(self.vid, self.pid)
            revision_str += " result [%s] " % result
    
            codes = self.get_revisions(device) 
            revision_str += " %s " % codes
        except:
            revision_str += " Error get revision: %s" % str(sys.exc_info())

        self.append_to_log(self.ex, count, revision_str)
        return revision_str

    def bus_info(self, count):
        """ Print host usb information, dont' connect to the
        device. Use Host system facility to find devices.""" 
        bus_str = " Start of bus info " 
        fd = FindDevices()
        result, usb_info = fd.list_usb()
        bus_str += " USB ID strings: %s" % usb_info

        result, serial = fd.get_serial(self.vid, self.pid)
        bus_str += " Serial USB Descriptor: %s" % serial

        self.append_to_log(self.ex, count, bus_str)
   
    def lines_info(self, count):
        """ Read various groups of lines from the device.
        """
        line_info = " Start of line info "
        try:
            result = self.check_bulk_data(self.device, 10)
            line_info += result
        except:
            line_info += " Error lines info: %s" % str(sys.exc_info())

        self.append_to_log(self.ex, count, line_info) 
        return line_info

    def check_bulk_data(self, device, line_count):
        """ Perform the read of the specified number of lines from the
        device.
        """
        curr_count = 0 
        result = " Start read of %s lines" % line_count
        while curr_count < line_count: 
            status, pixel_data = device.get_line()

            # Dont' do the performance checks here, that's later in log
            # file processing
            result += " Line: %s length is: %s" % (curr_count, 
                                                   len(pixel_data))

            curr_count += 1

        return result

    def get_revisions(self, device):
        result, sw_code = device.get_sw_code()
        result, fpga_code = device.get_fpga_code()
    
        code_str = "SW: %s FPGA: %s" % (sw_code, fpga_code)
        return code_str

    def append_to_log(self, ex, count, text):
        log_filename = "%s/exam_log.txt" % ex.exam_dir

        out_file = open(log_filename, "a+")
        out_file.write("%s: %s\n" % (count, text))
        out_file.close()

    def power_on(self, count, wait_interval=5):
        on_msg = "Turn on relay, wait %s seconds" % wait_interval
        phd_relay = relay.Relay()

        result = phd_relay.zero_on()
        on_msg += " Relay zero on Result: %s" % result

        result = phd_relay.three_on()
        on_msg += " Relay three on Result: %s" % result

        time.sleep(wait_interval)
        self.append_to_log(self.ex, count, on_msg)

    def power_off(self, count, wait_interval=5):
        off_msg = "Turn off relay, wait %s seconds" % wait_interval
        phd_relay = relay.Relay()
        
        result = phd_relay.zero_off()
        off_msg += " Relay zero off result: %s" % result

        # odroid 
        result = phd_relay.three_off()
        off_msg += " Relay three off result: %s" % result

        time.sleep(wait_interval)
        self.append_to_log(self.ex, count, off_msg)

class BroasterUtils(object):
    """ Helper functions for displaying text and information about the
    broaster.
    """
    def __init__(self):
        self.broaster_text = """
         )        (   (       (       )        (              (    
   (  ( /(  (     )\ ))\ )    )\ ) ( /(  (     )\ )  *   )    )\ ) 
 ( )\ )\()) )\   (()/(()/(   (()/( )\()) )\   (()/(` )  /((  (()/( 
 )((_|(_)((((_)(  /(_))(_))   /(_)|(_)((((_)(  /(_))( )(_))\  /(_))
((_)_  ((_)\ _ )\(_))(_))_   (_))   ((_)\ _ )\(_)) (_(_()|(_)(_))  
 | _ )/ _ (_)_\(_) _ \|   \  | _ \ / _ (_)_\(_) __||_   _| __| _ \ 
 | _ \ (_) / _ \ |   /| |) | |   /| (_) / _ \ \__ \  | | | _||   / 
 |___/\___/_/ \_\|_|_\|___/  |_|_\ \___/_/ \_\|___/  |_| |___|_|_\\
""" 
    def colorama_broaster(self):
        lines = self.broaster_text.split('\n')
        colorama.init()
    
        color_str = Fore.YELLOW + lines[1] + '\n'
        color_str += Fore.YELLOW + lines[2] + '\n'
        color_str += Fore.YELLOW + lines[3] + '\n'
        color_str += Fore.YELLOW + lines[4] + '\n'
        color_str += Fore.YELLOW + lines[5] + '\n'
        color_str += Fore.RED + lines[6] + '\n'
        color_str += Fore.RED + lines[7] + '\n'
        color_str += Fore.RED + lines[8] + '\n'
    
        color_str += Style.RESET_ALL
        return color_str
 
 
if __name__ == "__main__":
    butil = BroasterUtils()
    print butil.colorama_broaster()

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--iterations", type=int, required=True,
                        help="count of power test cylces")
    parser.add_argument("-d", "--description", required=True,
                        help="short description of exam")
    args = parser.parse_args()


    sae = WasatchBroaster_Exam(args.description)
    sae.run(args.iterations)
