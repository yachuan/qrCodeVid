import cv2
import os
#from pyzbar.pyzbar import decode
import cv2.aruco as aruco
import time
from video_spliter import split_video

class VidProcessor():

    def __init__(self, vid_path, save_path, args):

        self.path = vid_path
        self.save_to = save_path
        if not os.path.isdir(self.save_to):
            os.makedirs(self.save_to)
        self.qrcodes = {}
        self.splits = []
        self.stop = False
        self.OFFSET = 20
        self.args = args

    def read_mp4vidQR(self):

        vidcap = cv2.VideoCapture(self.path)
        success,image = vidcap.read()
        count = 1 # start with frame num 1
        while success:
            detected, qrcodes = self.detect_QRcode(image)
            cv2.putText(image, str(count), (60,60), cv2.FONT_HERSHEY_SIMPLEX,
                                1,(0, 0, 255), 2)
            if detected:
                save = os.path.join(self.save_to, "frame%d.jpg" % count)
                #cv2.imwrite(save, image)     # save frame as JPEG file   
                for i in qrcodes:
                    self.update_dict(i, count)
                    barcode = i[0]
                    (x, y, w, h) = barcode.rect
                    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
                    text = "{} ({})".format(i[1], i[2])
                    cv2.putText(image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                                1, (0, 0, 255), 2)
                    
                    if count % 30 == 0:
                        print(count, text)
            cv2.imshow('fm', image)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            success,image = vidcap.read()
            #print('Read a new frame: ', success)
            count += 1
        print('Total frame num:', count)
        print(self.qrcodes)
        
        vidcap.release()
        cv2.destroyAllWindows()
    
    def detect_QRcode(self, img, code=None):
        res = []
        # load the input image
        image = img
        # find the barcodes in the image and decode each of the barcodes
        # barcodes = decode(image)
        if len(barcodes) == 0:
            return False, None
        # loop over the detected barcodes
        # WARNING: here we should only assume one barcode
        for barcode in barcodes:
            # extract the bounding box location of the barcode and draw the
            # bounding box surrounding the barcode on the image
            # (x, y, w, h) = barcode.rect
            # cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
            # the barcode data is a bytes object so if we want to draw it on
            # our output image we need to convert it to a string first
            barcodeData = barcode.data.decode("utf-8")
            barcodeType = barcode.type
            # draw the barcode data and barcode type on the image
            text = "{} ({})".format(barcodeData, barcodeType)
            # cv2.putText(image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
            #     0.5, (0, 0, 255), 2)
            # print the barcode type and data to the terminal
            #print("[INFO] Found {} barcode: {}".format(barcodeType, barcodeData))
            if code is None or code == barcodeData:
                res.append((barcode, barcodeData, barcodeType))
        # # show the output image
        # cv2.imshow("Image", image)
        # cv2.waitKey(0)
        return True, res
    

    def read_mp4vidAR(self):

        vidcap = cv2.VideoCapture(self.path)
        success,image = vidcap.read()
        count = 1 # start with frame num 1
        while success:
            if self.args['mirror']:
                image = cv2.flip(image, 0)
            cv2.putText(image, str(count), (60,60), cv2.FONT_HERSHEY_SIMPLEX,
                                1,(0, 0, 255), 2)
            
            if len(self.splits) > 0:
                pair = self.splits.pop(0)
                start_pair = pair[0]
                end_pair = pair[1]
                start_fm = (start_pair[1] + self.OFFSET)/30
                end_fm = (end_pair[0] - self.OFFSET)/30
                dest = os.path.join(self.save_to, self.path.split('/')[-1].split('.')[0] + str(round(start_fm,2)) + '_' + str(round(end_fm,2)))
                print(start_fm, end_fm)
                if start_fm < end_fm:
                    print('splitting')
                    split_video(start_fm, end_fm, self.path, dest)
                else:
                    print('not valid start and stop, gesture too short')

            detected, image, datatuple = self.detectARcode(image)
            if detected:
                save = os.path.join(self.save_to, "frame%d.jpg" % count)
                #cv2.imwrite(save, image)     # save frame as JPEG file  
                corners, ids, rejectedImgPoints = datatuple

                idlist = ids.tolist()
                for i in idlist:
                    detection = self.update_AR(i, count)
                    if count % 30 == 0:
                        print(count, 'detected' + detection)
            cv2.imshow('fm', image)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            success,image = vidcap.read()
            count += 1
            time.sleep(0.01)
        print('Total frame num:', count)
        print(self.qrcodes)
        if 'START' in self.qrcodes and 'STOP' in self.qrcodes:
            pair = (self.qrcodes['START'], self.qrcodes['STOP'])
            self.splits.append(pair)
        if len(self.splits) > 0:
                pair = self.splits.pop(0)
                start_pair = pair[0]
                end_pair = pair[1]
                start_fm = (start_pair[1] + self.OFFSET)/30
                end_fm = (end_pair[0] - self.OFFSET)/30
                dest = os.path.join(self.save_to, self.path.split('/')[-1].split('.')[0] + "{0:.2f}".format(start_fm) + '_' + str(round(end_fm,2)))
                print(start_fm, end_fm)
                if start_fm < end_fm:
                    print('splitting')
                    split_video(start_fm, end_fm, self.path, dest)
                else:
                    print('not valid start and stop, gesture too short')
        print(self.splits)
        
        vidcap.release()
        cv2.destroyAllWindows()

    def detectARcode(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_1000)
        arucoParameters = aruco.DetectorParameters_create()
        corners, ids, rejectedImgPoints = aruco.detectMarkers(
            gray, aruco_dict, parameters=arucoParameters)

        if ids is None or len(ids) == 0:
            return False, image, (corners, ids, rejectedImgPoints)
        # print(corners, 'raaaaaaaaaaaaaaaaaa')
        # print(ids, 'zxxxxxxxxxxxxxxxxxxx')
        image = aruco.drawDetectedMarkers(image, corners, ids)
        return True, image, (corners, ids, rejectedImgPoints)

    def update_dict(self, qrcode_tuple, frame_num):
        qrcode = qrcode_tuple[0]
        data = qrcode_tuple[1]
        qrtype = qrcode_tuple[2]

        if data in self.qrcodes:
            if frame_num > self.qrcodes[data][1]:
                self.qrcodes[data] = (self.qrcodes[data][0], frame_num)
        else:
            self.qrcodes[data] = (frame_num, frame_num)

    def update_AR(self, ids, frame_num):
        #qrcode = qrcode_tuple[0]
        data = ids[0]
        #qrtype = qrcode_tuple[2]

        if data == 0:
            data = 'START'
            if self.stop:
                pair = (self.qrcodes['START'], self.qrcodes['STOP'])
                self.splits.append(pair)
                self.qrcodes = dict()
                self.stop = False
        elif data == 99:
            data = 'STOP'
            self.stop = True

        if data in self.qrcodes:
            if frame_num > self.qrcodes[data][1]:
                self.qrcodes[data] = (self.qrcodes[data][0], frame_num)
                
        else:
            self.qrcodes[data] = (frame_num, frame_num)

        return data