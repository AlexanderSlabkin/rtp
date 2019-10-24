import socket, struct, math, time, random, sys
from fractions import Fraction as Frac

default_params = ('test.h264', 1199, 50, 1, 260, 0, 0, 0)

# ffmpeg -i file2.mp4 -vcodec copy -an -bsf:v h264_mp4toannexb test.h264

UDP_IP = "127.0.0.1"
UDP_PORT = 5000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

N = len(sys.argv)
filename = str(sys.argv[1]) if N > 1 else default_params[0]
b = int(sys.argv[2]) if N > 2 else default_params[1]
a = int(sys.argv[3]) if N > 3 else default_params[2]
mode = int(sys.argv[4]) if N > 4 else default_params[3]
packetsize = int(sys.argv[5]) if N > 5 else default_params[4]
pad = int(sys.argv[6]) if N > 6 else default_params[5]
delay_status = int(sys.argv[7]) if N > 7 else default_params[6]
print_status = int(sys.argv[7]) if N > 7 else default_params[7]

try:
    file = open(filename, 'rb')
except FileNotFoundError:
    print('file not found')
    sys.exit(1)

if mode is 0:
    # Single NAL Unit Mode
    pt = 98
elif mode is 1:
    # Non-Interleaved Mode
    pt = 99
else:
    print('Error: wrong mode')
    sys.exit(2)
if not 1 < b / a < 150:
    print('Error: wrong frame rate')
    sys.exit(3)
if N < 2:
    print('default parameters is used:')
    print('filename = ' + '"' + str(default_params[0]) + '"', 'b = ' + str(default_params[1]),
          'a = ' + str(default_params[2]),
          'mode = ' + str(default_params[3]), 'packetsize = ' + str(default_params[4]),
          'pad = ' + str(default_params[5]) + '\n', sep='\n')
if pad > 0 and packetsize > 267:
    pad = 0
    print('Padding not available')

cc = 0
csrc = []
unitsize = packetsize - (12 + cc * 4)
if unitsize < 2:
    my_print('Error: Too small packetsize')
    sys.exit(2)

t = time.perf_counter()


def my_print(*args):
    pass


if print_status:
    my_print = print


def my_sleep(arg):
    pass


if delay_status:
    my_sleep = time.sleep

a1 = 0

packets = []

bytestream = file.read()
print('read time:', time.perf_counter() - t)
print('file length:', len(bytestream))


def makeheader(v, p, x, cc, m, pt, sn, timestamp, ssrc, csrc):
    if v > 2 or p > 1 or x > 1 or cc > 15 or m > 1 or pt > 127:
        my_print('error 1: wrong value in makeheader')
    firstbyte = (v << 6) | (p << 5) | (x << 4) | cc
    secondbyte = (m << 7) | pt
    sn = sn % 65536  # page 79
    header = struct.pack('!BBHII', firstbyte, secondbyte, sn, timestamp, ssrc)
    if cc:
        for i in csrc:
            header += struct.pack('!I', i)
    return header


ssrc = random.getrandbits(16)
sn = random.getrandbits(8)

timestamp = ts_start = random.getrandbits(16)
timestamp2 = timestamp
ts_numerator = 0
ts_num_inc = 90000 * a
ts_frac = Frac(0, b)

nal_types = []
sum1, sum2 = 0, 0
start, end = 0, 0
k = 0

n = 0
while not bytestream[n:n + 4] == bytes((0, 0, 0, 1)):
    n += 1
bytestream = bytestream[n + 4:]

timescale = 0
ref_point = time.perf_counter()
print('translation start:', ref_point)


