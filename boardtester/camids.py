""" collect data with automated hardware power cycling

usage:
    python broaster.py --iterations 10 --description "short test"
    python broaster.py --process "short test"

Uses phidgeter to control a relay placing the device in a known power
state. Performs checks of device functionality and stores for later
analysis.

You may notice return values from certain functions are not checked.
This is part of the test strategy, as it allows the same messages
printed to log files to be printed to the test runner for string
comparison. Later plans include converting this to log file intercept
using testfixtures.LogCapture
"""

import os
import sys    
import time
import argparse
import colorama
from colorama import init, Fore, Back, Style

from wpexam.exam import Exam
from wasatchusb import camera
from wasatchusb.utils import FindDevices
from phidgeter import relay

class WasatchCamIDS_Exam(object):
    """ Power cycle devices, store results in automatically created log
    files.
    """
    
    def __init__(self, exam_name):
        print "exam name is [%s]" % exam_name
        self.ex = Exam(exam_name) 
        self.buf_history = ""

    def bprint(self, in_str):
        """ Helper function to store all text before it is printed to the screen.
        """
        self.buf_history += in_str
        print in_str

    def run(self, max_runs=100):
        """ Main loop for the broaster exam. Turns on the device, waits,
        stores communication results, turns off the device. Repeat."""
        
        # This variable is key - sometimes the boards take 30+ seconds
        # to appear on the usb bus.  
        sleep_duration = 10.1

        count = 1
        while count < max_runs+1:
            self.bprint("Starting exam %s of %s ..." % (count, max_runs))
            self.power_on(count, wait_interval=sleep_duration)

            if self.check_for_ueye():
                self.bprint("uEye software already running, fail!")
                sys.exit(1)

            self.start_ueye()
            time.sleep(5)

            if not self.check_for_ueye():
                self.bprint("Can't start ueye software, fail!")
                sys.exit(1)

            # Manually positioned window, saves it's state
            self.move_and_click(20, 60, wait_interval=1)
            time.sleep(5)

            filename = "%s/%s_screenshot.png" % (self.ex.exam_dir, count)
            self.save_screenshot(filename)

            self.stop_ueye()
            # Doesn't always work the first time, do it again
            self.stop_ueye()
            time.sleep(1)
            # One more time, just to be sure
            self.stop_ueye()

            self.power_off(count, wait_interval=sleep_duration)

            count += 1
            self.bprint("done")

        self.bprint("Processed %s exams." % max_runs)
        self.bprint("Exams complete, results in: %s" % self.ex.exam_dir)
        return self.buf_history

    def move_and_click(self, posx, posy, wait_interval=1):
        """ Move the mouse to specified coordinates, click the left button"""
        import ctypes
        u32 = ctypes.windll.user32
        u32.SetCursorPos(int(posx), int(posy))
        u32.mouse_event(2, 0, 0, 0, 0) # left down
        u32.mouse_event(4, 0, 0, 0, 0) # left up
        
        time.sleep(wait_interval)
        return True

    def start_ueye(self):
        """ Start the software from IDS, wait 5 seconds for it to be ready."""
        ueye_exec = '''"C:\Program Files\IDS\uEye\Program\uEyeCockpit.exe"'''
          
        from subprocess import Popen
        result = Popen(ueye_exec)
        #print "Startup result: %s, wait 5" % result
        time.sleep(5)
        return True

    def stop_ueye(self):
        """ Kill the software from IDS - no clean, no confirmation, just kill."""
        import os
        # > /NUL is to keep the 'sent termination...' message from printing
        # Would be nice to capture it and send it to log
        ueye_kill = '''"taskkill /IM uEyeCockpit.exe 1> NUL 2> NUL"'''
        result = os.system(ueye_kill)
        #print "Kill result: %s" % result
        return True

    def check_for_ueye(self):
        """ List all system processes, return true if uEyeCockpit is found."""
        import wmi
        wmi_obj = wmi.WMI()

        for process in wmi_obj.Win32_Process():
            if "uEye" in process.Name:
                #print "Found ueye: %s, %s" % (process.processId, process.Name)
                return True
        return False

    def save_screenshot(self, filename):
        """ Use Pillow to take a screenshot and save to filename."""

        # take a screenshot, save it to disk
        from PIL import ImageGrab
        im = ImageGrab.grab()
        im.save(filename)
        return True


    def power_on(self, count, wait_interval=5):
        """ With a phidget with dual screw terminals per relay configured:
            0 - Ground , shield
            1 - DATA+ , DATA-
            2 - +VCC
        """

        phd_relay = relay.Relay()
        result = phd_relay.zero_on()
        result = phd_relay.one_on()
        result = phd_relay.two_on()

        time.sleep(wait_interval)

    def power_off(self, count, wait_interval=5):
        phd_relay = relay.Relay()

        # Disable +VCC first
        result = phd_relay.two_on()
        result = phd_relay.one_on()
        result = phd_relay.zero_on()

        time.sleep(wait_interval)

class CamIDSUtils(object):
    """ Helper functions for displaying text and information about the
    program.
    """
    def __init__(self):
        self.camids_text = """
###########################################################
#         _____          __  __ _____ _____   _____       #
#        / ____|   /\   |  \/  |_   _|  __ \ / ____|      #
#       | |       /  \  | \  / | | | | |  | | (___        #
#       | |      / /\ \ | |\/| | | | | |  | |\___ \       #
#       | |____ / ____ \| |  | |_| |_| |__| |____) |      #
#        \_____/_/    \_\_|  |_|_____|_____/|_____/       #
#                                                         #
###########################################################
""" 
    def colorama_camids(self):
        lines = self.camids_text.split('\n')
        colorama.init()
    
        color_str = Fore.GREEN + lines[1] + '\n'
        color_str += Fore.GREEN + lines[2] + '\n'
        color_str += Fore.GREEN + lines[3] + '\n'
        color_str += Fore.GREEN + lines[4] + '\n'
        color_str += Fore.GREEN + lines[5] + '\n'
        color_str += Fore.GREEN + lines[6] + '\n'
        color_str += Fore.GREEN + lines[7] + '\n'
        color_str += Fore.GREEN + lines[8] + '\n'
        color_str += Fore.GREEN + lines[9] + '\n'
        color_str += Fore.GREEN + lines[10] + '\n'
    
        color_str += Style.RESET_ALL
        return color_str
 
 
if __name__ == "__main__":
    camutil = CamIDSUtils()
    print camutil.colorama_camids()

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--iterations", type=int, required=True,
                        help="count of power test cylces")
    parser.add_argument("-d", "--description", required=True,
                        help="short description of exam")
    args = parser.parse_args()


    ids = WasatchCamIDS_Exam(args.description)
    ids.run(args.iterations)
