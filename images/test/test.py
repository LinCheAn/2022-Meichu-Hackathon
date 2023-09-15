import cv2
import os
import datetime
import sys 
cv2.namedWindow("preview")
vc = cv2.VideoCapture(0)
os.chdir(os.path.dirname(sys.argv[0]))


if vc.isOpened(): # try to get the first frame
    rval, frame = vc.read()
else:
    rval = False

while rval:
    cv2.imshow("preview", frame)
    rval, frame = vc.read()
    key = cv2.waitKey(20)
    # print(key)
    if key !=113: #press Q to take a picture
        #take picture
        # print("test")
        # filename = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        filename = "test"
        filetype = ".jpg"
        # print(filename)
        cv2.imwrite(filename+filetype, frame)
    if key == 27: # exit on ESC
        break

vc.release()
cv2.destroyWindow("preview") 