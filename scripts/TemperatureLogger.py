""" rough and ready script to collect temperatures from a wasatch
photonics stroker protocol series device. Also uses the ThorLabsMeter
cross platform wrapper from FastPM100 to collect power readings.

Output:
    Create/Append to filename (default: combined_log.csv)
    timestamp: min,max,avg CCD Temp  min,max,avg Laser Temp,
               min,max,avg PM100 Reading



Example configuration:

    Start the Thorlabs Optical power meter software
    Set wavelength to 785

    cd BoardTester
    python setup.py develop
    python scripts/TemperatureLogger.py 

"""

import sys
import time
import numpy
import logging
log = logging.getLogger()
log.setLevel(logging.INFO)

frmt_str = "%(levelname)-8s %(message)s"
frmt = logging.Formatter(frmt_str)
strm = logging.StreamHandler(sys.stdout)
strm.setFormatter(frmt)
log.addHandler(strm)


from wasatchusb import stroker_protocol
from fastpm100 import devices

pm100usb = devices.ThorlabsMeter()

device = stroker_protocol.StrokerProtocolDevice()
result = device.connect()
serial = device.get_serial_number()

laser_enable_wait = 1
log.info("Turn laser on, wait %s seconds", laser_enable_wait)
device.set_laser_enable(1)
time.sleep(laser_enable_wait)

filename = "combined_log.csv"
log.info("Starting log of: %s to %s", serial, filename)

period = 1
samples = 10
log.info("Logging %s samples every %s seconds", samples, period)

l_temps = []
c_temps = []
l_power = []

def init_data():
    l_temps = []
    c_temps = []
    l_power = []

def write_data():
    l_temp_grp  = [min(l_temps), max(l_temps), numpy.average(l_temps)]
    c_temp_grp  = [min(c_temps), max(c_temps), numpy.average(c_temps)]
    l_power_grp = [min(l_power), max(l_power), numpy.average(l_power)]

    combined_data = l_temp_grp, c_temp_grp, l_power_grp
    log.warn("Combined: %s", combined_data)

def get_data():
    l_temps.append(device.get_laser_temperature())
    c_temps.append(device.get_ccd_temperature())
    l_power.append(pm100usb.read())


stop_log = False
init_data()
get_data()

start_time = time.time()

while not stop_log:
    time.sleep(period + 1.0)
    now_time = time.time()

    curr_time = abs(now_time - start_time)


    if curr_time >= period:
        log.warn("Write to file")
        write_data()
        init_data()
        start_time = time.time()


    else:
        get_data()

    stop_log = True


#device.set_laser_enable(0)
