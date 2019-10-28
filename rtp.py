'''This is RTP Transmitter for H.264 Payload


'''


import socket
import struct
from random import getrandbits
from fractions import Fraction as Frac


class Transmitter():

    def __init__(self, file, address, mode='single', fps=24, SN=getrandbits(16), timestamp=getrandbits(16)):
        self.address = address
        self.socket_ = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.file = file
        self.mode = mode
        self.SN = SN
        self.delay = Frac(1/fps)
        self.timestamp = Frac(timestamp, self.delay.denominator)

    def check_prefix(bytestream):
        if bytestream[0:4] == bytes((0,0,0,1)): return True
        return False

    def get_preferences_from_file(self.file):



    def make_header(self, unit, type='single', identificator=None, *args, **kwargs):
#        firstbyte = (v << 6) | (p << 5) | (x << 4) | cc
        firstbyte = (args[0]) | (args[1] << p) | (args[2] << 4) | cc
        secondbyte = (m << 7) | pt

        header = struct.pack('!BBHII', firstbyte, secondbyte, self.SN, self.timestamp, ssrc)

        return header

    def send_unit(self, unit, type='single', **kwargs):
        if type == 'single':
        header = self.make_header(unit, type, kwargs['identificator'])
        self.socket_.sendto(header+unit, **self.address)
        self.SN = (self.SN + 1) % 2**16
        self.timestamp += self.delay

        elif type == 'FU-A':
            N = len(unit) / kwargs['packetsize']
            for i in range(N):

    def transmitt(self):






