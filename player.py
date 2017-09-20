""" pg_playmp3f.py
play MP3 music files using Python module pygame
pygame is free from: http://www.pygame.org
(does not create a GUI frame in this case)
"""
import pygame as pg
import msvcrt
import time


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
          "Press Space to play/pause")
    pg.mixer.music.play()
    start_time = time.time() + 2
    flag = 1
    while True:
        pressed_key = msvcrt.getch()
        if pressed_key == b'q':
            pg.mixer.music.play()
            exit()
        else:
            if pressed_key == b' ':
                if flag:
                    pg.mixer.music.pause()
                    flag = 0
                else:
                    pg.mixer.music.unpause()
                    flag = 1
            if pressed_key == b't':
                print(time.time() - start_time)

            if pressed_key == b'\xe0':
                second_key = msvcrt.getch()
                if second_key == b'M':
                    start_time -= 1
                    pg.mixer.music.play(start=time.time() - start_time)
                if second_key == b'K':
                    start_time += 1
                    pg.mixer.music.play(start=time.time() - start_time)

    # # while pg.mixer.music.get_busy():
    # #     pass
    #     # check if playback has finished
    #     # clock.tick(30)

# pick a MP3 music file you have in the working folder
# otherwise give the full file path
# (try other sound file formats too)
if __name__=="__main__":
    music_file = "song.mp3"
    # optional volume 0 to 1.0
    volume = 0.8
    play_music(music_file, volume)
