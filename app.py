import streamlit as st
import textwrap
import base64
from io import BytesIO
from PIL import Image
from datetime import datetime
import pandas as pd
from core.prediction import predict_image


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="SoyStress AI",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# SESSION STATE
# ============================================================

if "history" not in st.session_state:
    st.session_state.history = []

if "last_result" not in st.session_state:
    st.session_state.last_result = None

if "nav" not in st.session_state:
    st.session_state.nav = "Dashboard"


# ============================================================
# HTML RENDER HELPER
# ============================================================

def render_html(html):
    """Render custom HTML safely after removing Python indentation.

    textwrap.dedent() only strips the *common* leading whitespace across
    all lines. Because these HTML blocks are nested (e.g. an outer <div>
    at one indent level with inner <div>/<h3>/<p> tags indented further),
    dedent leaves the inner lines with leftover indentation of 4+ spaces.
    Markdown treats any line indented 4+ spaces as an indented code block,
    so the HTML gets rendered as literal text instead of being parsed.
    Stripping each line individually avoids that entirely.
    """
    cleaned = "\n".join(line.strip() for line in html.strip("\n").splitlines())
    st.markdown(
        cleaned,
        unsafe_allow_html=True
    )


def _image_to_data_uri(image):
    """Encode a PIL image as a base64 PNG data URI for inline <img> tags."""
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{encoded}"


def render_static_image(slot, image, caption=None):
    """Render the plain uploaded image (no scanning overlay) into `slot`."""
    with slot.container():
        render_html('<div class="image-card">')
        st.image(image, width="stretch")
        render_html("</div>")
        if caption:
            st.caption(caption)


def render_scanning_image(slot, image):
    """Render the uploaded image with an animated scan-line overlay into
    `slot`, used while the model is processing the image."""
    data_uri = _image_to_data_uri(image)
    with slot.container():
        render_html(f"""
            <div class="image-card">
                <div class="scan-frame">
                    <img src="{data_uri}" />
                    <div class="scan-line"></div>
                </div>
                <div class="scan-badge">
                    <span class="scan-dot"></span>
                    Scanning image…
                </div>
            </div>
            """)


# ============================================================
# CUSTOM CSS
# ============================================================