class Transmitter(object):

    def __init__(self, socket):
        self.socket = socket

    def make_header(self, header):
        self.bytes = header + self.bytes

    def transmit(bytestream, mode='single'):
        for index, byte in enumerate(bytestream):
            if byte is 0:
                if bytestream[index + 1:index + 4] == bytes((0, 0, 1)):
                    end = index
                    unit = bytestream[start:end]
                    start = index + 4
                    k += 1
                    if unit[0] & 0b1111 not in nal_types:
                        nal_types.append(unit[0] & 0b1111)
                    unit_len = len(unit)
                    if unit_len > unitsize:
                        # FU-A
                        N = math.ceil((unit_len - 1) / (unitsize - 2))

                        rtp_header = makeheader(2, 0, 0, cc, 0, pt, sn, timestamp, ssrc, csrc)

                        type1 = unit[0] & 0b11111
                        fu_header = type1 | 0b10000000
                        indicator = (unit[0] & 0b11100000) | 0b11100
                        NAL_header = struct.pack('BB', indicator, fu_header)
                        sn += 1

                        packet = rtp_header + NAL_header + unit[1:unitsize - 1]
                        packets.append(packet)
                        sock.sendto(packet, (UDP_IP, UDP_PORT))

                        NAL_header = struct.pack('BB', indicator, type1)
                        for i in range(1, N - 1):
                            rtp_header = makeheader(2, 0, 0, cc, 0, pt, sn, timestamp, ssrc, csrc)
                            sn += 1
                            packet = rtp_header + NAL_header + unit[(unitsize - 2) * i + 1:(unitsize - 2) * (i + 1) + 1]
                            packets.append(packet)
                            sock.sendto(packet, (UDP_IP, UDP_PORT))

                        fu_header = type1 | 0b1000000
                        NAL_header = struct.pack('BB', indicator, fu_header)
                        rtp_header = make_header(2, 0, 0, cc, 0, pt, sn, timestamp, ssrc, csrs)
                        sn += 1

                        if type1 in [1, 5]:
                            ts_numerator += ts_num_inc
                            timestamp = ts_start + math.ceil(ts_numerator / b)
                            ts_frac += Frac(ts_num_inc, b)
                            my_print(timestamp, ts_frac)
                            curtime = time.perf_counter() - ref_point
                            if timescale - curtime > 0:
                                my_sleep(timescale - curtime)
                            a1 += a
                            my_print(timescale)
                            timescale = a1 / b
                        packet = rtpheader + NALheader + unit[(N - 1) * (unitsize - 2) + 1:]
                        packets.append(packet)
                        sock.sendto(packet, (UDP_IP, UDP_PORT))


if mode is 1 and pad is 0:
    for index, byte in enumerate(bytestream):
        if byte is 0:
            if bytestream[index + 1:index + 4] == bytes((0, 0, 1)):
                end = index
                unit = bytestream[start:end]
                start = index + 4
                k += 1
                if unit[0] & 15 not in nal_types:
                    nal_types.append(unit[0] & 15)
                if len(unit) > unitsize:
                    # FU-A
                    N = math.ceil((len(unit) - 1) / (unitsize - 2))
                    sum2 += N
                    type1 = unit[0] & 31
                    fuheader = 128 | type1
                    indicator = (unit[0] & 224) | 28
                    NALheader = struct.pack('BB', indicator, fuheader)
                    rtpheader = makeheader(2, 0, 0, cc, 0, pt, sn, timestamp, ssrc, csrc)
                    sn += 1
                    packet = rtpheader + NALheader + unit[1:unitsize - 1]
                    packets.append(packet)
                    sock.sendto(packet, (UDP_IP, UDP_PORT))
                    fuheader = 0 | type1
                    NALheader = struct.pack('BB', indicator, fuheader)
                    for i in range(1, N - 1):
                        rtpheader = makeheader(2, 0, 0, cc, 0, pt, sn, timestamp, ssrc, csrc)
                        sn += 1
                        packet = rtpheader + NALheader + unit[(unitsize - 2) * i + 1:(unitsize - 2) * (i + 1) + 1]
                        packets.append(packet)
                        sock.sendto(packet, (UDP_IP, UDP_PORT))
                    fuheader = 64 | type1
                    NALheader = struct.pack('BB', indicator, fuheader)
                    rtpheader = makeheader(2, 0, 0, cc, 0, pt, sn, timestamp, ssrc, csrc)
                    sn += 1
                    if type1 in [1, 5]:
                        ts_numerator += ts_num_inc
                        timestamp = ts_start + math.ceil(ts_numerator / b)
                        ts_frac += Frac(ts_num_inc, b)
                        my_print(timestamp, ts_frac)
                        curtime = time.perf_counter() - ref_point
                        if timescale - curtime > 0:
                            my_sleep(timescale - curtime)
                        a1 += a
                        my_print(timescale)
                        timescale = a1 / b
                    packet = rtpheader + NALheader + unit[(N - 1) * (unitsize - 2) + 1:]
                    packets.append(packet)
                    sock.sendto(packet, (UDP_IP, UDP_PORT))
                else:
                    rtpheader = makeheader(2, 0, 0, cc, 0, pt, sn, timestamp, ssrc, csrc)
                    sn += 1
                    type1 = unit[0] & 31
                    if type1 in [1, 5]:
                        ts_numerator += ts_num_inc
                        timestamp = ts_start + math.ceil(ts_numerator / b)
                        curtime = time.perf_counter() - ref_point
                        if timescale - curtime > 0:
                            my_sleep(timescale - curtime)
                        a1 += a
                        my_print(timescale)
                        timescale = a1 / b
                    packet = rtpheader + unit
                    sum1 += 1
                    packets.append(packet)
                    sock.sendto(packet, (UDP_IP, UDP_PORT))
