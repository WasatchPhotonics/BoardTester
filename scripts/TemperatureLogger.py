""" rough and ready script to collect temperatures from a wasatch
photonics stroker protocol series device. Also uses the ThorLabsMeter
cross platform wrapper from FastPM100 to collect power readings.
"""

import sys
import time
import logging
log = logging.getLogger()
log.setLevel(logging.INFO)

frmt_str = "%(name)s %(levelname)-8s %(message)s"
frmt = logging.Formatter(frmt_str)
strm = logging.StreamHandler(sys.stdout)
strm.setFormatter(frmt)
log.addHandler(strm)


from wasatchusb import stroker_protocol

device = stroker_protocol.StrokerProtocolDevice()
result = device.connect()
print device.get_serial_number()
print device.get_laser_temperature()
print device.get_ccd_temperature()
