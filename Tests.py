import ID3Tags
import unittest
from unittest import mock
from mock import mock_open


class HeaderTest:

    def __init__(self):
        self.size = -10


class Reader_test:

    def __init__(self):
        self.file = open('111123.txt', 'rb')
        self.remaining_byte = 0
        self.header = HeaderTest()


class TestCat(unittest.TestCase):

    def test__header_read(self):

        value = b'ID3\x03\x00\x00\x00\n$R'
        with mock.patch('__main__.open', mock_open(read_data=value)) as m:
            reader = Reader_test()
            mp3header = ID3Tags.Header()
            mp3header.read(open("123.txt", 'rb'))
            self.assertDictEqual(
                mp3header.__dict__,
                {
                    'major_version': 3,
                    'revision': 0,
                    'flags': 0,
                    'size': 168530,
                    'return_size': 168530,
                    'Unsynchronized': False,
                    'Compressed': False,
                    'Experimental': False,
                    'Footer': False,
                    'read_ext_header': None
                })

    def test_tag_process_(self):
        frame = ID3Tags.TagFrame()
        frame.__dict__ = {
            'id': 'TPE2',
            'size': 17,
            'flags': 0,
            'raw': b'\x01\xff\xfeN\x00i\x00r\x00v\x00a\x00n\x00a\x00',
            'value': '',
            'TagAlterPreserve': False,
            'FileAlterPreserve': False,
            'ReadOnly': False,
            'Compressed': False,
            'Encrypted': False,
            'InGroup': False,
            'flag': 0}
        frame.process()
        self.assertEqual(frame.value, "Nirvana")

    def test_invalid_characters_(self):
        self.assertFalse(ID3Tags.Reader.valid_id("PRI12##@3VET"))

    def test_get_synvchsafe_bytes(self):
        self.assertEqual(ID3Tags.Reader.get_synchsafe_int("\x00\n$R"), 168530)

    def test_tags_output(self):
        with mock.patch("builtins.open", mock_open(read_data=b'ID3\x03\x00\x00\x00\n$R')):
            test_reader = ID3Tags.Reader("lolki.txt", True)
            test_reader.mp3frame = ID3Tags.Mp3Frame()
            test_reader.mp3frame.__dict__ = {
                'MPEG_version': 3,
                'layer_index': 1,
                'protection_bit': 1,
                'bitrate_index': 11,
                'sampling_rate_index': 0,
                'padding_bit': 1,
                'private': 0,
                'channel_mode': 1,
                'mode_ext': 2,
                'copyright': 0,
                'original': 1,
                'emphasis': 0,
                'time': 200.09854166666668,
                'frame_count': 0}
            test_reader.header = ID3Tags.Header()
            test_reader.header.__dict__ = {
                'major_version': 3,
                'revision': 0,
                'flags': 0,
                'size': 4086,
                'Unsynchronized': False,
                'Compressed': False,
                'Experimental': False,
                'Footer': False,
                'read_ext_header': None}
            self.assertEqual(
                test_reader.tags(
                    None, None), ("\n"
                                  "-----Header info----\n"
                                  "ID3 tag version: 2.3.0\n"
                                  "ID3 tag size: 4086 byte\n"
                                  "Comressed: No\n"
                                  "\n"
                                  "-----MP3frame info----\n"
                                  "MPEG Version: MPEG-1 Layer III\n"
                                  "Bitrate: 192 kb/s\n"
                                  "Sampling rate 44100 kh/s\n"
                                  "Channel mode: Join Stereo\n"
                                  "Time: 3.20 mm.ss\n"
                                  "Frame count: 0\n"
                                  "\n"
                                  "------Tags info-----\n"))


if __name__ == '__main__':
    unittest.main()