elif mode is 1 and pad > 0:
    for index, byte in enumerate(bytestream):
        if byte is 0:
            if bytestream[index + 1:index + 4] == bytes((0, 0, 1)):
                end = index
                unit = bytestream[start:end]
                start = index + 4
                k += 1
                if unit[0] & 15 not in nal_types:
                    nal_types.append(unit[0] & 15)
                if len(unit) > unitsize:
                    # FU-A
                    N = math.ceil((len(unit) - 1) / (unitsize - 2))
                    sum2 += N
                    type1 = unit[0] & 31
                    fuheader = 128 | type1
                    indicator = (unit[0] & 224) | 28
                    NALheader = struct.pack('!BB', indicator, fuheader)
                    rtpheader = makeheader(2, 0, 0, cc, 0, pt, sn, timestamp, ssrc, csrc)
                    sn += 1
                    packet = rtpheader + NALheader + unit[1:unitsize - 1]
                    packets.append(packet)
                    sock.sendto(packet, (UDP_IP, UDP_PORT))
                    fuheader = 0 | type1
                    NALheader = struct.pack('!BB', indicator, fuheader)
                    for i in range(1, N - 1):
                        rtpheader = makeheader(2, 0, 0, cc, 0, pt, sn, timestamp, ssrc, csrc)
                        sn += 1
                        packet = rtpheader + NALheader + unit[(unitsize - 2) * i + 1:(unitsize - 2) * (i + 1) + 1]
                        packets.append(packet)
                    fuheader = 64 | type1
                    NALheader = struct.pack('!BB', indicator, fuheader)
                    paddingsize = unitsize - 2 - len(unit[(N - 1) * (unitsize - 2) + 1:])
                    if paddingsize:
                        rtpheader = makeheader(2, pad, 0, cc, 0, pt, sn, timestamp, ssrc, csrc)
                        packet = rtpheader + NALheader + unit[(N - 1) * (unitsize - 2) + 1:] + bytes(
                            [0] * (paddingsize - 1)) + bytes([paddingsize])
                    else:
                        rtpheader = makeheader(2, 0, 0, cc, 0, pt, sn, timestamp, ssrc, csrc)
                        packet = rtpheader + NALheader + unit[(N - 1) * (unitsize - 2) + 1:]
                    sn += 1
                    if type1 in [1, 5]:
                        ts_numerator += ts_num_inc
                        timestamp = ts_start + math.ceil(ts_numerator / b)
                        curtime = time.perf_counter() - ref_point
                        if timescale - curtime > 0:
                            my_sleep(timescale - curtime)
                        a1 += a
                        my_print(timescale)
                        timescale = a1 / b
                    packets.append(packet)
                    sock.sendto(packet, (UDP_IP, UDP_PORT))
                else:
                    paddingsize = unitsize - len(unit)
                    if paddingsize:
                        rtpheader = makeheader(2, pad, 0, cc, 0, pt, sn, timestamp, ssrc, csrc)
                        packet = rtpheader + unit + bytes([0] * (paddingsize - 1)) + bytes([paddingsize])
                    else:
                        rtpheader = makeheader(2, 0, 0, cc, 0, pt, sn, timestamp, ssrc, csrc)
                        packet = rtpheader + unit
                    sn += 1
                    type1 = unit[0] & 31
                    if type1 in [1, 5]:
                        ts_numerator += ts_num_inc
                        timestamp = ts_start + math.ceil(ts_numerator / b)
                        curtime = time.perf_counter() - ref_point
                        if timescale - curtime > 0:
                            my_sleep(timescale - curtime)
                        a1 += a
                        my_print(timescale)
                        timescale = a1 / b
                    sum1 += 1
                    packets.append(packet)
                    sock.sendto(packet, (UDP_IP, UDP_PORT))

elif mode is 0:
    for index, byte in enumerate(bytestream):
        if byte is 0:
            if bytestream[index + 1:index + 4] == bytes((0, 0, 1)):
                end = index
                unit = bytestream[start:end]
                start = index + 4
                k += 1
                rtpheader = makeheader(2, 0, 0, cc, 0, pt, sn, timestamp, ssrc, csrc)
                sn += 1
                type1 = unit[0] & 31
                if type1 in [1, 5]:
                    ts_numerator += ts_num_inc
                    timestamp = ts_start + math.ceil(ts_numerator / b)
                    curtime = time.perf_counter() - ref_point
                    if timescale - curtime > 0:
                        my_sleep(timescale - curtime)
                    a1 += a
                    my_print(timescale)
                    timescale = a1 / b
                packet = rtpheader + unit
                sum1 += 1
                packets.append(packet)
                sock.sendto(packet, (UDP_IP, UDP_PORT))

file.close()
print('types: ', nal_types)
print('time to send:', str(time.perf_counter() - ref_point) + ';', 'NAL-units send:', k)
print('packets: ' + str(len(packets)) + ';', 'singles: ' + str(sum1) + ';', 'fus: ' + str(sum2))
