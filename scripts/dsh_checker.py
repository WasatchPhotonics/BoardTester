""" collect data with automated hardware power cycling

usage:
    python dsh_checker.py --iterations 10 --description "short test"

Uses phidgeter to control a relay placing the device in a known power
state. Start Dash software and change variables, take screen shots for
post-processing of device status and failure rates.

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

class WasatchDash_Exam(object):
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
        """ Main loop for verifying SVIS-00079 issues. Turn off device,
        wait, turn on device, wait. Take screenshot, repeat.
        """

        """
        Maybe: 
        THIS WILL ONLY WORK IF YOU TURN OFF 'stopped working' dialogs
        using the exec in utils/
        """

        max_retries = 5
        count = 1
        sleep_duration = 5 # wp raman device boot up time for device manager
        
        while count < max_runs+1:
            self.bprint("Starting exam %s of %s ..." % (count, max_runs))
            self.power_on(count, wait_interval=sleep_duration)

            retry_count = 0
            while retry_count < max_retries:
            
                print "Trying close: %s" % retry_count
                result = self.stop_Dash()
                retry_count += 1
                if not self.check_for_Dash():
                    retry_count = max_retries
                else:
                    time.sleep(1)

            if self.check_for_Dash():
                self.bprint("Dash software already running, fail!")
                sys.exit(1)

            self.start_Dash()
            time.sleep(5)

            self.click_dash_settings()
            time.sleep(5)
            self.change_dash_integration_time()
            time.sleep(1)
            self.click_dash_cooling()
            time.sleep(3)
            self.click_dash_logging()


            if not self.check_for_Dash():
                self.bprint("Can't start Dash software, fail!")
                sys.exit(1)


            #screenshot_wait = 60
            #screenshot_wait = 180
            screenshot_wait = 240
            print "Waiting %s seconds until screenshot" % screenshot_wait
            time.sleep(screenshot_wait)

            filename = "%s/%s_screenshot.png" % (self.ex.exam_dir, count)
            self.save_screenshot(filename)


            retry_count = 0
            while retry_count < max_retries:
            
                print "Trying close: %s" % retry_count
                result = self.stop_Dash()
                retry_count += 1
                if not self.check_for_Dash():
                    retry_count = max_retries
                else:
                    time.sleep(1)

                   
            #close_wait = 15
            close_wait = 1
            print "Tail close wait %s" % close_wait
            time.sleep(close_wait)

            self.power_off(count, wait_interval=sleep_duration)

            count += 1
            self.bprint("done")

        self.bprint("Processed %s exams." % max_runs)
        self.bprint("Exams complete, results in: %s" % self.ex.exam_dir)
        return self.buf_history

    def ueye_run(self, max_runs=100):
        """ Main loop for the broaster exam. Turns on the device, waits,
        stores communication results, turns off the device. Repeat.
        """
        
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

            # 993, 591 LAOCT OD button
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
        """ Move the mouse to specified coordinates, click the left button
        """
        import ctypes
        u32 = ctypes.windll.user32
        u32.SetCursorPos(int(posx), int(posy))
        u32.mouse_event(2, 0, 0, 0, 0) # left down
        u32.mouse_event(4, 0, 0, 0, 0) # left up
        
        time.sleep(wait_interval)
        return True

    def send_key_and_enter(self, keystroke):
        """ Send a value and then push enter.
        """

       
        import win32api
        import win32con
        win32api.keybd_event(keystroke, 0, 0, 0)
        time.sleep(1)
        win32api.keybd_event(keystroke, 0, win32con.KEYEVENTF_KEYUP, 0)


        enter_key = 0x0D
        win32api.keybd_event(enter_key, 0, 0, 0)
        time.sleep(1)
        win32api.keybd_event(enter_key, 0, win32con.KEYEVENTF_KEYUP, 0)


    def start_ueye(self):
        """ Start the software from IDS, wait 5 seconds for it to be ready.
        """
        ueye_exec = '''"C:\Program Files\IDS\uEye\Program\uEyeCockpit.exe"'''
          
        from subprocess import Popen
        result = Popen(ueye_exec)
        #print "Startup result: %s, wait 5" % result
        time.sleep(5)
        return True

    def stop_ueye(self):
        """ Kill the software from IDS - no clean, no confirmation, just kill.
        """
        import os
        # > /NUL is to keep the 'sent termination...' message from printing
        # Would be nice to capture it and send it to log
        ueye_kill = '''"taskkill /IM uEyeCockpit.exe 1> NUL 2> NUL"'''
        result = os.system(ueye_kill)
        #print "Kill result: %s" % result
        return True

    def check_for_ueye(self):
        """ List all system processes, return true if uEyeCockpit is found.
        """
        import wmi
        wmi_obj = wmi.WMI()

        for process in wmi_obj.Win32_Process():
            if "uEye" in process.Name:
                #print "Found ueye: %s, %s" % (process.processId, process.Name)
                return True
        return False
    
    def check_for_ueye(self):
        """ List all system processes, return true if uEyeCockpit is found.
        """
        import wmi
        wmi_obj = wmi.WMI()

        for process in wmi_obj.Win32_Process():
            if "uEye" in process.Name:
                #print "Found ueye: %s, %s" % (process.processId, process.Name)
                return True
        return False

    def check_for_Dash(self):
        """ List all system processe, return true if LargeAnimal is found.
        """
        import wmi
        wmi_obj = wmi.WMI()

        for process in wmi_obj.Win32_Process():
            if "Dash" in process.Name:
                return True
        return False

    def start_Dash(self):
        """ Start by double clicking the icon on the desktop. This is
        apparently necessary, as running the executable directory throws
        sapera errors.
        """
        icon_x = 36
        icon_y = 280
        self.move_and_click(icon_x, icon_y, 0.01)
        time.sleep(0.1)
        self.move_and_click(icon_x, icon_y, 0.01)
        return True

    def click_dash_logging(self):
        """ Click the dash logging tab
        """
        self.move_and_click(840, 601, 0.01)
        return True

    def click_dash_cooling(self):
        """ Click in the integration time in the toolbar, set to 3
        """
        self.move_and_click(800, 674, 0.01)
        return True


    def change_dash_integration_time(self):
        """ Click in the integration time in the toolbar, set to 3
        """
        self.move_and_click(544, 637, 0.01)
        time.sleep(0.1)
        self.move_and_click(544, 637, 0.01)

        time.sleep(1)
        self.send_key_and_enter(0x33) # 3 ms integration time

        return True

    def click_dash_settings(self):
        """ Click the settings icon in the toolbar.
        """
        self.move_and_click(770, 790, 0.01)
        return True

    def direct_exec_start_Dash(self):
        """ Start the software from wasatch, wait 5 seconds for it to be
        ready.
        """
        LAOCT_exec = '''"C:\\Wasatch\\Software\\OCT\\LargeAnimal OCT_6_29_15_centerImage\\bin\\Release\\LargeAnimalOCT.exe"'''

        print "Try and open %s" % LAOCT_exec  
        from subprocess import Popen
        result = Popen(LAOCT_exec)
        print "Startup result: %s, wait 5" % result
        time.sleep(5)
        return True

    def stop_Dash(self):
        """ Kill the software from Wasatch - no clean, no confirmation,
        just kill.
        """
        import os
        # > /NUL is to keep the 'sent termination...' message from printing
        # Would be nice to capture it and send it to log
        ueye_kill = '''"taskkill /IM Dash.exe 1> NUL 2> NUL"'''
        result = os.system(ueye_kill)
        #print "Kill result: %s" % result
        return True

    def startup_click_LAOCT(self):
        """ Click the OD button, wait, click the 'live update' button
        Make sure to set the startup icon to maximized to get the window
        in the same position every time.
        """
        self.move_and_click(993, 591)
        time.sleep(1)
        self.move_and_click(967, 764)
        return True
    
    def save_screenshot(self, filename):
        """ Use Pillow to take a screenshot and save to filename.
        """

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
        result = phd_relay.two_off()
        result = phd_relay.one_off()
        result = phd_relay.zero_off()

        time.sleep(wait_interval)

class DashUtils(object):
    """ Helper functions for displaying text and information about the
    program.
    """
    def __init__(self):
        self.dashutils_text = """
