import os, joblib, numpy as np
from .preprocessing import preprocess_image
from .segmentation import segment_green_region
from .features import extract_features

MODEL_PATH="models/best_model.pkl"
FEATURE_PATH="models/feature_names.pkl"

CLASS_INFO={
0:("Least wilting","Lowest observed wilting severity in the annotated scale."),
1:("Slight wilting","Low wilting severity."),
2:("Moderate wilting","Intermediate wilting severity."),
3:("High wilting","High observed wilting severity."),
4:("Very high wilting","Very high observed wilting severity."),
5:("Most wilting","Highest observed wilting severity in the current six-class data.")
}

def predict_image(image):
    if not os.path.exists(MODEL_PATH): raise FileNotFoundError(MODEL_PATH)
    if not os.path.exists(FEATURE_PATH): raise FileNotFoundError(FEATURE_PATH)
    model=joblib.load(MODEL_PATH); names=joblib.load(FEATURE_PATH)
    processed=preprocess_image(image)
    mask,seg=segment_green_region(processed)
    feats=extract_features(processed,mask)
    x=np.array([[feats.get(n,0.0) for n in names]],dtype=float)
    pred=int(model.predict(x)[0])
    if hasattr(model,"predict_proba"):
        p=model.predict_proba(x)[0]
        classes=getattr(model,"classes_",range(len(p)))
        probs={int(c):float(v) for c,v in zip(classes,p)}
        conf=max(probs.values())
    else: probs={pred:1.0}; conf=1.0
    label,desc=CLASS_INFO.get(pred,(f"Class {pred}","Class label from trained model."))
    return {"class":pred,"label":label,"description":desc,"confidence":float(conf),
            "probabilities":probs,"features":feats,"processed":processed,"mask":mask,"segmented":seg}