render_html("""
<style>

@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');


/* ----------------------------------------------------------
   GLOBAL
---------------------------------------------------------- */

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

h1, h2, h3, h4 {
    font-family: 'Space Grotesk', sans-serif !important;
}

.stApp {
    background: #f6f8f7;
}

.block-container {
    max-width: 1280px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}


/* ----------------------------------------------------------
   SIDEBAR
---------------------------------------------------------- */

[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #102a1b 0%,
        #0b2116 100%
    );
}

[data-testid="stSidebar"] * {
    color: #f1f7f3 !important;
}

[data-testid="stSidebar"] .stCaption {
    color: #b9cbbf !important;
}

[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,.15);
}

.brand {
    padding: 10px 0;
}

.brand-mark {
    display: inline-flex;
    width: 42px;
    height: 42px;
    align-items: center;
    justify-content: center;
    border-radius: 12px;
    background: rgba(255,255,255,.10);
    font-size: 23px;
    margin-right: 9px;
    vertical-align: middle;
}

.brand-name {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.3rem;
    font-weight: 700;
    color: white;
    vertical-align: middle;
}

.brand-subtitle {
    color: #b9cbbf !important;
    font-size: .82rem;
    line-height: 1.5;
    margin-top: 10px;
}


/* ----------------------------------------------------------
   HERO
---------------------------------------------------------- */

.hero {
    padding: 2.7rem;
    border-radius: 28px;

    background:
        radial-gradient(
            circle at 88% 20%,
            rgba(111,190,133,.22),
            transparent 30%
        ),
        linear-gradient(
            135deg,
            #0c2417 0%,
            #1d5130 60%,
            #2c7448 100%
        );

    color: white;
    margin-bottom: 1.5rem;

    box-shadow:
        0 18px 45px rgba(12,36,23,.15);
}

.hero-eyebrow {
    color: #bfe4c9 !important;
    font-size: .75rem;
    font-weight: 700;
    letter-spacing: .14em;
}

.hero h1 {
    color: white !important;
    font-size: 3.1rem;
    margin: .35rem 0 .5rem;
}

.hero p {
    color: #d9f0df !important;
    max-width: 780px;
    line-height: 1.65;
    margin: 0;
}


/* ----------------------------------------------------------
   SECTION HEADERS
---------------------------------------------------------- */

.kicker {
    color: #287044 !important;
    font-size: .74rem;
    font-weight: 800;
    letter-spacing: .13em;
    text-transform: uppercase;
    margin-top: .3rem;
}

.section-title {
    font-family: 'Space Grotesk', sans-serif;
    color: #17221b !important;
    font-size: 1.75rem;
    font-weight: 700;
    margin-bottom: .25rem;
}

.section-description {
    color: #68766d !important;
    margin-bottom: 1rem;
}


/* ----------------------------------------------------------
   CARDS
---------------------------------------------------------- */

.metric,
.card,
.info-card {

    border: 1px solid #dfe9e2;
    border-radius: 20px;

    background: #ffffff;

    box-shadow:
        0 8px 28px rgba(16,42,27,.06);
}

.metric {
    padding: 1.25rem;
    min-height: 105px;
}

.metric-title {
    color: #68766d !important;
    font-size: .76rem;

    text-transform: uppercase;

    letter-spacing: .06em;

    font-weight: 600;
}

.metric-value {
    color: #163622 !important;

    font-family: 'Space Grotesk', sans-serif;

    font-size: 1.5rem;

    font-weight: 700;

    margin-top: .4rem;
}


/* ----------------------------------------------------------
   WORKFLOW
---------------------------------------------------------- */

.workflow {
    padding: 1.35rem;
    min-height: 185px;
}

.workflow-number {

    display: inline-flex;

    width: 36px;
    height: 36px;

    align-items: center;
    justify-content: center;

    border-radius: 11px;

    background: #e9f5ec;

    color: #1d5130 !important;

    font-weight: 800;
}

.workflow h3 {

    color: #163622 !important;

    margin:
        1rem 0 .45rem;

    font-size: 1.15rem;
}

.workflow p,
.info-card p,
.info-card li {

    color: #59665e !important;

    line-height: 1.6;
}


/* ----------------------------------------------------------
   INFORMATION CARDS
---------------------------------------------------------- */

.info-card {
    padding: 1.5rem;
}

.info-card h3,
.info-card h4 {

    color: #163622 !important;
}


/* ----------------------------------------------------------
   ASSESSMENT
---------------------------------------------------------- */

.assessment {

    border: 1px solid #cfe4d5;

    border-left:
        6px solid #287044;

    border-radius: 20px;

    padding:
        1.45rem 1.55rem;

    background:
        linear-gradient(
            135deg,
            #eef8f1,
            #f9fcf9
        );

    margin:
        1rem 0 1.4rem;
}

.assessment-label {

    color: #287044 !important;

    font-size: .73rem;

    letter-spacing: .13em;

    font-weight: 800;
}

.assessment h2 {

    color: #102a1b !important;

    margin:
        .4rem 0 .2rem;
}

.assessment p {

    color: #59665e !important;

    margin: 0;
}


/* ----------------------------------------------------------
   UPLOAD AREA
---------------------------------------------------------- */

.upload-panel {

    border:
        1.5px dashed #91b19b;

    border-radius: 22px;

    padding: 1.35rem;

    background:
        linear-gradient(
            180deg,
            #f9fcfa,
            #f1f8f3
        );
}

.upload-panel h3 {

    color: #163622 !important;

    margin:
        0 0 .3rem;
}

.upload-panel p {

    color: #68766d !important;

    margin: 0;
}

.chip {

    display: inline-block;

    padding:
        .35rem .65rem;

    border-radius: 999px;

    background: #e9f5ec;

    color: #1d5130 !important;

    font-size: .75rem;

    font-weight: 700;

    margin:
        .7rem .2rem 0 0;
}


/* ----------------------------------------------------------
   IMAGE
---------------------------------------------------------- */

.image-card {

    border:
        1px solid #dfe9e2;

    border-radius: 20px;

    padding: .6rem;

    background: white;

    margin-top: .8rem;
}


/* ----------------------------------------------------------
   SCANNING OVERLAY (shown while the model is processing)
---------------------------------------------------------- */

.scan-frame {
    position: relative;
    overflow: hidden;
    border-radius: 16px;
    line-height: 0;
}

.scan-frame img {
    display: block;
    width: 100%;
    border-radius: 16px;
    filter: brightness(0.92) saturate(1.1);
}

.scan-line {
    position: absolute;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(
        90deg,
        transparent,
        #eafbee,
        #6fbe85,
        #eafbee,
        transparent
    );
    box-shadow: 0 0 16px 4px rgba(111, 190, 133, .85);
    animation: scan-move 1.8s ease-in-out infinite;
}

.scan-frame::after {
    content: "";
    position: absolute;
    inset: 0;
    background: repeating-linear-gradient(
        0deg,
        rgba(111, 190, 133, .07) 0px,
        rgba(111, 190, 133, .07) 1px,
        transparent 1px,
        transparent 4px
    );
    pointer-events: none;
}

.scan-badge {
    display: inline-flex;
    align-items: center;
    gap: .45rem;
    margin-top: .6rem;
    font-size: .78rem;
    font-weight: 600;
    color: #1d5130 !important;
}

.scan-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #2c7448;
    animation: scan-pulse 1.1s ease-in-out infinite;
}

@keyframes scan-move {
    0%   { top: 2%; }
    50%  { top: 96%; }
    100% { top: 2%; }
}

@keyframes scan-pulse {
    0%, 100% { opacity: .35; transform: scale(.85); }
    50%      { opacity: 1;   transform: scale(1.1); }
}


/* ----------------------------------------------------------
   READY CARD
---------------------------------------------------------- */

.ready-card {

    border:
        1px solid #dfe9e2;

    border-radius: 22px;

    padding: 1.4rem;

    background: white;

    min-height: 100%;
}

.ready-card h3 {

    color: #163622 !important;
}

.ready-card p,
.ready-card li {

    color: #68766d !important;

    line-height: 1.55;
}


/* ----------------------------------------------------------
   PROBABILITY PROFILE
---------------------------------------------------------- */

.probability-card {

    border:
        1px solid #dfe9e2;

    border-radius: 15px;

    padding:
        .85rem 1rem;

    background: white;

    margin: .5rem 0;
}

.probability-head {

    display: flex;

    justify-content:
        space-between;

    color: #163622 !important;

    font-weight: 700;

    font-size: .88rem;

    margin-bottom: .4rem;
}

.probability-track {

    height: 9px;

    background: #e8eee9;

    border-radius: 99px;

    overflow: hidden;
}

.probability-fill {

    height: 100%;

    background:
        linear-gradient(
            90deg,
            #3d8a59,
            #77b78a
        );

    border-radius: 99px;
}

.probability-fill.predicted {

    background:
        linear-gradient(
            90deg,
            #1d5130,
            #4b9964
        );
}


/* ----------------------------------------------------------
   ABOUT
---------------------------------------------------------- */

.about-hero {

    padding: 1.7rem;

    border-radius: 24px;

    background:
        linear-gradient(
            135deg,
            #eaf5ed,
            #f8fbf9
        );

    border:
        1px solid #d7e8dc;

    margin-bottom: 1.2rem;
}

.about-hero h2 {

    color: #102a1b !important;

    margin:
        0 0 .45rem;
}

.about-hero p {

    color: #526158 !important;

    line-height: 1.65;

    margin: 0;
}


/* ----------------------------------------------------------
   NOTICE
---------------------------------------------------------- */

.notice {

    padding:
        1rem 1.1rem;

    border-radius: 15px;

    background: #fff8e8;

    border:
        1px solid #f0dfb7;

    color: #76580e !important;

    line-height: 1.55;
}


/* ----------------------------------------------------------
   EMPTY STATE
---------------------------------------------------------- */

.empty-state {

    text-align: center;

    padding: 3rem 1rem;

    border:
        1px dashed #c8d6cc;

    border-radius: 22px;

    background: white;
}

.empty-state h3 {

    color: #163622 !important;
}

.empty-state p {

    color: #68766d !important;
}


/* ----------------------------------------------------------
   BUTTONS
---------------------------------------------------------- */

.stButton > button {

    border-radius: 12px !important;

    font-weight: 700 !important;

    min-height: 3rem;
}

.stButton > button[kind="primary"] {

    background:
        linear-gradient(
            135deg,
            #24633d,
            #3d8a59
        ) !important;

    border: none !important;

    color: white !important;

    box-shadow:
        0 8px 20px rgba(36,99,61,.18);
}

.stButton > button[kind="primary"]:hover {

    background:
        linear-gradient(
            135deg,
            #1d5130,
            #34794d
        ) !important;

    color: white !important;
}


/* ----------------------------------------------------------
   FILE UPLOADER
---------------------------------------------------------- */

[data-testid="stFileUploader"] section {

    border:
        1px dashed #9db8a5 !important;

    background: white !important;

    border-radius: 16px !important;
}

[data-testid="stFileUploader"] span,
[data-testid="stFileUploader"] small,
[data-testid="stFileUploader"] label {

    color: #526158 !important;
}

[data-testid="stFileUploader"] button {

    color: #1d5130 !important;

    border-color:
        #a9c1b0 !important;

    background: white !important;
}


/* ----------------------------------------------------------
   MISC
---------------------------------------------------------- */

hr {
    border-color: #dfe9e2 !important;
}

footer {
    visibility: hidden;
}

</style>
""")


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def section_header(kicker, title, description=None):

    render_html(
        f'<div class="kicker">{kicker}</div>')

    render_html(
        f'<div class="section-title">{title}</div>')

    if description:

        render_html(
            f'<div class="section-description">{description}</div>')


