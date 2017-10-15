import struct
import zlib
import hexdump
import os
# http://id3lib.sourceforge.net/id3/id3v2-00.txt
# http://id3.org/d3v2.3.0
# http://id3.org/id3v2.4.0-structure
encodings = ['iso8859-1', 'utf-16', 'utf-16be', 'utf-8']
bitrate = {
    1: 32,
    2: 40,
    3: 48,
    4: 56,
    5: 64,
    6: 80,
    7: 96,
    8: 112,
    9: 128,
    10: 160,
    11: 192,
    12: 224,
    13: 256,
    14: 320,
    15: 192
}
sampling_rate = {
    0: 44100,
    1: 48000,
    2: 32000,
    3: "Error. NotExist"
}
channel_mode = {
    0: "Stereo",
    1: "Join Stereo",
    2: "Dual Channel",
    3: "Mono"
}


class Id3Error(Exception):
    pass


class Header:
    """ Represent the ID3 header in a tag.
    """

    def __init__(self):
        self.major_version = 0
        self.revision = 0
        self.flags = 0
        self.size = 0
        self.size = 0
        self.Unsynchronized = False
        self.Compressed = False
        self.Experimental = False
        self.Footer = False
    #
    # def __str__(self):
    #     return str(self.__dict__)

    def read(self, file):
        raw_header = file.read(10)
        if len(raw_header) < 10:
            raise Id3Error("Incorrect file")

        raw_header = struct.unpack('!3sBBBBBBB', raw_header)
        if raw_header[0] != b"ID3":
            self.return_size = 0
            self.is_empty_header = True
            return

        self.is_empty_header = False
        self.major_version = raw_header[1]
        self.revision = raw_header[2]
        self.flags = raw_header[3]
        self.size = Reader.get_synchsafe_int(raw_header[4:8])

        self.return_size = self.size

        self.read_ext_header = None

        self.process_flag()
        if self.read_ext_header:
            self.read_ext_header(file)

    def pass_pass(self):
        pass

    def process_flag(self):
        self.Unsynchronized = self.flags & 128 != 0
        if self.major_version == 2:
            self.Compressed = self.flags & 64 != 0
        if self.major_version >= 3:
            if self.flags & 64:
                if self.major_version == 3:
                    self.read_ext_header = self.read_ext_header_ver3
                if self.major_version == 4:
                    self.read_ext_header = self.read_ext_header_ver4
            self.Experimental = self.flags & 32 != 0
        if self.major_version == 4:
            self.Footer = self.flags & 16 != 0

    def read_ext_header_ver3(self, file):
        size = Reader.get_int(file.read(4))
        self.return_size -= 4
        data = file.read(size)
        self.return_size -= size

    def read_ext_header_ver4(self, file):
        size = Reader.get_synchsafe_int(file.read(4))
        self.return_size -= 4
        data = file.read(size - 4)
        self.return_size -= (size - 4)

    def __str__(self):
        return "ID3 tag version: 2.{}.{}\n"\
            .format(self.major_version, self.revision) +\
               "ID3 tag size: {} byte\n".format(self.size) + \
               'Comressed: {}\n'\
            .format("Yes" if self.Compressed else "No")


