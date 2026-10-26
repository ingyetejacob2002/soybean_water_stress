import base64
from io import BytesIO
from datetime import datetime

import pandas as pd
import streamlit as st
from PIL import Image

from core.prediction import predict_image, CLASS_INFO
from core.visuals import hero_uri, leaf_uri, RAMP

st.set_page_config(page_title="SoyStress AI", page_icon="🌱", layout="wide",
                   initial_sidebar_state="expanded")

PAGES = {"Dashboard": "🏠", "Analyze Image": "🔬", "Prediction History": "🕘",
         "About System": "🌱", "Help": "💡"}
for k, v in {"history": [], "last_result": None, "last_image": None, "nav": "Dashboard"}.items():
    st.session_state.setdefault(k, v)


def go(page):
    st.session_state.nav = page


def html(s):
    st.markdown("\n".join(l.strip() for l in s.strip().splitlines() if l.strip()),
                unsafe_allow_html=True)


def data_uri(img):
    buf = BytesIO()
    img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


# ------------------------------------------------------------------ CSS
html("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=Space+Grotesk:wght@500;700&display=swap');
html,body,[class*="css"]{font-family:'DM Sans',sans-serif}
h1,h2,h3,h4{font-family:'Space Grotesk',sans-serif!important}
.stApp{background:#f4f7f5}
.block-container{max-width:1240px;padding-top:1.6rem;padding-bottom:3rem}
#MainMenu,footer{visibility:hidden}
/* sidebar */
[data-testid="stSidebar"]{background:linear-gradient(180deg,#0f2a1b,#0a1f14)}
[data-testid="stSidebar"] *{color:#eef6f0!important}
[data-testid="stSidebar"] [role="radiogroup"]{gap:.3rem}
[data-testid="stSidebar"] [role="radiogroup"] label{padding:.65rem .9rem;border-radius:12px;width:100%;cursor:pointer;transition:.15s}
[data-testid="stSidebar"] [role="radiogroup"] label:hover{background:rgba(255,255,255,.08)}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked){background:rgba(111,190,133,.22);box-shadow:inset 3px 0 0 #6fbe85}
[data-testid="stSidebar"] [role="radiogroup"] label>div:first-child{display:none}
.brand{display:flex;align-items:center;gap:.7rem;padding:.4rem 0 .2rem}
.brand-mark{width:44px;height:44px;border-radius:13px;background:rgba(255,255,255,.12);display:flex;align-items:center;justify-content:center;font-size:24px}
.brand-name{font:700 1.3rem 'Space Grotesk';color:#fff}
.side-note{font-size:.78rem;color:#a9c0b0!important;line-height:1.5}
/* hero */
.hero{border-radius:26px;padding:3rem 2.8rem;background-size:cover;background-position:center;color:#fff;margin-bottom:1.3rem;box-shadow:0 18px 44px rgba(12,36,23,.2)}
.eyebrow{font-size:.74rem;font-weight:700;letter-spacing:.15em;color:#c4e8cd!important}
.hero h1{color:#fff!important;font-size:3.2rem;margin:.3rem 0 .6rem}
.hero p{color:#e0f3e5!important;max-width:620px;line-height:1.65;margin:0 0 1.1rem}
.pill{display:inline-block;padding:.35rem .8rem;margin:0 .4rem .4rem 0;border-radius:99px;background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.22);font-size:.78rem;font-weight:600;color:#fff!important}
/* headings */
.kicker{color:#287044!important;font-size:.72rem;font-weight:800;letter-spacing:.14em;text-transform:uppercase}
.title{font:700 1.7rem 'Space Grotesk';color:#17221b!important;margin:.1rem 0 .2rem}
.desc{color:#66756b!important;margin-bottom:1rem}
/* cards */
.card,.metric,.step{background:#fff;border:1px solid #dfe9e2;border-radius:20px;box-shadow:0 8px 26px rgba(16,42,27,.06)}
.card{padding:1.4rem;height:100%}
.card h3{color:#163622!important;margin:.2rem 0 .5rem;font-size:1.2rem}
.card p,.card li{color:#59665e!important;line-height:1.6}
.metric{padding:1.1rem 1.3rem}
.metric span{display:block;color:#66756b;font-size:.73rem;font-weight:700;letter-spacing:.07em;text-transform:uppercase}
.metric b{display:block;color:#163622;font:700 1.5rem 'Space Grotesk';margin-top:.3rem}
.step{padding:1.2rem;height:100%}
.step i{display:inline-flex;width:36px;height:36px;border-radius:11px;background:#e7f4ea;color:#1d5130;font-style:normal;font-weight:800;align-items:center;justify-content:center}
.step h4{margin:.8rem 0 .3rem;color:#163622}
.step p{margin:0;color:#59665e;font-size:.92rem;line-height:1.55}
/* scale gallery */
.grid{display:grid;grid-template-columns:repeat(6,1fr);gap:.9rem}
.sc{background:#fff;border:1px solid #dfe9e2;border-radius:18px;overflow:hidden;box-shadow:0 8px 22px rgba(16,42,27,.06);transition:.2s}
.sc:hover{transform:translateY(-4px)}
.sc img{display:block;width:100%;aspect-ratio:8/7;object-fit:cover}
.sc div{padding:.7rem .8rem .85rem;border-top:4px solid var(--c)}
.sc b{display:block;color:#163622;font-size:.92rem}
.sc span{color:#66756b;font-size:.78rem}
@media(max-width:900px){.grid{grid-template-columns:repeat(3,1fr)}}
/* result */
.result{border-radius:22px;padding:1.6rem;background:#fff;border:1px solid #dfe9e2;border-left:8px solid var(--c);box-shadow:0 10px 30px rgba(16,42,27,.07)}
.result .big{font:700 2.2rem 'Space Grotesk';color:#102a1b}
.result p{color:#59665e;margin:.3rem 0 0}
.badge{display:inline-block;padding:.3rem .8rem;border-radius:99px;color:#fff;font-weight:700;font-size:.8rem;background:var(--c)}
.bar{background:#fff;border:1px solid #e3ece6;border-radius:14px;padding:.7rem .95rem;margin:.45rem 0}
.bar.on{border-color:var(--c);box-shadow:0 0 0 2px color-mix(in srgb,var(--c) 22%,transparent)}
.bar-h{display:flex;justify-content:space-between;color:#163622;font-size:.88rem;font-weight:600;margin-bottom:.4rem}
.bar-h i{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:.5rem}
.track{height:9px;background:#e8eee9;border-radius:99px;overflow:hidden}
.fill{height:100%;border-radius:99px}
.notice{padding:1rem 1.1rem;border-radius:15px;background:#fff8e8;border:1px solid #f0dfb7;color:#76580e!important;line-height:1.55}
.empty{text-align:center;padding:3rem 1rem;border:1px dashed #c8d6cc;border-radius:22px;background:#fff}
.empty h3{color:#163622!important}.empty p{color:#66756b!important}
/* scanning */
.scan{position:relative;overflow:hidden;border-radius:16px;line-height:0}
.scan img{width:100%;filter:brightness(.92) saturate(1.1)}
.scan b{position:absolute;left:0;right:0;height:3px;background:linear-gradient(90deg,transparent,#eafbee,#6fbe85,#eafbee,transparent);box-shadow:0 0 16px 4px rgba(111,190,133,.85);animation:mv 1.8s ease-in-out infinite}
@keyframes mv{0%,100%{top:2%}50%{top:96%}}
/* widgets */
.stButton>button,.stDownloadButton>button{border-radius:12px!important;font-weight:700!important;min-height:2.9rem}
.stButton>button[kind="primary"]{background:linear-gradient(135deg,#24633d,#3d8a59)!important;border:none!important;color:#fff!important;box-shadow:0 8px 20px rgba(36,99,61,.2)}
[data-testid="stFileUploader"] section{border:1.5px dashed #8fb09a!important;background:#fff!important;border-radius:18px!important;padding:1.4rem!important}
</style>
""")


def header(kicker, title, desc=""):
    html(f'<div class="kicker">{kicker}</div><div class="title">{title}</div><div class="desc">{desc}</div>')


def metric(label, value):
    html(f'<div class="metric"><span>{label}</span><b>{value}</b></div>')


def gallery():
    cards = "".join(
        f'<div class="sc" style="--c:{RAMP[i]}"><img src="{leaf_uri(i)}"/>'
        f'<div><b>Class {i} · {CLASS_INFO[i][0]}</b><span>{CLASS_INFO[i][1]}</span></div></div>'
        for i in range(6))
    html(f'<div class="grid">{cards}</div>')


def show_image(slot, img, caption, scanning=False):
    with slot.container():
        if scanning:
            html(f'<div class="scan"><img src="{data_uri(img)}"/><b></b></div>')
        else:
            st.image(img, width="stretch")
        st.caption(caption)


# ------------------------------------------------------------------ SIDEBAR
with st.sidebar:
    html('<div class="brand"><div class="brand-mark">🌱</div><div class="brand-name">SoyStress AI</div></div>'
         '<div class="side-note">Soybean water-stress &amp; wilting assessment from leaf images.</div>')
    st.divider()
    st.radio("Navigation", list(PAGES), key="nav",
             format_func=lambda p: f"{PAGES[p]}   {p}", label_visibility="collapsed")
    st.divider()
    st.metric("Analyses this session", len(st.session_state.history))
    st.markdown('<div class="side-note">Research decision-support tool. Use alongside field observations.</div>',
                unsafe_allow_html=True)

page = st.session_state.nav

# ------------------------------------------------------------------ DASHBOARD
if page == "Dashboard":
    html(f"""
    <div class="hero" style='background-image:linear-gradient(100deg,rgba(8,28,17,.9) 28%,rgba(8,28,17,.15)),url("{hero_uri()}")'>
      <div class="eyebrow">AGRICULTURAL AI • SOYBEAN</div>
      <h1>See drought stress<br>before it costs yield.</h1>
      <p>Upload a soybean leaf or plant image and get an instant wilting-severity
      estimate on a six-class scale, powered by your trained machine-learning model.</p>
      <span class="pill">📷 Image-based</span><span class="pill">🎨 Colour + texture features</span>
      <span class="pill">⚡ Instant result</span>
    </div>""")
    a, b, c, d = st.columns(4)
    with a: metric("Analysis mode", "Image-based")
    with b: metric("Stress scale", "6 classes")
    with c: metric("Features used", "16")
    with d: metric("Session analyses", len(st.session_state.history))
    st.write("")
    header("QUICK ACTIONS", "Where would you like to go?")
    cols = st.columns(3, gap="medium")
    for col, (p, icon, text) in zip(cols, [
            ("Analyze Image", "🔬", "Upload an image and get a prediction."),
            ("Prediction History", "🕘", "Review and export this session's results."),
            ("Help", "💡", "Tips for taking images the model reads best.")]):
        with col:
            html(f'<div class="card"><div style="font-size:2rem">{icon}</div><h3>{p}</h3><p>{text}</p></div>')
            st.button(f"Open {p}", key=f"go_{p}", on_click=go, args=(p,),
                      type="primary" if p == "Analyze Image" else "secondary", width="stretch")
    st.write("")
    header("REFERENCE", "The six-class wilting scale", "Illustrative leaves showing how severity progresses from class 0 to class 5.")
    gallery()
    st.write("")
    header("WORKFLOW", "How it works")
    cols = st.columns(4, gap="medium")
    for col, (n, t, d) in zip(cols, [("01", "Upload", "Choose a clear soybean image."),
                                     ("02", "Process", "Denoise, enhance and isolate the green region."),
                                     ("03", "Predict", "Extract colour and texture features and run the model."),
                                     ("04", "Interpret", "Review class, confidence and probabilities.")]):
        with col:
            html(f'<div class="step"><i>{n}</i><h4>{t}</h4><p>{d}</p></div>')

# ------------------------------------------------------------------ ANALYZE
elif page == "Analyze Image":
    header("IMAGE ANALYSIS", "Analyze a soybean image", "Upload an image, then press Analyze.")
    left, right = st.columns([1.1, .9], gap="large")
    with left:
        uploaded = st.file_uploader("Choose soybean image", type=["jpg", "jpeg", "png", "webp"],
                                    label_visibility="collapsed")
        slot = st.empty()
        image = None
        if uploaded:
            image = Image.open(uploaded).convert("RGB")
            cap = f"**{uploaded.name}** • {image.width} × {image.height}px"
            show_image(slot, image, cap)
    with right:
        html("""<div class="card"><div class="kicker">PHOTO TIPS</div><h3>For the best result</h3>
        <ul><li>Fill the frame with the leaf or plant.</li><li>Use natural, even daylight.</li>
        <li>Avoid blur, heavy shadows and very dark images.</li>
        <li>Keep soil and background to a minimum.</li></ul></div>""")
        st.write("")
        if image is not None:
            if st.button("🌿  ANALYZE IMAGE", type="primary", width="stretch"):
                show_image(slot, image, cap, scanning=True)
                try:
                    with st.spinner("Processing image and generating prediction..."):
                        res = predict_image(image)
                    st.session_state.last_result, st.session_state.last_image = res, image
                    st.session_state.history.insert(0, {
                        "Time": datetime.now().strftime("%Y-%m-%d %H:%M"), "Image": uploaded.name,
                        "Class": res["class"], "Label": res["label"],
                        "Confidence": f'{res["confidence"] * 100:.1f}%'})
                except Exception as e:
                    st.error("Model loading/prediction failed.")
                    st.exception(e)
                finally:
                    show_image(slot, image, cap)
        else:
            st.info("Upload an image to enable the analysis button.")

    r = st.session_state.last_result
    if r:
        st.divider()
        header("MODEL RESULT", "Prediction result")
        col = RAMP[r["class"]]
        a, b = st.columns([1, 1], gap="large")
        with a:
            html(f"""<div class="result" style="--c:{col}"><span class="badge">CLASS {r["class"]}</span>
            <div class="big">{r["label"]}</div><p>{r["description"]}</p>
            <p><b>Model probability: {r["confidence"] * 100:.1f}%</b></p></div>""")
            if r["confidence"] < 0.4:
                st.warning("Low confidence - the model is unsure. Try a clearer, better-lit image.")
            st.write("")
            st.image(leaf_uri(r["class"]), caption=f'Reference: class {r["class"]} leaf', width=260)
        with b:
            probs = r["probabilities"]
            rows = ""
            for i in range(6):
                p = probs.get(i, 0.0) * 100
                on = "on" if i == r["class"] else ""
                rows += (f'<div class="bar {on}" style="--c:{RAMP[i]}"><div class="bar-h"><span>'
                         f'<i style="background:{RAMP[i]}"></i>Class {i} · {CLASS_INFO[i][0]}</span>'
                         f'<b>{p:.1f}%</b></div><div class="track"><div class="fill" '
                         f'style="width:{p:.1f}%;background:{RAMP[i]}"></div></div></div>')
            html(rows)
        t1, t2, t3 = st.tabs(["Original", "Enhanced", "Segmented green region"])
        with t1: st.image(st.session_state.last_image, width="stretch")
        with t2: st.image(r["processed"][:, :, ::-1], width="stretch")
        with t3: st.image(r["segmented"][:, :, ::-1], width="stretch")
        with st.expander("🔎 View extracted features"):
            st.dataframe(pd.DataFrame([r["features"]]).T.rename(columns={0: "value"}), width="stretch")

# ------------------------------------------------------------------ HISTORY
elif page == "Prediction History":
    header("SESSION RECORD", "Prediction history", "Predictions made during this session.")
    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history)
        st.dataframe(df, width="stretch", hide_index=True)
        c1, c2, _ = st.columns([1, 1, 3])
        c1.download_button("⬇ Download CSV", df.to_csv(index=False), "soystress_history.csv", "text/csv",
                           width="stretch")
        if c2.button("🗑 Clear history", width="stretch"):
            st.session_state.history, st.session_state.last_result = [], None
            st.rerun()
    else:
        html('<div class="empty"><div style="font-size:2.6rem">🕘</div><h3>No predictions yet</h3>'
             '<p>Analyzed images will appear here.</p></div>')
        st.button("Analyze an image", type="primary", on_click=go, args=("Analyze Image",))

# ------------------------------------------------------------------ ABOUT
elif page == "About System":
    header("PROJECT INFORMATION", "About SoyStress AI",
           "An image-based research tool for soybean wilting and water-stress assessment.")
    gallery()
    st.write("")
    a, b = st.columns(2, gap="large")
    with a:
        html("""<div class="card"><div class="kicker">PIPELINE</div><h3>From image to assessment</h3>
        <ol><li><b>Preprocessing</b> - resize, denoise, contrast enhancement.</li>
        <li><b>Segmentation</b> - isolate the green plant region.</li>
        <li><b>Feature extraction</b> - colour, vegetation index and texture (GLCM).</li>
        <li><b>ML prediction</b> - trained ExtraTrees classifier.</li>
        <li><b>Interpretation</b> - class, probability and severity.</li></ol></div>""")
    with b:
        html("""<div class="card"><div class="kicker">TECHNOLOGY</div><h3>Built with</h3>
        <p>Python • Streamlit • OpenCV • NumPy • Pandas • scikit-image • scikit-learn • Joblib</p>
        <div class="notice"><b>Research note:</b> this is an image-based estimate of observed wilting
        severity. It does not replace soil-moisture measurement or field diagnosis.</div></div>""")

# ------------------------------------------------------------------ HELP
else:
    header("USER GUIDE", "Help & usage")
    with st.expander("How do I use the system?", expanded=True):
        st.markdown("1. Open **Analyze Image**.\n2. Upload a clear soybean image.\n"
                    "3. Press **Analyze Image**.\n4. Review the class, probabilities and processed views.\n"
                    "5. Export results from **Prediction History**.")
    with st.expander("Model loading / prediction failed"):
        st.write("Make sure `best_model.pkl` and `feature_names.pkl` are inside the `models/` folder.")
    with st.expander("The prediction looks wrong"):
        st.write("Use a sharp, evenly lit image where the leaf fills most of the frame.")
    with st.expander("Changes are not showing"):
        st.write("Restart Streamlit after replacing project files.")
    with st.expander("How do I use my own photos?"):
        st.write("Create an `assets/` folder next to `app.py` and add `hero.jpg` and "
                 "`class_0.jpg` ... `class_5.jpg`. They replace the generated illustrations.")
    html('<div class="notice"><b>Important:</b> predictions are decision-support outputs and should be '
         'read together with field observations and agronomic data.</div>')