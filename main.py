import os
import argparse
from vidreader import VidProcessor

if __name__ == '__main__':
    

    # construct the argument parser and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--video", required=True, default='data/qrvidex1210.mp4',
        help="path to input video")
    args = vars(ap.parse_args())

    # load the input image
    path = args["video"]
    #path = 'data/qrvidex1210.mp4'
    #path = 'data/qrvidex1210dark.mp4'

    save = 'pix'
    r = VidProcessor(path, save)
    #r.read_mp4vidQR()
    r.read_mp4vidAR()

