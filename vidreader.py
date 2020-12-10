import cv2
import os
from pyzbar.pyzbar import decode

class VidProcessor():

    def __init__(self, vid_path, save_path):

        self.path = vid_path
        self.save_to = save_path
        if not os.path.isdir(self.save_to):
            os.makedirs(self.save_to)
        self.qrcodes = {}

    def read_mp4vid(self):

        vidcap = cv2.VideoCapture(self.path)
        success,image = vidcap.read()
        count = 1 # start with frame num 1
        while success:
            detected, qrcodes = self.detect_QRcode(image)
            if detected:
                save = os.path.join(self.save_to, "frame%d.jpg" % count)
                cv2.imwrite(save, image)     # save frame as JPEG file   
                for i in qrcodes:
                    self.update_dict(i, count)
                    if count % 5 == 0:
                        print(count, "{} ({})".format(i[1], i[2]))
                        

            success,image = vidcap.read()
            #print('Read a new frame: ', success)
            count += 1
        print('Total frame num:', count)
        print(self.qrcodes)
    
    def detect_QRcode(self, img, code=None):
        res = []
        # load the input image
        image = img
        # find the barcodes in the image and decode each of the barcodes
        barcodes = decode(image)
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
    
    def update_dict(self, qrcode_tuple, frame_num):
        qrcode = qrcode_tuple[0]
        data = qrcode_tuple[1]
        qrtype = qrcode_tuple[2]

        if data in self.qrcodes:
            if frame_num > self.qrcodes[data][1]:
                self.qrcodes[data] = (self.qrcodes[data][0], frame_num)
        else:
            self.qrcodes[data] = (frame_num, frame_num)