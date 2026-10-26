import cv2, numpy as np

def preprocess_image(image):
    if hasattr(image,"convert"):
        image=np.array(image.convert("RGB"))
        image=cv2.cvtColor(image,cv2.COLOR_RGB2BGR)
    image=cv2.resize(image,(512,512))
    image=cv2.fastNlMeansDenoisingColored(image,None,5,5,7,21)
    lab=cv2.cvtColor(image,cv2.COLOR_BGR2LAB)
    l,a,b=cv2.split(lab)
    l=cv2.createCLAHE(clipLimit=2.0,tileGridSize=(8,8)).apply(l)
    return cv2.cvtColor(cv2.merge([l,a,b]),cv2.COLOR_LAB2BGR)
