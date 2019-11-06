"""This is RTP Transmitter for H.264 Payload


"""


import socket
import struct
import sys
from math import ceil
from time import perf_counter
from time import sleep
from random import getrandbits
from fractions import Fraction as Frac


class Transmitter:
    type_mask = 0b11111
    nri_mask = 0b11100000
    unit_types = {'FU-A': 28, 'FU-B': 29}
    pt = {'FU-A': 99, 'single': 98}

    def __init__(self, file: str = 'test.h264', address: tuple = ('127.0.0.1', 5000),
                 mode: str = 'single', fps: int = 24, sn: int = getrandbits(16),
                 timestamp: bytes = getrandbits(16), ssrc: bytes = getrandbits(16),
                 cc: int = 0, v: int = 2, x: bool = 0, m: bool = 0):
        self.address = address
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.file = file
        self.mode = mode
        self.sn = sn
        if not 1 < fps < 200:
            print('Error: wrong frame rate')
            sys.exit(1)
        self.delay = Frac((1/fps)) * 90000
        self.timestamp = timestamp * self.delay
        print(round(self.timestamp), self.timestamp)
        self.ssrc = ssrc
        self.cc = cc
        self.v = v
        self.x = x
        self.m = m
        self.packets_send = 0
        self.timescale = Frac(0.0)
        self.delay1 = Frac(1/fps)
        self.ref_point = 0
        self.delay_status = True
        if self.delay_status:
            self.my_sleep = sleep
        self.print_status = False
        if self.print_status:
            self.my_print = print

    @staticmethod
    def my_sleep(delay):
        pass

    @staticmethod
    def my_print(*args):
        pass

    def get_preferences_from_file(self):
        pass

    @staticmethod
    def cut_slices(unit, fu_a_size) -> iter:
        n = ceil((len(unit) - 1) / fu_a_size - 2)
        for i in range(n):
            yield unit[(fu_a_size-2)*i+1:(fu_a_size-2)*(i+1)+1]

    def generate_sdp(self):
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
        rtp_header = struct.pack('!BBHII', first_byte, second_byte, self.sn,
                                 round(self.timestamp), self.ssrc)

        header = rtp_header + nal_header

        return header

    def send_packet(self, packet) -> None:
        self.sock.sendto(packet, self.address)
        self.sn = (self.sn + 1) % 2 ** 16
        self.packets_send += 1

    def time_job(self, first_byte):
        if first_byte & self.type_mask in [1, 5]:
            self.timestamp += self.delay
            current_time = perf_counter() - self.ref_point
            delay = self.timescale - current_time
            if delay > 0:
                self.my_sleep(delay)
            self.timescale += self.delay1
            self.my_print(float(self.timescale))

    def send_unit_single(self, unit, rtp_type='single') -> None:
        header = self.make_header(rtp_type=rtp_type, p=0)
        self.send_packet(header+unit)
        self.time_job(unit[0])

    def send_unit_fu_a(self, unit, rtp_type='FU-A', **kwargs):
        fu_a_size, padding_size = kwargs['fu_a_size'], 0
        # fu_a = self.cut_slices(unit, fu_a_size)
        # header = self.make_header(p=0, first_byte=unit[0], rtp_type=rtp_type, flag='s')
        # self.send_packet(header + next(fu_a))
        # for i in fu_a:
        #     header = self.make_header(p=0, first_byte=unit[0], rtp_type=rtp_type,
        #                               flag='m')
        #     self.send_packet(header + i)
        # header = self.make_header(p=0, first_byte=unit[0], rtp_type=rtp_type, flag='e')
        # self.send_packet(header + next(fu_a))
        n = ceil((len(unit) - 1) / (fu_a_size - 2))
        header = self.make_header(p=0, flag='s', first_byte=unit[0],
                                  rtp_type=rtp_type)
        self.send_packet(header + unit[1:fu_a_size - 1])
        for i in range(1, n - 1):
            header = self.make_header(p=0, first_byte=unit[0], flag='m',
                                      rtp_type=rtp_type)
            self.send_packet(header + unit[(fu_a_size - 2) * i + 1:(fu_a_size - 2) * (i + 1) + 1])
        padding_size, p = fu_a_size - 2 - len(unit[(fu_a_size - 2) * (n - 1) + 1:]), int(padding_size > 0)
        header = self.make_header(p=p, first_byte=unit[0], rtp_type=rtp_type, flag='e')
        self.send_packet(
            header + unit[(fu_a_size - 2) * (n - 1) + 1:]
            + p*(bytes([0]*(padding_size-1))
                 + bytes([padding_size]))
                        )
        self.time_job(unit[0])

    def transmit(self, mode: str = None, packet_size: int = 260) -> None:
        try:
            file = open(self.file, 'rb')
            bytestream = bytearray(file.read())
        except FileNotFoundError:
            print('File not found')
            sys.exit(2)
        fu_a_size = None
        print(f'File opened successfully, transmitting {self.file} to {self.address[0]:s}, port: {self.address[1]}')

        senders = {'single': self.send_unit_single, 'FU-A': self.send_unit_fu_a}

        if mode:
            self.mode = mode

        if self.mode == 'FU-A':
            fu_a_size = packet_size - (12 + self.cc * 4)
            if fu_a_size < 32:
                print('Error: Too small packet_size')
                sys.exit(3)

        send = senders[self.mode]
        k = 0
        self.ref_point = perf_counter()
        while len(bytestream) > 1:

            end = bytestream.find(bytes((0, 0, 0, 1)), 1)
            unit = bytestream[4:end]
            send(unit, self.mode, fu_a_size=fu_a_size)

            del bytestream[:end]
            k += 1

        print(f'While transmission {self.packets_send} packets and {k} units were send')