class TagFrame:
    """ Represent an ID3 frame in a tag.
    """

    def __init__(self):
        self.id = ''
        self.size = 0
        self.flags = 0
        self.raw = ''
        self.value = ''
        self.TagAlterPreserve = False
        self.FileAlterPreserve = False
        self.ReadOnly = False
        self.Compressed = False
        self.Encrypted = False
        self.InGroup = False

    def __str__(self):
        return str(self.__dict__)

    def process(self):
        if self.Compressed:
            self.raw = zlib.decompress(self.raw)

        # Скопировал, не моё
        if self.id[0] == 'T':
            # Text fields start with T
            encoding = self.raw[0]
            if 0 <= encoding < len(encodings):
                # if _c: _coverage('encoding%d' % encoding)
                value = self.raw[1:].decode(encodings[encoding])
            else:
                # if _c: _coverage('bad encoding')
                value = self.raw[1:]
            # Don't let trailing zero header_header_ fool you.
            if value:
                value = value.strip('\0')
            # The value can actually be a list.
            if '\0' in value:
                value = value.split('\0')
                # if _c: _coverage('textlist')
            self.value = value
        elif self.id[0] == 'W':
            # URL fields start with W
            self.value = self.raw.strip('\0')
            if self.id == 'WXXX':
                self.value = self.value.split('\0')
        elif self.id == 'CDM':
            # ID3v2.2.1 Compressed Data Metaframe
            if self.raw[0] == 'z':
                self.raw = zlib.decompress(self.raw[5:])
            else:
                # if _c: _coverage('badcdm!')
                raise Id3Error('Unknown CDM compression: %02x' % self.raw[
                    0])
        #
        if self.id == "APIC":
            enc = self.raw[0]
            location = self.raw.find(b'\x00', 1)
            self.MIME_type = self.raw[1:location]
            self.pict_type = self.raw[location + 1]
            location2 = self.raw.find(b'\x00', location + 2)
            self.description = self.raw[location + 2: location2]
            self.value = self.raw[location2 + 1:]

        if self.id == "USLT":
            enc = self.raw[0]
            lang = self.raw[1:4]
            location = self.raw.find(b'\x00', 5)
            content_descr = self.raw[5:location]
            if 0 <= enc < len(encodings):
                # if _c: _coverage('encoding%d' % encoding)
                value = self.raw[location + 4:].decode(encodings[enc])
            else:
                # if _c: _coverage('bad encoding')
                value = self.raw[location + 1:]
            self.value = value