def metric_card(title, value):

    render_html(
        f"""
        <div class="metric">

            <div class="metric-title">
                {title}
            </div>

            <div class="metric-value">
                {value}
            </div>

        </div>
        """)


def probability_profile(probabilities, predicted_class):

    for index, probability in enumerate(probabilities):

        percentage = float(probability) * 100

        predicted = (
            index == int(predicted_class)
        )

        label = (
            "Predicted class"
            if predicted
            else "Class"
        )

        fill_class = (
            "probability-fill predicted"
            if predicted
            else "probability-fill"
        )

        render_html(
            f"""
            <div class="probability-card">

                <div class="probability-head">

                    <span>
                        {label} {index}
                    </span>

                    <span>
                        {percentage:.1f}%
                    </span>

                </div>

                <div class="probability-track">

                    <div
                        class="{fill_class}"
                        style="width:{max(0,min(100,percentage)):.2f}%">
                    </div>

                </div>

            </div>
            """)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    render_html(
        """
        <div class="brand">

            <span class="brand-mark">
                🌱
            </span>

            <span class="brand-name">
                SoyStress AI
            </span>

            <div class="brand-subtitle">
                Intelligent soybean water-stress &
                wilting assessment
            </div>

        </div>
        """)

    st.divider()

    st.radio(
        "Navigation",
        [
            "Dashboard",
            "Analyze Image",
            "Prediction History",
            "About System",
            "Help"
        ],
        key="nav",
        label_visibility="collapsed"
    )

    st.divider()

    st.caption(
        "Research decision-support system"
    )


