'''This is RTP Transmitter for H.264 Payload


'''


import socket
import struct
from random import getrandbits
from fractions import Fraction as Frac


class Transmitter():

    def __init__(self, file, address, mode='single', SN=getrandbits(16), timestamp=getrandbits(16), fps=24):
        self.address = address
        self.mode = mode
        self.SN = SN
        self.timestamp = timestamp
        self.socket_ = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.delay = Frac(1/fps)

    def send_unit(self, unit, type='single'):
        header = make_header(unit, type, identificator = None)
        self.socket_.sendto(header+unit, **self.address)



