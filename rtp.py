#!/usr/bin/env python3

"""This is script for RTP transmission of H.264


"""

import argparse

from transmission import Transmitter

from reception import Receiver


parser = argparse.ArgumentParser(description='Sending/receiving H.264 via UDP to/from specified address')
parser.add_argument('-i', '--file', type=str, dest='File', default='test.h264',
                    help='Destination file in receive mode or file that should be send in transmit mode ')
parser.add_argument('-m', '--mode', type=str, dest='Mode', default='single')
parser.add_argument('-a', '--address', '--ip', type=str, dest='IP', default='127.0.0.1')
parser.add_argument('-p', '--port', type=int, dest='Port', default=5000)
parser.add_argument('-r', '--receive', dest='receive_flag', action='store_true', default=False)
parser.add_argument('-t', '--transmit', dest='transmit_flag', action='store_true', default=False)

args = parser.parse_args()

print(args.receive_flag)
if args.transmit_flag:
    T = Transmitter(args.File, (args.IP, args.Port), args.Mode)
    T.transmit()

if args.receive_flag:
    R = Receiver(args.File, (args.IP, args.Port), args.Mode)