page = st.session_state.nav


# ============================================================
# DASHBOARD
# ============================================================

if page == "Dashboard":

    render_html(
        """
        <div class="hero">

            <div class="hero-eyebrow">
                AGRICULTURAL AI • SOYBEAN
            </div>

            <h1>
                SoyStress AI
            </h1>

            <p>
                Image-based assessment of soybean
                water-stress and wilting severity
                using your trained machine-learning model.
            </p>

        </div>
        """)

    a, b, c = st.columns(3)

    with a:
        metric_card(
            "Analysis mode",
            "Image-based"
        )

    with b:
        metric_card(
            "Stress scale",
            "6 classes"
        )

    with c:
        metric_card(
            "Session analyses",
            str(len(st.session_state.history))
        )

    st.write("")

    section_header(
        "GET STARTED",
        "Start an analysis",
        "Upload a clear soybean image and generate a model prediction."
    )

    if st.button(
        "🔍  Analyze a soybean image",
        type="primary",
        width="stretch"
    ):

        st.session_state.nav = "Analyze Image"

        st.rerun()

    st.write("")

    section_header(
        "WORKFLOW",
        "How SoyStress AI works",
        "The system follows the image-processing and prediction pipeline used by the application."
    )

    workflow = [

        (
            "01",
            "Upload",
            "Select a clear soybean image from your computer."
        ),

        (
            "02",
            "Process",
            "Apply preprocessing and isolate the relevant green region."
        ),

        (
            "03",
            "Predict",
            "Extract visual features and run the saved ML model."
        ),

        (
            "04",
            "Interpret",
            "Review the predicted class, probability and assessment."
        )

    ]

    cols = st.columns(4, gap="medium")

    for col, (number, title, description) in zip(
        cols,
        workflow
    ):

        with col:

            render_html(
                f"""
                <div class="card workflow">

                    <div class="workflow-number">
                        {number}
                    </div>

                    <h3>
                        {title}
                    </h3>

                    <p>
                        {description}
                    </p>

                </div>
                """)

    st.write("")

    left, right = st.columns(
        [1.15, .85],
        gap="large"
    )

    with left:

        render_html(
            """
            <div class="info-card">

                <div class="kicker">
                    SYSTEM OVERVIEW
                </div>

                <h3>
                    From soybean image to stress assessment
                </h3>

                <p>
                    SoyStress AI analyzes visual characteristics
                    of a soybean image and uses the resulting
                    feature representation with the trained
                    machine-learning model to estimate observed
                    wilting severity.
                </p>

                <p>
                    The output is intended as a research
                    decision-support result and should be
                    considered together with field observations
                    and other agronomic measurements.
                </p>

            </div>
            """)

    with right:

        render_html(
            """
            <div class="info-card">

                <div class="kicker">
                    QUICK GUIDE
                </div>

                <h3>
                    For the best analysis
                </h3>

                <ul>

                    <li>
                        Use a clear, well-focused soybean image.
                    </li>

                    <li>
                        Keep the plant or leaf clearly visible.
                    </li>

                    <li>
                        Avoid heavily blurred or extremely dark images.
                    </li>

                    <li>
                        Use the result together with field observations.
                    </li>

                </ul>

            </div>
            """)


