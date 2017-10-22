import pygame as pg
import time


class _Getch:
    """Gets a single character from standard input.  Does not echo to the
screen."""

    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()

    def __call__(self): return self.impl()


class _GetchUnix:
    def __call__(self):
        import tty
        import sys
        import termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class _GetchWindows:
    def __call__(self):
        import msvcrt
        return msvcrt.getch()


def play_music(music_file, volume=0.8):
    """
    stream music with mixer.music module in a blocking manner
    this will stream the sound from disk while playing
    """
    # set up the mixer
    freq = 44100     # audio CD quality
    bitsize = -16    # unsigned 16 bit
    channels = 2     # 1 is mono, 2 is stereo
    buffer = 20000    # number of samples (experiment to get best sound)
    pg.mixer.init(freq, bitsize, channels, buffer)
    # volume value 0.0 to 1.0
    pg.mixer.music.set_volume(volume)
    # clock = pg.time.Clock()
    try:
        pg.mixer.music.load(music_file)
        print("Music file {} loaded!".format(music_file))
    except pg.error:
        print("File {} not found! ({})".format(music_file, pg.get_error()))
        return

    print("Press q to quit\n"
          "Press Space to play/pause\n"
          "Press -> to forward")
    pg.mixer.music.play()
    start_time = time.time() + 2
    flag = 1
    getch = _Getch()

    while True:
        pressed_key = getch()
        if pressed_key == b'q'or pressed_key == 'q':
            pg.mixer.music.play()
            exit()
        else:
            if pressed_key == b' ' or pressed_key == ' ':
                if flag:
                    pg.mixer.music.pause()
                    flag = 0
                else:
                    pg.mixer.music.unpause()
                    flag = 1
            if pressed_key == b't':
                print(time.time() - start_time)

            if pressed_key == b'\xe0':
                second_key = getch()
                if second_key == b'M':
                    start_time -= 10
                    pg.mixer.music.play(start=time.time() - start_time)
                if second_key == b'K':
                    start_time += 1
                    pg.mixer.music.play(start=time.time() - start_time)
            if pressed_key == '\x1b':
                second_key = getch() + getch()
                if second_key == '[C':
                    start_time += 1
                    pg.mixer.music.play(start=time.time() - start_time)
                if second_key == '[D':
                    start_time -= 10
                    pg.mixer.music.play(start=time.time() - start_time)


if __name__ == "__main__":
    music_file = "song.mp3"
    # optional volume 0 to 1.0
    volume = 0.8
    play_music(music_file, volume)
