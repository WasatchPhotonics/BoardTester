import time
import sys
import logging
log = logging.getLogger(__name__)

from phidgeter import relay

import wasatchusb
from wasatchusb import feature_identification

total_count = 0

def print_pixel():
    """ Print the default set of data from the device. To diagnose these
    individually, see the wasatchusb/test/test_feature_identification.py
    file.
    """

    dev_list = feature_identification.ListDevices()
    result = dev_list.get_all()
    if result == []:
        print "No devices found!"
        return []

    dev_count = 0
    #for item in dev_list.get_all():
        #print "Device: %s     VID: %s PID: %s" \
               #% (dev_count, item[0], item[1])
        #dev_count += 1

    last_device = dev_list.get_all()[-1]
    last_pid = int(last_device[1], 16)
    #print "Connect to last device pid: %s" % last_pid

    device = feature_identification.Device(pid=last_pid)
    device.connect()

    integration_time = 100
    print "Set integration time: %s" % integration_time
    device.set_integration_time(100)


    data = device.get_line()
    avg_data =  sum(data) / len(data)
    #print ""
    #print "Grab Data: %s pixels" % len(data)
    print "Min: %s Max: %s Avg: %s" \
            % (min(data), max(data), avg_data)

    pixel_range = [270, 271, 272, 273, 274, 275]
    print "%s Pixels:" % total_count,
    for idx in pixel_range:
        print "{:8}".format(idx),
    print ""

    print "%s Values:" % total_count,
    for pix in pixel_range:
        print "{:8}".format(data[pix]),
    print ""

    return data



def write_data(raw_data, filename="on_server_link/csvout.csv"):
    """ Append the specified pixel data in csv format to a text file.
    """
    with open(filename, "a") as out_file:
        for pixel in raw_data:
            out_file.write("%s," % pixel)
        out_file.write("\n")



phd_relay = relay.Relay()

stop_test = False
off_wait_interval = 3
on_wait_interval = 10

raw_data = range(0, 0, 512)

try:
    phd_relay.one_off()
    print "Off Wait %s..." % off_wait_interval
    time.sleep(off_wait_interval)
    phd_relay.one_on()

    print "On Wait %s..." % on_wait_interval
    time.sleep(on_wait_interval)


    raw_data = print_pixel()
    phd_relay.one_off()

except Exception as exc:
    print "Failure, writing blank line: %s" % exc

#filename = datetime.strptime(datetime.now(),
                             #"Start_%Y_%m_%d_%H_%M_%S.csv")
write_data(raw_data)
total_count += 1

