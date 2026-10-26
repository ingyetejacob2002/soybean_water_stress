import cv2, numpy as np
from skimage.feature import graycomatrix, graycoprops


def extract_features(image_bgr, mask):
    """Return the 16 features whose names/scales match models/feature_names.pkl.

    Scales inferred from the trained ExtraTrees split thresholds:
    RGB 0-255, OpenCV HSV (H 0-180, S 0-255), OpenCV Lab (a/b centred on 128),
    normalised ExG (~0.06-0.35), GLCM on 8-bit gray (contrast up to ~27).
    """
    rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)
    lab = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2LAB)
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)

    valid = mask > 0
    if not np.any(valid):
        valid = np.ones(mask.shape, bool)

    rv, hv, lv = rgb[valid].astype(float), hsv[valid].astype(float), lab[valid].astype(float)
    r, g, b = rv[:, 0], rv[:, 1], rv[:, 2]

    f = {
        "mean_red": r.mean(), "mean_green": g.mean(), "mean_blue": b.mean(),
        "std_red": r.std(), "std_green": g.std(), "std_blue": b.std(),
        "mean_hue": hv[:, 0].mean(),
        "mean_saturation": hv[:, 1].mean(),
        "mean_lab_a": lv[:, 1].mean(),
        "mean_lab_b": lv[:, 2].mean(),
    }

    total = r + g + b + 1e-8
    f["exg"] = float(np.mean((2 * g - r - b) / total))

    g8 = gray.copy()
    g8[~valid] = 0
    glcm = graycomatrix(g8, [1], [0, np.pi / 4, np.pi / 2, 3 * np.pi / 4],
                        levels=256, symmetric=True, normed=True)
    for p in ["contrast", "dissimilarity", "homogeneity", "energy", "correlation"]:
        f[f"glcm_{p}"] = graycoprops(glcm, p).mean()

    return {k: float(v) for k, v in f.items()}