###########################################################
#                                                         #
#         ___          _           _   _ _                #
#        /   \__ _ ___| |__  /\ /\| |_(_) |___            #
#       / /\ / _` / __| '_ \/ / \ \ __| | / __|           #
#      / /_// (_| \__ \ | | \ \_/ / |_| | \__ \           #
#      ___,' \__,_|___/_| |_|\___/ \__|_|_|___/           #
#                                                         #
###########################################################
""" 
    def colorama_dashutils(self):
        lines = self.dashutils_text.split('\n')
        colorama.init()
    
        color_str = Fore.RED + lines[1] + '\n'
        color_str += Fore.RED + lines[2] + '\n'
        color_str += Fore.RED + lines[3] + '\n'
        color_str += Fore.RED + lines[4] + '\n'
        color_str += Fore.RED + lines[5] + '\n'
        color_str += Fore.RED + lines[6] + '\n'
        color_str += Fore.RED + lines[7] + '\n'
        color_str += Fore.RED + lines[8] + '\n'
        color_str += Fore.RED + lines[9] + '\n'
        color_str += Fore.RED + lines[10] + '\n'
    
        color_str += Style.RESET_ALL
        return color_str
 
 
if __name__ == "__main__":
    dashutil = DashUtils()
    print dashutil.colorama_dashutils()

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--iterations", type=int, required=True,
                        help="count of power test cylces")
    parser.add_argument("-d", "--description", required=True,
                        help="short description of exam")
    args = parser.parse_args()


    #ids = WasatchCamIDS_Exam(args.description)
    #ids.run(args.iterations)

    dash = WasatchDash_Exam(args.description)
    dash.run(args.iterations)
