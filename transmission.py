'''This is script for RTP transmission of H.264


'''

import argparse

from rtp import Transmitter


parser = argparse.ArgumentParser(description='Sending H.264 via UDP to specified address')
parser.add_argument('-i', '--infile', type=str, dest='File')
parser.add_argument('-m', '--mode', type=str, dest='Mode')
parser.add_argument('-a', '--address', '--ip', type=str, dest='IP')
parser.add_argument('-p', '--port', type=int, dest='Port')


args = parser.parse_args()

T = Transmitter(args.File, (args.IP, args.Port), 'single')

T.transmitt()

