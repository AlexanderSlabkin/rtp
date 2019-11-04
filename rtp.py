"""This is RTP Transmitter for H.264 Payload


"""


import socket
import struct
import sys
from math import ceil
from random import getrandbits
from fractions import Fraction as Frac


class Transmitter:

    type_mask = 0b11111
    nri_mask = 0b11100000
    unit_types = {'FU-A': 28, 'FU-B': 29}
    fu_a_type = 28
    fu_b_type = 29
    pt = {'FU-A': 99, 'single': 98}

    def __init__(self, file: str = 'test.h264', address: tuple = ('127.0.0.1', 5000),
                 mode: str = 'single', fps: int = 24, sn: int = getrandbits(16),
                 timestamp: int = getrandbits(16), ssrc: bytes = getrandbits(16),
                 cc: int = 0, v: int = 2, x: bool = 0, m: bool = 0):
        self.address = address
        self.socket_ = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.file = file
        self.mode = mode
        self.sn = sn
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

    @staticmethod
    def check_prefix(bytestream):
        if bytestream[0:4] == bytes((0, 0, 0, 1)):
            return True
        return False

    def get_preferences_from_file(self):
        pass

    def make_header(self, p=0, **kwargs) -> bytes:
        nal_header = bytes()
        if kwargs['rtp_type'] == 'FU-A':
            unit_type = kwargs['first_byte'] & self.type_mask
            unit_nri = kwargs['first_byte'] & self.nri_mask
            fu_header = unit_type
            indicator = self.unit_types[kwargs['rtp_type']] | unit_nri
            if kwargs['flag'] == 's':
                fu_header = 0b10000000 | fu_header
            elif kwargs['flag'] == 'e':
                fu_header = 0b01000000 | fu_header
            nal_header = struct.pack('!BB', indicator, fu_header)

        first_byte = self.v << 6 | (p << 5) | (self.x << 4) | self.cc
        second_byte = (self.m << 7) | self.pt[kwargs['rtp_type']]
        rtp_header = struct.pack('!BBHII', first_byte, second_byte, self.sn, round(self.timestamp), self.ssrc)

        header = rtp_header + nal_header

        return header

    # def send_packet(self,):

    def send_unit(self, unit, rtp_type='single', **kwargs):
        if rtp_type == 'single':
            header = self.make_header(rtp_type=rtp_type, p=0)
            self.socket_.sendto(header+unit, self.address)
            self.packets_send += 1

        elif rtp_type == 'FU-A':
            unit_size = kwargs['unit_size']
            n = ceil((len(unit)-1) / unit_size-2)
            header = self.make_header(p=0, flag='s', first_byte=unit[0],
                                      rtp_type=rtp_type)
            self.socket_.sendto(header + unit[1:unit_size-1], self.address)
            self.packets_send += 1
            for i in range(1, n-1):
                header = self.make_header(p=0, first_byte=unit[0], flag='m',
                                          rtp_type=rtp_type)
                self.socket_.sendto(header + unit[(unit_size-2)*i+1:(unit_size-2)*(i+1)+1], self.address)
                self.packets_send += 1
            header = self.make_header(p=0, first_byte=unit[0], rtp_type=rtp_type, flag='e')
            self.socket_.sendto(header + unit[(unit_size-2)*(n-1)+1:], self.address)
            self.packets_send += 1

        self.sn = (self.sn + 1) % 2 ** 16
        self.timestamp += self.delay
        print(f'Unit {self.sn} send')

    def transmit(self, mode: str = None, packet_size: int = 260) -> object:
        try:
            file = open(self.file, 'rb')
        except FileNotFoundError:
            print('File not found')
            sys.exit(1)
        bytestream = bytearray(file.read())
        unit_size = None

        if mode:
            self.mode = mode

        if self.mode == 'FU-A':
            unit_size = packet_size - (12 + self.cc * 4)
            if unit_size < 2:
                print('Error: Too small packet_size')
                sys.exit(2)

        while len(bytestream) > 1:

            end = bytestream.find(bytes((0, 0, 0, 1)), 1)
            unit = bytestream[4:end]
            self.send_unit(unit, self.mode, unit_size=unit_size)

            del bytestream[:end]

        print(f'While transmission {self.packets_send} packets were send')

        return 0
