import argparse
import ID3Tags
import gui
import sys
import player
import hexdump
parser = argparse.ArgumentParser()
parser.add_argument('name', type=str, help='file name')
parser.add_argument('--gui', action='store_true', help='Graphic UI')
parser.add_argument('--pic', help='filename to store picture')
parser.add_argument('--txt', help='filename to store txt')
parser.add_argument('--hex', action='store_true',
                    help='hexdump of binary tags')

parser.add_argument('--player', help='Play sound', action="store_true")


args = parser.parse_args()

name = args.name

tags = ID3Tags.Reader(name)

picname = None if not args.pic else args.pic
txtname = None if not args.txt else args.txt
is_hex = args.hex

if args.player:
    player.play_music(name)


elif not args.gui:
    pass
    print(tags.tags(picname, txtname, is_hex))
else:
    text = "WithOut TEXT"
    if 'USLT' in tags.Frames:
        text = tags.Frames["USLT"].value
    if 'APIC' in tags.Frames:
        filename = args.pic
    ex = gui.Example(name, tags.tags(picname, txtname, is_hex), text)
    sys.exit(ex.app.exec_())
