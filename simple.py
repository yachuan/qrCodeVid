import cv2
import time, argparse





if __name__ == '__main__':
    # construct the argument parser and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--video", required=True, default='data/qrvidex1210.mp4',
        help="path to input video")
    args = vars(ap.parse_args())

    # load the input image
    path = args["video"]

    vidcap = cv2.VideoCapture(path)
    success,image = vidcap.read()
    count = 1 # start with frame num 1
    while success:
        # cv2.putText(image, str(count), (60,60), cv2.FONT_HERSHEY_SIMPLEX,
        #                     1,(0, 0, 255), 2)
        #image = cv2.flip(image, 0)
        cv2.imshow('fm', image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        success,image = vidcap.read()
        count += 1
        time.sleep(0.01)

    vidcap.release()
    cv2.destroyAllWindows()