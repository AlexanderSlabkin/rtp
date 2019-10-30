'''This is RTP Transmitter for H.264 Payload


'''


import socket
import struct
import sys
from random import getrandbits
from fractions import Fraction as Frac


class Transmitter():

    def __init__(self, file: str='test.h264', address: tuple=('127.0.0.1', 5000),
                 mode: str='single', fps: int=24, SN: int=getrandbits(16),
                 timestamp: int=getrandbits(16), ssrc: bytes=getrandbits(16),
                 cc: bytes = 0, v: int = 2, x: bool=0, m: bool=0) -> object:
        self.address = address
        self.socket_ = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.file = file
        self.mode = mode
        self.SN = SN
        if not 1 < fps < 200:
            print('Error: wrong frame rate')
            sys.exit(2)
        self.delay = Frac((1/fps)*90000)
        self.timestamp = Frac(timestamp, self.delay.denominator)
        self.ssrc = ssrc
        self.cc = cc
        self.v = v
        self.x = x
        self.m = m
        self.packets_send = 0

    def check_prefix(bytestream):
        if bytestream[0:4] == bytes((0,0,0,1)): return True
        return False

    def get_preferences_from_file(self):
        pass



    def make_header(self, type='single', p=0, pt=1, identificator=None, **kwargs):
#        firstbyte = (v << 6) | (p << 5) | (x << 4) | cc
#        secondbyte = (m << 7) | pt
        firstbyte = (self.v) << 6 | (p << 5) | (self.x << 4) | self.cc
        secondbyte = (self.m << 7) | pt
        header = struct.pack('!BBHII', firstbyte, secondbyte, self.SN, round(self.timestamp), self.ssrc)

        return header

    def send_unit(self, unit, type='single', **kwargs):
        if type == 'single':
            pt = 98
            header = self.make_header(type, p=0, pt=pt)
            print(self.address)
            self.socket_.sendto(header+unit, self.address)
            self.SN = (self.SN + 1) % 2**16
            self.timestamp += self.delay
            print(f'Unit {self.SN} send')
            self.packets_send += 1

        elif type == 'FU-A':
            pt = 99
            N = len(unit) / kwargs['packetsize']
            header = self.make_header(type, p=0, pt=pt, identificator= kwargs['identificator'])
            for i in range(N):
                pass

    def transmitt(self, mode: str, packetsize: int) -> object:
        try:
            file = open(self.file, 'rb')
        except FileNotFoundError:
            print('File not found')
            sys.exit(1)
        bytestream = bytearray(file.read())
        while len(bytestream) > 1:
            end = bytestream.find(bytes((0, 0, 0, 1)), 1)
            unit = bytestream[4:end]
            self.send_unit(unit, self.mode)

            del bytestream[:end]

        print(f'While transmitt {self.packets_send} packets were send')









