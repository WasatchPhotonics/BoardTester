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

class ProcessBroaster(object):
    """ Look through the existing exam results, and create statistics
    about pass and failure rates.
    """
    def __init__(self, exam_root="exam_results"):
        #print "Start process broaster"
        self._exam_root = exam_root

    def find_log(self, description):
        """ Look through each exam log entry, and return the full exam
        log if the description is found in the file.
        """


        # Check for root directory
        if not os.path.exists(self._exam_root):
            print "Exam root: %s does not exist"
            return "invalid exam root"

        # For each sub directory in the root, walk through all
        # directories, and look for the description text in the system
        # info file

        list_of_files = {}
        for (dirpath, dirnames, filenames) in os.walk(self._exam_root):
            for dirname in dirnames:
                full_path = "%s/%s" % (dirpath, dirname)
                result, name = self.check_sub(full_path, description)
                if result:
                    print "Found description in %s" % full_path
                    return name

        return "not found"
   
    def check_sub(self, full_path, description):
        """ Look at the exam info file in the specified directory,
        return true if the description text is present.
        """
        for (dirpath, dirnames, filenames) in os.walk(full_path):
            for dirname in dirnames:

                sysname = "%s/%s/" % (full_path, dirname)
                sysname += "%s_system_info.txt" % dirname
                #print "Open %s" % sysname
                sysfile = open(sysname)
                for line in sysfile.readlines():
                    #print "line is: %s" % line
                    if description in line:
                        ret_file = "%s/%s" % (full_path, dirname)
                        ret_file += "/exam_log.txt"
                        return True, ret_file
                sysfile.close()

        #print "Description %s not found" % description
        return False, "not found"

    def process_log(self, filename):
        """ Look for all the pass/fail criteria entries in a log file.
        Return a text summary of the failure rates.
        """
        log_file = open(filename)
        fail_count = 0
        pass_count = 0
        for line in log_file.readlines():
            # Only check the usb bulk read status for now
            if 'Error lines info' in line:
                fail_count += 1
            elif "Line: 9 length is: 1024" in line:
                pass_count += 1
 

        summ_str = "%s Fail, %s Pass" % (fail_count, pass_count)
        return summ_str

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
            #self.power_on(count, wait_interval=sleep_duration)


            #self.power_off(count, wait_interval=sleep_duration)

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
        print "Startup result: %s, wait 5" % result
        time.sleep(5)
        return True

    def stop_ueye(self):
        """ Kill the software from IDS - no clean, no confirmation, just kill."""
        import os
        ueye_kill = '''"taskkill /IM uEyeCockpit.exe"'''
        result = os.system(ueye_kill)
        print "Kill result: %s" % result
        return True

    def check_for_ueye(self):
        """ List all system processes, return true if uEyeCockpit is found."""
        import wmi
        wmi_obj = wmi.WMI()

        for process in wmi_obj.Win32_Process():
            if "uEye" in process.Name:
                print "Found ueye: %s, %s" % (process.processId, process.Name)
                return True
        return False

    def take_screenshot(self, exam, suffix):
        screen_file = "%s/test_screenshot_%s.png" % (exam.exam_dir, 
                                                     suffix)

        # take a screenshot, save it to disk
        from PIL import ImageGrab
        im = ImageGrab.grab()
        im.save(screen_file)


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

class CamIDSUtils(object):
    """ Helper functions for displaying text and information about the
    program.
    """
    def __init__(self):
        self.camids_text = """
##########################################################
#         _____          __  __ _____ _____   _____      #
#        / ____|   /\   |  \/  |_   _|  __ \ / ____|     #
#       | |       /  \  | \  / | | | | |  | | (___       #
#       | |      / /\ \ | |\/| | | | | |  | |\___ \      #
#       | |____ / ____ \| |  | |_| |_| |__| |____) |     #
#        \_____/_/    \_\_|  |_|_____|_____/|_____/      #
#							 #
##########################################################
""" 
    def colorama_camids(self):
        lines = self.camids_text.split('\n')
        colorama.init()
    
        color_str = Fore.BLUE + lines[1] + '\n'
        color_str += Fore.GREEN + lines[2] + '\n'
        color_str += Fore.GREEN + lines[3] + '\n'
        color_str += Fore.GREEN + lines[4] + '\n'
        color_str += Fore.GREEN + lines[5] + '\n'
        color_str += Fore.GREEN + lines[6] + '\n'
        color_str += Fore.GREEN + lines[7] + '\n'
        color_str += Fore.GREEN + lines[8] + '\n'
        color_str += Fore.BLUE + lines[9] + '\n'
        color_str += Fore.BLUE + lines[10] + '\n'
    
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


    sae = WasatchBroaster_Exam(args.description)
    sae.run(args.iterations)
