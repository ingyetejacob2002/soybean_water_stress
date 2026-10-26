import cv2, numpy as np
from skimage.feature import graycomatrix, graycoprops

def extract_features(image_bgr,mask):
    f={}
    rgb=cv2.cvtColor(image_bgr,cv2.COLOR_BGR2RGB)
    hsv=cv2.cvtColor(image_bgr,cv2.COLOR_BGR2HSV)
    lab=cv2.cvtColor(image_bgr,cv2.COLOR_BGR2LAB)
    valid=mask>0
    if not np.any(valid): valid=np.ones(mask.shape,bool)
    rv,hv,lv=rgb[valid],hsv[valid],lab[valid]
    for i,n in enumerate(["r","g","b"]):
        f[f"rgb_{n}_mean"]=float(rv[:,i].mean()); f[f"rgb_{n}_std"]=float(rv[:,i].std())
    for i,n in enumerate(["h","s","v"]): f[f"hsv_{n}_mean"]=float(hv[:,i].mean())
    for i,n in enumerate(["l","a","b"]): f[f"lab_{n}_mean"]=float(lv[:,i].mean())
    r,g,b=rv[:,0].astype(float),rv[:,1].astype(float),rv[:,2].astype(float)
    exg=2*g-r-b
    f["exg_mean"]=float(exg.mean()); f["exg_std"]=float(exg.std())
    gray=cv2.cvtColor(image_bgr,cv2.COLOR_BGR2GRAY); gray[~valid]=0
    gray32=np.floor(gray.astype(np.float32)/256*32).astype(np.uint8); gray32[gray32>31]=31
    glcm=graycomatrix(gray32,[1],[0,np.pi/4,np.pi/2,3*np.pi/4],levels=32,symmetric=True,normed=True)
    for p in ["contrast","dissimilarity","homogeneity","energy","correlation","ASM"]:
        f[f"glcm_{p}_mean"]=float(graycoprops(glcm,p).mean())
    return f
