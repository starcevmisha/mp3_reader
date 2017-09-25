import argparse
import ID3Tags
import player
parser = argparse.ArgumentParser()
parser.add_argument('name', type=str, help='file name')
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

else:
    print(tags.tags(picname, txtname, is_hex))

