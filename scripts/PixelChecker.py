import time

from phidgeter import relay

import wasatchusb
from wasatchusb import feature_identification


def print_pixel():
    """ Print the default set of data from the device. To diagnose these
    individually, see the wasatchusb/test/test_feature_identification.py
    file.
    """

    dev_list = feature_identification.ListDevices()
    result = dev_list.get_all()
    if result == []:
        print "No devices found!"
        sys.exit(1)

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

    data = device.get_line()
    avg_data =  sum(data) / len(data)
    #print ""
    #print "Grab Data: %s pixels" % len(data)
    print "Min: %s Max: %s Avg: %s" \
            % (min(data), max(data), avg_data)

    pixel_range = [270, 271, 272, 273, 274, 275]
    print "270    271    272    273    274    275"
    for pix in pixel_range:
        print "%s " %  data[pix],
    print ""

    return data


def write_data(raw_data, filename="csvout.csv"):
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
while stop_test == False:
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

    write_data(raw_data)