# ============================================================
# ANALYZE IMAGE
# ============================================================

elif page == "Analyze Image":

    section_header(
        "IMAGE ANALYSIS",
        "Analyze Soybean Image",
        "Upload a soybean image and let the trained model assess its wilting severity."
    )

    left, right = st.columns(
        [1.05, .95],
        gap="large"
    )

    with left:

        render_html(
            """
            <div class="upload-panel">

                <h3>
                    📤 Upload a soybean image
                </h3>

                <p>
                    Drag and drop an image below,
                    or browse your computer.
                </p>

                <span class="chip">
                    JPG
                </span>

                <span class="chip">
                    JPEG
                </span>

                <span class="chip">
                    PNG
                </span>

                <span class="chip">
                    WEBP
                </span>

            </div>
            """)

        uploaded = st.file_uploader(
            "Choose soybean image",
            type=[
                "jpg",
                "jpeg",
                "png",
                "webp"
            ],
            label_visibility="collapsed"
        )

        image = None
        image_slot = st.empty()

        if uploaded:

            image = Image.open(
                uploaded
            ).convert("RGB")

            render_static_image(
                image_slot,
                image,
                caption=(
                    f"**{uploaded.name}** • "
                    f"{image.width} × {image.height}px"
                )
            )

    with right:

        render_html(
            """
            <div class="ready-card">

                <div class="kicker">
                    ANALYSIS PIPELINE
                </div>

                <h3>
                    Ready to analyze?
                </h3>

                <p>
                    Once submitted, the image passes through
                    the application's processing pipeline before
                    the trained model produces its result.
                </p>

                <ul>

                    <li>
                        Image preprocessing
                    </li>

                    <li>
                        Green-region segmentation
                    </li>

                    <li>
                        Colour and texture feature extraction
                    </li>

                    <li>
                        Trained ML model prediction
                    </li>

                    <li>
                        Wilting severity interpretation
                    </li>

                </ul>

            </div>
            """)

        st.write("")

        if uploaded and image is not None:

            if st.button(
                "🌿  ANALYZE IMAGE",
                type="primary",
                width="stretch"
            ):

                render_scanning_image(
                    image_slot,
                    image
                )

                with st.spinner(
                    "Processing image and generating prediction..."
                ):

                    try:

                        result = predict_image(
                            image
                        )

                        st.session_state.last_result = result

                        st.session_state.history.insert(
                            0,
                            {
                                "Time":
                                    datetime.now().strftime(
                                        "%Y-%m-%d %H:%M"
                                    ),

                                "Image":
                                    uploaded.name,

                                "Class":
                                    result["class"],

                                "Label":
                                    result["label"],

                                "Confidence":
                                    f'{result["confidence"] * 100:.1f}%'
                            }
                        )

                        st.success(
                            "Analysis completed successfully."
                        )

                    except Exception as e:

                        st.error(
                            "Model loading/prediction failed."
                        )

                        st.exception(e)

                        st.info(
                            "Ensure best_model.pkl and "
                            "feature_names.pkl are inside "
                            "the models/ folder."
                        )

                    finally:

                        render_static_image(
                            image_slot,
                            image,
                            caption=(
                                f"**{uploaded.name}** • "
                                f"{image.width} × {image.height}px"
                            )
                        )

        else:

            st.info(
                "Upload an image to activate the analysis button."
            )


    # --------------------------------------------------------
    # PREDICTION RESULT
    # --------------------------------------------------------

    if st.session_state.last_result:

        r = st.session_state.last_result

        st.divider()

        section_header(
            "MODEL RESULT",
            "Prediction Result",
            "Summary of the most recently analyzed image."
        )

        a, b, c = st.columns(3)

        with a:

            metric_card(
                "Predicted class",
                f'Class {r["class"]}'
            )

        with b:

            metric_card(
                "Wilting / stress level",
                r["label"]
            )

        with c:

            metric_card(
                "Model probability",
                f'{r["confidence"] * 100:.1f}%'
            )

        render_html(
            f"""
            <div class="assessment">

                <div class="assessment-label">
                    ASSESSMENT
                </div>

                <h2>
                    {r["label"]}
                </h2>

                <p>
                    {r["description"]}
                </p>

            </div>
            """)

        section_header(
            "MODEL OUTPUT",
            "Class probability profile",
            "Relative probability assigned to each wilting class."
        )

        probability_profile(
            r["probabilities"],
            r["class"]
        )

        with st.expander(
            "🔎 View extracted features"
        ):

            st.dataframe(
                pd.DataFrame(
                    [r["features"]]
                ),
                width="stretch",
                hide_index=True
            )


