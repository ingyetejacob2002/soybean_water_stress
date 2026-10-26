# SoyStress AI

## Run
Place your existing trained artifacts in `models/`:
- `best_model.pkl`
- `feature_names.pkl`

Then:

```bash
pip install -r requirements.txt
streamlit run app.py
```

The app provides image upload, prediction, probability profile, feature display, history and system information.

**Important:** the feature extraction in `core/features.py` must match the exact feature extraction used when the saved model was trained.