class Mp3Frame:

    def __init__(self):
        self.MPEG_version = 0
        self.layer_index = 0
        self.protection_bit = 0
        self.bitrate_index = 0
        self.sampling_rate_index = 0
        self.padding_bit = 0
        self.private = 0
        self.channel_mode = 0
        self.mode_ext = 0
        self.copyright = 0
        self.original = 0
        self.emphasis = 0
        self.time = 0
        self.frame_count = 0

    def read(self, reader):
        reader.file.seek(reader.header.size + 10)
        raw_header = reader.file.read(4)

        while not (raw_header[0] & 0xFF ==
                   0xFF and raw_header[1] >> 5 & 0x7 == 0x7):
            reader.file.seek(-1, 1)
            raw_header = reader.file.read(4)

        self.MPEG_version = (raw_header[1] >> 3) & 0b11
        self.layer_index = (raw_header[1] >> 1) & 0b11
        self.protection_bit = raw_header[1] & 0b1
        self.bitrate_index = raw_header[2] >> 4
        self.sampling_rate_index = (raw_header[2] >> 2) & 0b11
        self.padding_bit = (raw_header[2] >> 1) & 0b1
        self.private = raw_header[2] & 0b1
        self.channel_mode = (raw_header[3] >> 6) & 0b11
        self.mode_ext = (raw_header[3] >> 4) & 0b11
        self.copyright = (raw_header[3] >> 3) & 0b1
        self.original = (raw_header[3] >> 2) & 0b1
        self.emphasis = raw_header[3] & 0b11
        self.time = 0

        offset = 32 if self.channel_mode != 3 else 17

        reader.file.seek(offset, 1)
        compress_type = reader.file.read(4)
        if compress_type == b"Info" or compress_type == b"Xing":
            reader.file.seek(4, 1)
            self.frame_count = int.from_bytes(
                reader.file.read(4), byteorder='big')
            self.time = 1152 * self.frame_count / \
                sampling_rate[
                    self.sampling_rate_index]
        elif compress_type == b'VBRI':
            reader.file.seek(10, 1)
            self.frame_count = int.from_bytes(
                reader.file.read(4), byteorder='big')
            self.time = 1152 * self.frame_count / \
                sampling_rate[
                    self.sampling_rate_index]

        else:
            self.time = \
                (os.path.getsize(reader.file_name) - reader.header.size) / \
                (bitrate[self.bitrate_index] * 1000) * 8

    # def __str__(self):
    #     return str(self.__dict__)

    def __str__(self):
        # self.MPEG_version)
        return "MPEG Version: MPEG-1 Layer III\n" +\
               "Bitrate: {} kb/s\n".format(bitrate[self.bitrate_index]) +\
               "Sampling rate {} kh/s\n"\
            .format(sampling_rate[self.sampling_rate_index]) +\
               "Channel mode: {}\n"\
            .format(channel_mode[self.channel_mode]) +\
               "Time: %d.%02d mm.ss\n" \
               % (int(self.time // 60), int(self.time % 60)) +\
               "Frame count: {}\n".format(self.frame_count)


class Reader:

    def __init__(self, file, is_test_case=False):
        self.Frames = {}

        self.file_name = file
        self.header = None
        self.frames = {}
        self.allFrames = []
        try:
            with (open(file, 'rb')) as self.file:
                if not is_test_case:
                    self.read_tags()
        except FileNotFoundError as e:
            print(e)
            exit()

    def read_tags(self):

        self.header = Header()
        self.header.read(self.file)

        self.remaining_byte = self.header.return_size

        read_frame_versions = {2: self.read_frame_rev2,
                               3: self.read_frame_rev3,
                               4: self.read_frame_rev4}

        if self.header.major_version in read_frame_versions:

            self.read_frame = read_frame_versions[self.header.major_version]

            while self.remaining_byte > 0:
                frame = self.read_frame()
                if frame:
                    frame.process()
                    self.Frames[frame.id] = frame
                else:
                    break
        else:
            pass

        self.mp3frame = Mp3Frame()
        self.mp3frame.read(self)

    validIdChars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

    @staticmethod
    def valid_id(id_string):
        for c in id_string:
            if c not in Reader.validIdChars:
                return False
        return True

    def read_bytes(self, num):
        # TODO обработать шоб хорошо если меньше, если рассинхронизированы
        self.remaining_byte -= num
        return self.file.read(num)

    def read_frame_rev2(self):
        if self.remaining_byte < 6:
            return None
        version_id = self.read_bytes(3).decode()
        if len(version_id) < 3 or not Reader.valid_id(version_id):
            return None
        header_header_bytes = struct.unpack('!BBB', self.read_bytes(3))
        frame = TagFrame()
        frame.id = version_id
        frame.size = Reader.get_int(header_header_bytes)
        frame.raw = self.read_bytes(frame.size)
        return frame

    def read_frame_rev3(self):
        if self.remaining_byte < 10:
            return None
        version_id = self.read_bytes(4).decode()
        if len(version_id) < 4 or not Reader.valid_id(version_id):
            return None
        header_bytes = struct.unpack('!BBBBh', self.read_bytes(6))
        frame = TagFrame()
        frame.id = version_id
        frame.size = Reader.get_int(header_bytes[:4])
        real_size = frame.size
        frame.flag = header_bytes[4]

        frame.TagAlterPreserve = frame.flag & 32768 != 0
        frame.FileAlterPreserve = frame.flag & 16384 != 0
        frame.ReadOnly = frame.flag & 8192 != 0

        frame.Compressed = frame.flag & 128 != 0
        frame.Encrypted = frame.flag & 64 != 0
        frame.InGroup = frame.flag & 32 != 0

        if frame.Compressed:
            frame.decompressed_size = Reader.get_int(self.read_bytes(4))
            real_size -= 4
        if frame.Encrypted:
            frame.encryption_method = self.read_bytes(1)
            real_size -= 1
        if frame.InGroup:
            frame.group = self.read_bytes(1)
            real_size -= 1

        frame.raw = self.read_bytes(real_size)
        return frame

    def read_frame_rev4(self):
        if self.remaining_byte < 10:
            return None
        version_id = self.read_bytes(4).decode()
        if len(version_id) < 4 or not Reader.valid_id(version_id):
            return None
        header_bytes = struct.unpack('!BBBBh', self.read_bytes(6))
        frame = TagFrame()
        frame.id = version_id
        frame.size = Reader.get_synchsafe_int(header_bytes[:4])
        real_size = frame.size
        frame.flag = header_bytes[4]

        frame.TagAlterPreserve = frame.flag & 16384 != 0
        frame.FileAlterPreserve = frame.flag & 8192 != 0
        frame.ReadOnly = frame.flag & 4096 != 0

        frame.InGroup = frame.flag & 64 != 0
        if frame.InGroup:
            frame.group = self.read_bytes(1)
            real_size -= 1

        frame.Compressed = frame.flag & 8 != 0

        frame.Encrypted = frame.flag & 4 != 0
        if frame.Encrypted:
            frame.encryption_method = self.read_bytes(1)
            real_size -= 1

        frame.Unsynchronized = frame.flag & 2 != 0

        if frame.flags & 1:
            frame.data_len = Reader.get_synchsafe_int(self.read_bytes(4))
            real_size -= 4

        frame.raw = self.read_bytes(real_size)
        return frame

    @staticmethod
    def get_int(bytes_string):
        i = 0
        if isinstance(bytes_string, str):
            bytes_string = [ord(c) for c in bytes_string]
        for b in bytes_string:
            i = i * 256 + b
        return i

    @staticmethod
    def get_synchsafe_int(bytes_string):
        i = 0
        if isinstance(bytes_string, str):
            bytes_string = [ord(c) for c in bytes_string]
        for b in bytes_string:
            i = i * 128 + b
        return i

    def tags(self, picname, txtname, is_hex=False):
        tag_str = []

        if not self.header.is_empty_header:
            tag_str.append("\n-----Header info----\n")

            tag_str.append(str(self.header))

        tag_str.append("\n-----MP3frame info----\n")

        tag_str.append(str(self.mp3frame))

        if len(self.Frames) > 0:
            tag_str.append("\n------Tags info-----\n")
            for i in self.Frames:
                if isinstance(self.Frames[i].value, bytes) and is_hex:
                    tag_str.append("{}: \n{}\n".format(
                        self.Frames[i].id,
                        hexdump.hexdump(self.Frames[i].value, 'return')))
                else:
                    if (self.Frames[i].id == "APIC"):
                        tag_str.append("{}: {}\n".format(
                            self.Frames[i].id,
                            "Picture. Use --pic to store it or --hex to view"))
                    elif(self.Frames[i].id == "USLT"):
                        tag_str.append("{}: {}\n".format(
                            self.Frames[i].id,
                            "Text. Use --txt to store it"))
                    else:
                        tag_str.append("{}: {}\n".format(
                            self.Frames[i].id,
                            self.Frames[i].
                            value[:min(len(self.Frames[i].value), 30)]))

            basename = self.file_name.split('.')[0]

            if "APIC" in self.Frames and picname:
                with open(picname, 'wb') as h:
                    h.write(self.Frames['APIC'].value)
            if "USLT" in self.Frames and txtname:
                with open(txtname, "wb") as h:
                    text = self.Frames['USLT'].value
                    h.write(text.encode('utf-8'))

        return ''.join(tag_str)

    def __iter__(self):
        for i in self.Frames:
            yield "{}: {}\n".format(
                self.Frames[i].id,
                self.Frames[i].value[:min(len(self.Frames[i].value), 30)])

if __name__ == "__main__":
    file_name = 'song.mp3'
    a = Reader(file_name)
    a.tags()
