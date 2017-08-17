""" rough and ready script to collect laser power readings only and
write to disk

Example configuration:

    Start the Thorlabs Optical power meter software
    Set wavelength to 785, set high gain, no averaging

    cd BoardTester
    python setup.py develop
    python scripts/TemperatureLogger.py

"""

import os
import sys
import time
import numpy
import logging
import datetime
import zmq
log = logging.getLogger()
log.setLevel(logging.INFO)

frmt_str = "%(asctime)-8s %(message)s"
frmt = logging.Formatter(frmt_str)
strm = logging.StreamHandler(sys.stdout)
strm.setFormatter(frmt)
log.addHandler(strm)


from wasatchusb import stroker_protocol
from fastpm100 import devices

pm100usb = devices.ThorlabsMeter()
try:
    result = pm100usb.read()
except Exception as exc:
    print "Problem setting up power meter: %s" % exc
    print "Continuing without power meter"
    pm100usb = None


filename = "combined_log.csv"
log.info("Starting log of: %s", filename)

period = 1
samples = 1000
sleep_interval = (float(period) / float(samples))
log.info("Logging %s samples every %s seconds (sample rate: %s)", \
         samples, period, sleep_interval)


l_temps = []
c_temps = []
l_power = []

y_therm = []
b_therm = []
e_amper = []

def write_data():

    # Format of csv file is:
    # Tiemstamp, min, max, average of all readings, all readings
    l_power_grp = [min(l_power), max(l_power), numpy.average(l_power)]
    l_power_grp.extend(l_power)

    timestamp = datetime.datetime.now()
    with open(filename, "a") as out_file:
        out_file.write("%s," % timestamp)

        # Laser power groups:
        pow_str = ""
        for item in l_power_grp:
            out_file.write("%s," % item)
        pow_str += "%2.2f," % item

        out_file.write("\n")

        log.info("%s", pow_str)

def get_data():
    l_power.append(pm100usb.read())



stop_log = False
start_time = time.time()


while not stop_log:
    # Sample every sleep interval, write at every period
    time.sleep(sleep_interval)
    now_time = time.time()

    curr_time = abs(now_time - start_time)

    if curr_time >= period:
        write_data()
        l_power = []
        start_time = time.time()


    else:
        log.debug("Get data")
        get_data()


