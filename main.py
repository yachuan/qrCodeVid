import os

from vidreader import VidProcessor

if __name__ == '__main__':

    path = 'data/qrvidex1210.mp4'
    save = 'pix'
    r = VidProcessor(path, save)
    r.read_mp4vid()

