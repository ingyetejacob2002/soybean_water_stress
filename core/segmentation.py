import cv2, numpy as np

def segment_green_region(image_bgr):
    hsv=cv2.cvtColor(image_bgr,cv2.COLOR_BGR2HSV)
    mask=cv2.inRange(hsv,np.array([20,30,20],np.uint8),np.array([100,255,255],np.uint8))
    k=np.ones((5,5),np.uint8)
    mask=cv2.morphologyEx(mask,cv2.MORPH_OPEN,k)
    mask=cv2.morphologyEx(mask,cv2.MORPH_CLOSE,k)
    segmented=cv2.bitwise_and(image_bgr,image_bgr,mask=mask)
    return mask,segmented