# ============================================================
# PREDICTION HISTORY
# ============================================================

elif page == "Prediction History":

    section_header(
        "SESSION RECORD",
        "Prediction History",
        "Predictions generated during the current application session."
    )

    if st.session_state.history:

        st.dataframe(
            pd.DataFrame(
                st.session_state.history
            ),
            width="stretch",
            hide_index=True
        )

        st.write("")

        if st.button(
            "🗑️ Clear session history"
        ):

            st.session_state.history = []

            st.session_state.last_result = None

            st.rerun()

    else:

        render_html(
            """
            <div class="empty-state">

                <div style="font-size:2.5rem">
                    🕘
                </div>

                <h3>
                    No predictions yet
                </h3>

                <p>
                    Your analyzed soybean images will appear
                    here during this session.
                </p>

            </div>
            """)


# ============================================================
# ABOUT SYSTEM
# ============================================================

elif page == "About System":

    section_header(
        "PROJECT INFORMATION",
        "About SoyStress AI",
        "An image-based research decision-support application for soybean wilting and water-stress assessment."
    )

    render_html(
        """
        <div class="about-hero">

            <h2>
                🌱 Intelligent soybean stress assessment
            </h2>

            <p>
                SoyStress AI provides an accessible interface
                for applying a trained machine-learning model
                to soybean images and estimating observed
                wilting severity associated with water stress.
            </p>

        </div>
        """)

    a, b = st.columns(
        2,
        gap="large"
    )

    with a:

        render_html(
            """
            <div class="info-card">

                <div class="kicker">
                    PURPOSE
                </div>

                <h3>
                    What the system does
                </h3>

                <p>
                    The application accepts a soybean image,
                    processes the image, extracts visual features
                    and passes those features to the saved
                    machine-learning model.
                </p>

                <p>
                    The final output is a predicted wilting/stress
                    class together with a probability estimate
                    and severity label.
                </p>

            </div>
            """)

    with b:

        render_html(
            """
            <div class="info-card">

                <div class="kicker">
                    DECISION SUPPORT
                </div>

                <h3>
                    How to interpret results
                </h3>

                <p>
                    A higher wilting class represents greater
                    observed wilting severity within the six-class
                    scale used by the trained model.
                </p>

                <p>
                    Predictions should be interpreted alongside
                    field observations, environmental conditions
                    and other agronomic measurements.
                </p>

            </div>
            """)

    st.write("")

    section_header(
        "METHODOLOGY",
        "System processing pipeline",
        "Major stages used to prepare an image for prediction."
    )

    stages = [

        (
            "01",
            "Image acquisition",
            "Supply a soybean image."
        ),

        (
            "02",
            "Preprocessing",
            "Resize, denoise and enhance the image."
        ),

        (
            "03",
            "Segmentation",
            "Isolate the relevant green plant region."
        ),

        (
            "04",
            "Feature extraction",
            "Calculate colour, vegetation-index and texture features."
        ),

        (
            "05",
            "ML prediction",
            "Run the saved trained model."
        ),

        (
            "06",
            "Interpretation",
            "Display class, probability and severity."
        )

    ]

    cols = st.columns(
        3,
        gap="medium"
    )

    for col, (
        number,
        title,
        description
    ) in zip(
        cols * 2,
        stages
    ):

        with col:

            render_html(
                f"""
                <div class="card workflow">

                    <div class="workflow-number">
                        {number}
                    </div>

                    <h3>
                        {title}
                    </h3>

                    <p>
                        {description}
                    </p>

                </div>
                """)

    st.write("")

    a, b = st.columns(
        2,
        gap="large"
    )

    with a:

        render_html(
            """
            <div class="info-card">

                <div class="kicker">
                    STRESS SCALE
                </div>

                <h3>
                    Six-class wilting scale
                </h3>

                <p>
                    <strong>
                        Class 0 — Least wilting
                    </strong><br>
                    Lowest observed wilting severity.
                </p>

                <p>
                    <strong>
                        Class 1 — Slight wilting
                    </strong><br>
                    Early or mild wilting symptoms.
                </p>

                <p>
                    <strong>
                        Class 2 — Moderate wilting
                    </strong><br>
                    Intermediate wilting severity.
                </p>

                <p>
                    <strong>
                        Class 3 — High wilting
                    </strong><br>
                    Pronounced wilting symptoms.
                </p>

                <p>
                    <strong>
                        Class 4 — Very high wilting
                    </strong><br>
                    Severe observed wilting.
                </p>

                <p>
                    <strong>
                        Class 5 — Most wilting
                    </strong><br>
                    Highest wilting severity in the
                    six-class scale.
                </p>

            </div>
            """)

    with b:

        render_html(
            """
            <div class="info-card">

                <div class="kicker">
                    TECHNOLOGY
                </div>

                <h3>
                    Software components
                </h3>

                <p>
                    Python • Streamlit • OpenCV • NumPy •
                    Pandas • Scikit-image • Scikit-learn • Joblib
                </p>

                <br>

                <div class="notice">

                    <strong>
                        Research note:
                    </strong>

                    <br>

                    This application provides an image-based
                    estimate of observed soybean wilting severity.
                    It should not replace direct soil-moisture
                    measurements or field diagnosis.

                </div>

            </div>
            """)


