#!/usr/bin/env python3

import argparse
import smbus2
import sys

def getArgs():
    parser = argparse.ArgumentParser()
    # filename of table, required as can mix between buses
    parser.add_argument('-b', '--bus', required=True)
    parser.add_argument('-o', '--old', required=True)
    # sensor bus
    parser.add_argument('-n', '--new', required=True)
    return parser.parse_args()

if __name__ == '__main__':
    args = getArgs()
    bus = int(args.bus)
    old_address = int(args.old, 0)
    new_address = int(args.new, 0)
    print(new_address, old_address)
    try:
        DEV_CTX = smbus2.SMBus(bus)
        DEV_CTX.write_i2c_block_data(old_address, 0x00, [0x02, 0x00, 0x01,
            new_address, 0xff])
    except IOError as e:
        print(e.message)
        sys.exit(1)
