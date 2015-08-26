""" process data collected from broaster, list failure rates

usage:
    python process.py -d "known test description"

Prints a summary of useful information about failure rates as recorded
by the broaster.
"""

import argparse

from broaster import BroasterUtils
from broaster import ProcessBroaster

if __name__ == "__main__":
    butil = BroasterUtils()
    print butil.colorama_broaster()

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--description", required=True,
        help="short description of exam")
    parser.add_argument("-n", "--node", 
        help="With summarize as description, process this entire node")
    args = parser.parse_args()

    proc = ProcessBroaster()

    if args.description == "summarize":
        result = proc.process_mti_group(args.node)
        print "result is: %s" % result
        
    else:
        print "Searching for results file matching: %s" % args.description

        filename = proc.find_log(args.description)
        if filename == "not found":
            print "Cannot find description: %s" % args.description
        else:
            result = proc.process_log(filename)
            print "\n%s\n" % result
