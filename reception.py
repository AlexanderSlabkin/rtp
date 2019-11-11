"""



"""

import socket
import struct


class Receiver:
    def __init__(self, file: str = 'received1.h264', address: tuple = ('127.0.0.1', 5000), mode: str = 'single'):
        self.address = address
        self.mode = mode
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(address)
        self.sock.settimeout(5.0)
        self.packets_received = 0
        self.file = file

    def receive(self):
        nals = []
        fu_data = b''
        while True:
            try:
                data = self.sock.recvfrom(65565)

            except socket.timeout:
                print(f'Packets received: {self.packets_received}')
                break

            packet = data[0]
            self.packets_received += 1
            print(len(packet))
            fb, sb, seqnum, timestamp = struct.unpack("!BBHI", packet[:8])  # RTP header

            pad = (fb >> 5) & 1
            ext = (fb >> 4) & 1
            cc = fb & 15
            mark = (sb >> 7) & 1

            if pad > 3 or pad < 0:
                continue

            extsize = struct.unpack("!xxH", packet[12 + 4 * cc:16 + 4 * cc])[0] if ext else 0
            padsize = 0
            if pad == 1:
                padsize = struct.unpack("!B", packet[-1:])[0]

            data = packet[12 + 4 * (cc + ext + extsize):-padsize] if pad else packet[12 + 4 * (cc + ext + extsize):]

            if not len(data):
                continue

            nalheader = struct.unpack("!B", data[:1])[0]
            nalf = (nalheader >> 7) & 1
            nalnri = (nalheader >> 5) & 3
            naltype = nalheader & 31
            if 0 < naltype < 24:  # single unit
                print('lol %d' % len(nals))
                nals.append(data)
            elif naltype == 24:  # stap-a
                nal_data = data[1:]
                while len(nal_data):
                    nal_size = struct.unpack("!H", nal_data[:2])[0]
                    nal_data = nal_data[2:]
                    tdata = nal_data[:nal_size]
                    nals.append(tdata)
                    nal_data = nal_data[nal_size:]
            elif naltype == 28:  # fu-a
                fuheader = struct.unpack("!xB", data[:2])[0]
                s = fuheader >> 7
                e = (fuheader >> 6) & 1
                if s:
                    theader = (nalheader & 224) | (fuheader & 31)
                    fu_data = struct.pack("!B", theader) + data[2:]
                else:
                    fu_data += data[2:]

                if e:
                    nals.append(fu_data)

            else:
                continue

        print('nals: {}'.format(len(nals)))
        print('Writing in %s' % self.file)
        file = open(self.file, 'wb')
        print('stop')
        for nal in nals:
            nal = struct.pack("!I", 1) + nal
            file.write(nal)

        file.close()
        self.sock.close()


'''


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Internet # UDP
sock.bind((UDP_IP, UDP_PORT))

packets = []
nals = []
fudata = b''
print("Starting socket on", UDP_IP, ":", UDP_PORT, end='\n')

while True:
    try:
        data = sock.recvfrom(65565)
    except socket.timeout:
        print("Packets received:", len(packets), end='\n')
        break
    sock.settimeout(5.0)
    packet = data[0]
    packets.append(packet)
    # print("Packets received:",len(packets), end='\r')
    if len(packet) < 12:
        continue

# s.close()
# print("Socket closed")


for packet in packets:
    fb, sb, seqnum, timestamp = struct.unpack("!BBHI", packet[:8])  # RTP header

    pad = (fb >> 5) & 1
    ext = (fb >> 4) & 1
    cc = fb & 15
    mark = (sb >> 7) & 1

    if (pad > 3 or pad < 0):
        continue

    extsize = struct.unpack("!xxH", packet[12 + 4 * cc:16 + 4 * cc])[0] if ext else 0
    padsize = 0
    if pad == 1:
        padsize = struct.unpack("!B", packet[-1:])[0]
        # print(len(packet), padsize)
    data = packet[12 + 4 * (cc + ext + extsize):-padsize] if pad else packet[12 + 4 * (cc + ext + extsize):]

    if not len(data):
        continue

    nalheader = struct.unpack("!B", data[:1])[0]
    nalf = (nalheader >> 7) & 1
    nalnri = (nalheader >> 5) & 3
    naltype = nalheader & 31
    if 0 < naltype < 24:  # single unit
        nals.append(data)
    elif naltype == 24:  # stap-a
        naldata = data[1:]
        while len(naldata):
            nalsize = struct.unpack("!H", naldata[:2])[0]
            naldata = naldata[2:]
            tdata = naldata[:nalsize]
            nals.append(tdata)
            naldata = naldata[nalsize:]
    elif naltype == 28:  # fu-a
        fuheader = struct.unpack("!xB", data[:2])[0]
        s = fuheader >> 7
        e = (fuheader >> 6) & 1
        if s:
            theader = (nalheader & 224) | (fuheader & 31)
            # print ('theader: ', theader, end='\n\n')
            fudata = struct.pack("!B", theader) + data[2:]
            # print ('fudata0 ', fudata, end='\n\n')
        else:
            fudata += data[2:]
            # print ('fudata1 ', fudata, end='\n\n')

        if e:
            # print ('fudata: ', fudata, end='\n\n')
            nals.append(fudata)
            # print ('nal: ', nals[len(nals)-1], end='\n\n')
            # print('fudata: ', fudata)

    else:
        print('lol')
        continue

print('nals: ' + str(len(nals)), 'singles: ' + str(sum1), '; fus: ' + str(sum2))
file2 = open('rawdata.h264', 'wb')
rawnals = b''
sum1 = 0
print('stop')
for nal in nals:
    nal = struct.pack("!I", 1) + nal
    file2.write(nal)
    sum1 += len(nal)

bi = struct.pack('!B', 100)
stre = bi + struct.pack('!B', 0)
bi2 = struct.unpack('!B', stre[0:1])[0]
print(bi2)

file2.close()
# ffmpeg -f h264 -i rawdata.h264 -vcodec copy output.mp4
'''