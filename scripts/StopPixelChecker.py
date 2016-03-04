""" rough and ready script to collect five lines of data, look for any
anomalies, and stop.


Example run:
watch --beep --errexit --chgexit python -u scripts/StopPixelChecker.py

"""

import time
import sys
import logging
from boardtester import reporter
log = logging.getLogger(__name__)

from phidgeter import relay

import wasatchusb
from wasatchusb import feature_identification

total_count = 0

def group_pixel():
    """ Like print_pixel below, but reuse the connection and get max_count acquisitions.
    """

    dev_list = feature_identification.ListDevices()
    result = dev_list.get_all()
    if result == []:
        print "No devices found!"
        sys.exit(2)

    dev_count = 0
    last_device = dev_list.get_all()[-1]
    last_pid = int(last_device[1], 16)

    device = feature_identification.Device(pid=last_pid)
    device.connect()

    integration_time = 100
    print "Set integration time: %s" % integration_time
    device.set_integration_time(100)

    # Make sure the data is empty first
    group_data = []
    max_count = 5
    for item in range(max_count):
        group_data.append(range(0, 0, 512))

    for line_item in range(max_count):
        data = device.get_line()
        if data[0] != 1:
            print "Exit First pixel non-one: %s" % data[0]
            sys.exit(1)
        if data[-1] != 512:
            print "Exit Last pixel non-five twelve: %s" % data[-1]
            sys.exit(1)


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
        group_data[line_item] = data

    return group_data

def write_data(raw_data, filename="on_server_link/csvout.csv"):
    """ Append the specified pixel data in csv format to a text file.
    """
    with open(filename, "a") as out_file:
        for pixel in raw_data:
            out_file.write("%s," % pixel)
        out_file.write("\n")

def write_group(group_data, filename="on_server_link/group_out.csv"):
    """ Append the specified group of pixel data in csv format to a text file.
    """
    for line_item in group_data:
        with open(filename, "a") as out_file:
            for pixel in line_item:
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

    group_data = group_pixel()

    phd_relay.one_off()

except Exception as exc:
    print "Failure, writing blank line: %s" % exc

#write_data(raw_data)
#update_html_report(raw_data)

write_group(group_data)

total_count += 1

