#!/usr/bin/env python3

"""This is script for RTP transmission of H.264


"""

import argparse

from rtp import Transmitter


parser = argparse.ArgumentParser(description='Sending H.264 via UDP to specified address')
parser.add_argument('-i', '--infile', type=str, dest='File', default='test.h264')
parser.add_argument('-m', '--mode', type=str, dest='Mode', default='single')
parser.add_argument('-a', '--address', '--ip', type=str, dest='IP', default='127.0.0.1')
parser.add_argument('-p', '--port', type=int, dest='Port', default=5000)

args = parser.parse_args()

T = Transmitter(args.File, (args.IP, args.Port), args.Mode)

T.transmit()