# ============================================================
# HELP
# ============================================================

elif page == "Help":

    section_header(
        "USER GUIDE",
        "Help & Usage",
        "A quick guide to operating SoyStress AI."
    )

    a, b = st.columns(
        2,
        gap="large"
    )

    with a:

        render_html(
            """
            <div class="info-card">

                <div class="kicker">
                    STEP-BY-STEP
                </div>

                <h3>
                    How to use the system
                </h3>

                <ol>

                    <li>
                        Open <strong>Analyze Image</strong>.
                    </li>

                    <li>
                        Upload a clear soybean image.
                    </li>

                    <li>
                        Click <strong>ANALYZE IMAGE</strong>.
                    </li>

                    <li>
                        Wait for processing.
                    </li>

                    <li>
                        Review the predicted class,
                        severity and probabilities.
                    </li>

                    <li>
                        Use Prediction History to review
                        session results.
                    </li>

                </ol>

            </div>
            """)

    with b:

        render_html(
            """
            <div class="info-card">

                <div class="kicker">
                    TROUBLESHOOTING
                </div>

                <h3>
                    Common issues
                </h3>

                <p>

                    <strong>
                        Model loading/prediction failed:
                    </strong>

                    <br>

                    Confirm that best_model.pkl and
                    feature_names.pkl are inside the
                    models/ folder.

                </p>

                <p>

                    <strong>
                        Poor prediction:
                    </strong>

                    <br>

                    Try a clear, well-lit image with the
                    soybean plant or leaf visible.

                </p>

                <p>

                    <strong>
                        Missing output:
                    </strong>

                    <br>

                    Restart Streamlit after replacing
                    project files.

                </p>

            </div>
            """)

    st.write("")

    render_html(
        """
        <div class="notice">

            <strong>
                Important:
            </strong>

            Model predictions are research
            decision-support outputs and should be
            interpreted alongside field observations
            and relevant agronomic data.

        </div>
        """)