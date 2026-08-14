import streamlit as st
from ultralytics import YOLO
from PIL import Image
import numpy as np
import cv2
import tempfile
import os
import smtplib
import subprocess
import imageio_ffmpeg
import requests
import base64

from email.message import EmailMessage
from datetime import datetime
from zoneinfo import ZoneInfo
from streamlit_geolocation import streamlit_geolocation


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="EcoBin-AI",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# SESSION STATE
# ============================================================

defaults = {
    "page": "home",
    "last_alert_time": None,

    "image_result": None,
    "camera_result": None,
    "video_result": None,

    "live_latitude": None,
    "live_longitude": None,
    "live_accuracy": None,
    "live_area": None,
    "location_loaded": False,
}

for key, value in defaults.items():

    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# PREMIUM DARK UI
# ============================================================

st.markdown(
    """
<style>

/* ============================================================
   ROOT COLORS
   ============================================================ */

:root {

    --bg: #050b14;
    --bg2: #08111f;

    --card: #0b1626;
    --card2: #0d192b;

    --border: #263a55;
    --border2: #314965;

    --white: #f8fafc;
    --text: #dce7f5;
    --muted: #91a3ba;

    --blue: #3b82f6;
    --blue2: #60a5fa;

    --green: #22c55e;
    --green2: #34d399;

    --purple: #7c5cff;

    --danger: #ef4444;
    --orange: #fb923c;
}


/* ============================================================
   MAIN APP
   ============================================================ */

.stApp {

    background:

        radial-gradient(
            circle at 5% 5%,
            rgba(34,197,94,.08),
            transparent 23%
        ),

        radial-gradient(
            circle at 95% 5%,
            rgba(59,130,246,.08),
            transparent 25%
        ),

        linear-gradient(
            135deg,
            #050b14,
            #07101c 45%,
            #040912
        );

    color: var(--text);
}


/* ============================================================
   CONTAINER
   ============================================================ */

.block-container {

    max-width: 1280px;

    padding:
        22px 4% 28px 4% !important;
}


/* ============================================================
   HIDE STREAMLIT DEFAULT UI
   ============================================================ */

#MainMenu,
footer,
header {

    visibility: hidden;
}


/* ============================================================
   GENERAL TEXT
   ============================================================ */

.stMarkdown,
.stMarkdown p,
.stMarkdown li {

    color: var(--text);
}


/* ============================================================
   HOME TITLE
   ============================================================ */

.hero-title {

    text-align: center;

    color: #e8f1ff;

    font-size: 31px;

    font-weight: 900;

    letter-spacing: -.5px;

    margin: 0;
}


.hero-subtitle {

    text-align: center;

    color: #8497b0;

    font-size: 13px;

    margin:
        4px 0 18px 0;
}


/* ============================================================
   NEW HERO CARD
   ============================================================ */

.hero-card-new {

    min-height: 315px;

    background:

        radial-gradient(
            circle at 88% 85%,
            rgba(34,197,94,.07),
            transparent 30%
        ),

        radial-gradient(
            circle at 5% 10%,
            rgba(59,130,246,.05),
            transparent 28%
        ),

        linear-gradient(
            145deg,
            #0d1728,
            #08111f
        );

    border:
        1px solid #263a55;

    border-radius:
        22px;

    padding:
        38px 40px 27px 40px;

    box-shadow:

        0 18px 50px
        rgba(0,0,0,.34),

        inset 0 1px 0
        rgba(255,255,255,.025);

    position: relative;

    overflow: hidden;

    display: flex;

    flex-direction: column;

    justify-content: space-between;
}


/* TOP GRADIENT LINE */

.hero-card-new::before {

    content: "";

    position: absolute;

    left: 0;
    top: 0;

    width: 100%;
    height: 5px;

    background:

        linear-gradient(
            90deg,
            #22c55e,
            #3b82f6,
            #7c5cff
        );
}


/* ============================================================
   HERO TOP CONTENT
   ============================================================ */

.hero-top-content {

    position: relative;

    z-index: 2;
}


.program-pill {

    display: inline-block;

    width: fit-content;

    padding:
        9px 15px;

    border-radius:
        999px;

    background:
        rgba(37,99,235,.10);

    color:
        #b9d3f7;

    border:
        1px solid #31527b;

    font-size:
        12px;

    font-weight:
        800;

    margin-bottom:
        25px;
}


.hero-career-new {

    color:
        #f5f8fc;

    font-size:
        33px;

    font-weight:
        900;

    line-height:
        1.2;

    margin-bottom:
        13px;
}


.hero-capstone-new {

    color:
        #9aabc0;

    font-size:
        18px;

    font-weight:
        700;
}


/* ============================================================
   HERO PROJECT AREA
   ============================================================ */

.hero-project-area {

    display:
        flex;

    align-items:
        center;

    justify-content:
        space-between;

    gap:
        20px;

    margin-top:
        30px;

    position:
        relative;

    z-index:
        2;
}


.hero-project-info {

    flex:
        1;

    min-width:
        0;
}


.hero-project-name-new {

    color:
        #22e879;

    font-size:
        25px;

    font-weight:
        900;

    line-height:
        1.2;

    margin-bottom:
        7px;
}


.hero-project-subtitle {

    color:
        #95a7bd;

    font-size:
        12px;

    font-weight:
        700;

    white-space:
        nowrap;
}


/* ============================================================
   LOGO INSIDE HERO CARD
   ============================================================ */

.hero-logo-container {

    width:
        92px;

    height:
        92px;

    flex-shrink:
        0;

    display:
        flex;

    align-items:
        center;

    justify-content:
        center;
}


.hero-project-logo {

    width:
        84px;

    height:
        84px;

    object-fit:
        contain;

    border-radius:
        17px;

    background:
        #ffffff;

    padding:
        3px;

    box-shadow:
        0 9px 25px
        rgba(0,0,0,.35);
}


/* ============================================================
   DESCRIPTION CARD
   ============================================================ */

.description-card {

    min-height:
        315px;

    background:

        linear-gradient(
            145deg,
            #0d1728,
            #08111f
        ) !important;

    border:
        1px solid #263a55 !important;

    border-radius:
        22px;

    padding:
        25px 27px;

    box-shadow:
        0 15px 40px
        rgba(0,0,0,.27) !important;
}


.description-heading {

    color:
        #e8f1ff !important;

    font-size:
        18px;

    font-weight:
        900;

    margin-bottom:
        13px;
}


.description-card p {

    color:
        #93a6bd !important;

    font-size:
        13px;

    line-height:
        1.75;

    margin:
        0 0 14px 0;
}


/* ============================================================
   SECTION TITLE
   ============================================================ */

.section-title {

    color:
        #dce9f9;

    font-size:
        19px;

    font-weight:
        900;

    margin:
        15px 0 10px 0;
}


/*
IMPORTANT:
No huge margin after hero.
This keeps System Capabilities close to
the first-page structure.
*/


/* ============================================================
   CAPABILITY CARD
   ============================================================ */

.capability-card {

    background:

        linear-gradient(
            145deg,
            #0d192b,
            #091321
        ) !important;

    border:
        1px solid #263a55;

    border-radius:
        16px;

    padding:
        16px 12px;

    min-height:
        105px;

    text-align:
        center;

    box-shadow:
        0 9px 25px
        rgba(0,0,0,.22);
}


.capability-icon {

    font-size:
        21px;

    margin-bottom:
        5px;
}


.capability-title {

    color:
        #e4edf9 !important;

    font-size:
        13px;

    font-weight:
        900;
}


.capability-text {

    color:
        #8ea1b8 !important;

    font-size:
        10.5px;

    line-height:
        1.45;

    margin-top:
        5px;
}


/* ============================================================
   TEAM
   ============================================================ */

.team-card {

    background:

        linear-gradient(
            145deg,
            #0d192b,
            #091321
        ) !important;

    border:
        1px solid #263a55;

    border-radius:
        17px;

    padding:
        19px;

    min-height:
        150px;

    box-shadow:
        0 9px 25px
        rgba(0,0,0,.20);
}


.team-heading {

    color:
        #a9c7ef !important;

    font-size:
        11px;

    font-weight:
        900;

    letter-spacing:
        .3px;

    margin-bottom:
        10px;
}


.team-text {

    color:
        #91a3ba !important;

    font-size:
        11px;

    line-height:
        1.9;
}


.team-text a {

    color:
        #60a5fa !important;
}


.footer-text {

    text-align:
        center;

    color:
        #6f829a;

    font-size:
        11px;

    margin-top:
        20px;
}


/* ============================================================
   PREDICTION PAGE HEADER
   ============================================================ */

.page-header {

    background:

        linear-gradient(
            135deg,
            #102544,
            #122e51
        );

    border-radius:
        20px;

    padding:
        22px 25px;

    color:
        white;

    margin-bottom:
        18px;

    box-shadow:
        0 12px 30px
        rgba(0,0,0,.30);
}


.page-header-title {

    font-size:
        27px;

    font-weight:
        900;

    margin:
        0;
}


.page-header-sub {

    color:
        #a9c7e8;

    font-size:
        12px;

    margin-top:
        5px;
}


/* ============================================================
   LOCATION
   ============================================================ */

.location-card {

    background:

        linear-gradient(
            135deg,
            #0d2132,
            #0b2419
        );

    border:
        1px solid #27516c;

    border-radius:
        16px;

    padding:
        15px 18px;

    margin:
        8px 0 20px 0;
}


.location-heading {

    color:
        #dcecff;

    font-size:
        15px;

    font-weight:
        900;

    margin-bottom:
        9px;
}


.location-line {

    color:
        #9bb0c8 !important;

    font-size:
        12px;

    line-height:
        1.7;
}


/* ============================================================
   MODE TITLE
   ============================================================ */

.mode-title {

    color:
        #dce9f9;

    font-size:
        20px;

    font-weight:
        900;

    margin:
        22px 0 12px 0;
}


/* ============================================================
   IO CARDS
   ============================================================ */

.io-card {

    background:

        linear-gradient(
            145deg,
            #0d192b,
            #091321
        );

    border:
        1px solid #263a55;

    border-radius:
        17px;

    padding:
        14px;

    min-height:
        0 !important;

    height:
        auto !important;

    box-shadow:
        0 8px 23px
        rgba(0,0,0,.22);

    overflow:
        hidden;
}


.io-card-title {

    color:
        #dcecff !important;

    font-size:
        15px;

    font-weight:
        900;

    margin-bottom:
        7px;
}


.io-description {

    color:
        #8fa3bb !important;

    font-size:
        11px;

    font-weight:
        600;

    margin-bottom:
        8px;
}


/* ============================================================
   EMPTY MESSAGE
   ============================================================ */

.empty-message {

    min-height:
        120px;

    display:
        flex;

    align-items:
        center;

    justify-content:
        center;

    text-align:
        center;

    color:
        #8ea2ba !important;

    background:
        #08111e;

    border:
        1px dashed #314964;

    border-radius:
        12px;

    padding:
        15px;

    font-size:
        12px;

    font-weight:
        700;
}


/* ============================================================
   FILE UPLOADER
   ============================================================ */

div[data-testid="stFileUploader"] {

    color:
        #d7e4f3 !important;
}


div[data-testid="stFileUploader"] label {

    color:
        #cbd9ea !important;

    font-weight:
        700 !important;
}


div[data-testid="stFileUploaderDropzone"] {

    background:
        #08111e !important;

    border:
        1px dashed #314964 !important;

    border-radius:
        11px !important;

    padding:
        10px !important;
}


div[data-testid="stFileUploaderDropzoneInstructions"] {

    color:
        #a1b2c7 !important;
}


div[data-testid="stFileUploaderDropzoneInstructions"] span {

    color:
        #a1b2c7 !important;
}


div[data-testid="stFileUploaderDropzoneInstructions"] small {

    color:
        #71869f !important;
}


div[data-testid="stFileUploaderDropzone"] button {

    color:
        #ffffff !important;

    background:
        #173b6c !important;

    border:
        none !important;
}


/* ============================================================
   PREVIEW
   ============================================================ */

.preview-box {

    background:
        #08111e;

    border:
        1px solid #263a55;

    border-radius:
        12px;

    padding:
        7px;

    text-align:
        center;

    margin-top:
        5px;
}


.preview-label {

    color:
        #91a4bb !important;

    font-size:
        11px;

    font-weight:
        700;

    margin-bottom:
        5px;
}


/* ============================================================
   BUTTONS
   ============================================================ */

div.stButton > button {

    width:
        100%;

    border-radius:
        10px !important;

    min-height:
        42px;

    font-weight:
        800 !important;

    border:
        1px solid #314964 !important;

    color:
        #cfe0f2 !important;

    background:
        #0c1828 !important;

    transition:
        all .2s ease;
}


div.stButton > button:hover {

    border-color:
        #3b82f6 !important;

    color:
        #ffffff !important;

    background:
        #10243c !important;

    box-shadow:
        0 5px 17px
        rgba(59,130,246,.16);
}


/* ============================================================
   PRIMARY BUTTON
   ============================================================ */

.primary-btn div.stButton > button {

    background:

        linear-gradient(
            135deg,
            #176b45,
            #155e75
        ) !important;

    color:
        #ffffff !important;

    border:
        none !important;

    box-shadow:
        0 8px 22px
        rgba(34,197,94,.13);
}


/* ============================================================
   VISIBLE STATUS
   ============================================================ */

.success-visible {

    background:
        rgba(22,163,74,.12) !important;

    border:
        1.5px solid #22c55e !important;

    border-radius:
        10px !important;

    padding:
        10px 12px !important;

    margin-top:
        9px !important;

    color:
        #86efac !important;

    font-size:
        12px !important;

    font-weight:
        800 !important;
}


.waiting-visible {

    background:
        rgba(37,99,235,.10);

    border:
        1px solid #315d91;

    border-radius:
        10px;

    padding:
        10px;

    color:
        #9fc3f1;

    font-size:
        11px;

    font-weight:
        700;

    text-align:
        center;
}


/* ============================================================
   OUTPUT
   ============================================================ */

.output-result {

    margin-top:
        10px;

    background:
        #08111e;

    border:
        1px solid #263a55;

    border-radius:
        13px;

    padding:
        9px;
}


.output-result-title {

    color:
        #cfe0f3 !important;

    font-size:
        12px;

    font-weight:
        900;

    margin-bottom:
        7px;
}


/* ============================================================
   STATUS OVERFLOW
   ============================================================ */

.status-overflow {

    background:
        rgba(127,29,29,.18) !important;

    border:
        2px solid #ef4444 !important;

    border-radius:
        12px;

    padding:
        11px;

    color:
        #fca5a5 !important;

    font-size:
        11px;

    line-height:
        1.7;

    margin-top:
        9px;
}


.status-normal {

    background:
        rgba(21,128,61,.15) !important;

    border:
        2px solid #22c55e !important;

    border-radius:
        12px;

    padding:
        11px;

    color:
        #86efac !important;

    font-size:
        11px;

    line-height:
        1.7;

    margin-top:
        9px;
}


.status-no-detection {

    background:
        rgba(154,52,18,.14) !important;

    border:
        2px solid #fb923c !important;

    border-radius:
        12px;

    padding:
        11px;

    color:
        #fdba74 !important;

    font-size:
        11px;

    font-weight:
        700;

    margin-top:
        9px;
}


.status-title {

    font-size:
        14px;

    font-weight:
        900;

    margin-bottom:
        5px;
}


/* ============================================================
   DETAILS
   ============================================================ */

.details-card {

    background:
        #0b1626 !important;

    border:
        1px solid #263a55 !important;

    border-radius:
        11px;

    padding:
        10px 12px;

    margin-top:
        9px;
}


.details-title {

    color:
        #cfe0f3 !important;

    font-size:
        12px;

    font-weight:
        900;

    margin-bottom:
        5px;
}


.detail-row {

    color:
        #91a4bb !important;

    font-size:
        11px;

    padding:
        5px 0;

    border-bottom:
        1px solid #1c2b3e;
}


.detail-row:last-child {

    border-bottom:
        none;
}


/* ============================================================
   EMAIL SUCCESS
   ============================================================ */

.email-success {

    background:
        rgba(22,163,74,.12) !important;

    border:
        2px solid #22c55e !important;

    border-radius:
        11px;

    padding:
        10px;

    text-align:
        center;

    margin-top:
        9px;
}


.email-success-title {

    color:
        #86efac !important;

    font-size:
        12px;

    font-weight:
        900;
}


.email-success-text {

    color:
        #6ee7b7 !important;

    font-size:
        10px;

    font-weight:
        700;

    margin-top:
        3px;
}


/* ============================================================
   VIDEO
   ============================================================ */

.video-result-box {

    background:
        #08111e;

    border:
        1px solid #263a55;

    border-radius:
        12px;

    padding:
        8px;

    margin-top:
        8px;
}


/* ============================================================
   MEDIA
   ============================================================ */

[data-testid="stImage"] {

    border-radius:
        10px;

    overflow:
        hidden;
}


[data-testid="stVideo"] {

    border-radius:
        10px;

    overflow:
        hidden;
}


/* ============================================================
   PROGRESS
   ============================================================ */

.stProgress > div > div > div > div {

    background:
        #3b82f6;
}


/* ============================================================
   CAMERA
   ============================================================ */

div[data-testid="stCameraInput"] {

    border-radius:
        12px;
}


/* ============================================================
   MOBILE
   ============================================================ */

@media (max-width: 900px) {

    .hero-title {
        font-size: 25px;
    }

    .hero-card-new {
        min-height: auto;
        padding: 32px 25px 25px 25px;
    }

    .description-card {
        min-height: auto;
    }

    .hero-career-new {
        font-size: 27px;
    }

    .hero-project-area {
        margin-top: 30px;
    }

    .hero-project-name-new {
        font-size: 21px;
    }

    .hero-project-subtitle {
        white-space: normal;
    }

    .hero-logo-container {
        width: 80px;
        height: 80px;
    }

    .hero-project-logo {
        width: 74px;
        height: 74px;
    }

    .io-card {
        margin-bottom: 12px;
    }
}

</style>
""",
    unsafe_allow_html=True
)


# ============================================================
# HELPERS
# ============================================================

def show_logo(width=72):

    logo_path = os.path.join(
        os.path.dirname(__file__),
        "logo.png"
    )

    if os.path.exists(logo_path):

        st.image(
            logo_path,
            width=width
        )


# ============================================================
# LOAD MODEL
# ============================================================

@st.cache_resource
def load_model():

    model_path = os.path.join(
        os.path.dirname(__file__),
        "best.pt"
    )

    if not os.path.exists(model_path):

        raise FileNotFoundError(
            "best.pt file not found in the same folder as app.py"
        )

    return YOLO(model_path)


# ============================================================
# REVERSE GEOCODING
# ============================================================

@st.cache_data(ttl=300)
def reverse_geocode(
    latitude,
    longitude
):

    try:

        response = requests.get(
            "https://nominatim.openstreetmap.org/reverse",

            params={
                "lat": latitude,
                "lon": longitude,
                "format": "jsonv2",
                "addressdetails": 1,
                "zoom": 18,
                "accept-language": "en",
            },

            headers={
                "User-Agent":
                "EcoBin-AI-Garbage-Overflow-Detection/1.0"
            },

            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        address = data.get(
            "address",
            {}
        )

        area = (

            address.get("suburb")

            or address.get("neighbourhood")

            or address.get("village")

            or address.get("town")

            or address.get("city")

            or address.get("municipality")
        )

        city = (

            address.get("city")

            or address.get("town")

            or address.get("village")

            or address.get("municipality")
        )

        state = address.get(
            "state",
            ""
        )

        postcode = address.get(
            "postcode",
            ""
        )

        parts = []

        if area:
            parts.append(area)

        if city and city != area:
            parts.append(city)

        if state:
            parts.append(state)

        if postcode:
            parts.append(postcode)

        return (

            ", ".join(parts)

            if parts

            else data.get(
                "display_name",
                "Area name unavailable"
            )
        )

    except Exception:

        return "Area name unavailable"


# ============================================================
# LIVE LOCATION
# ============================================================

def get_live_location():

    location = streamlit_geolocation()

    if not location:
        return

    latitude = location.get(
        "latitude"
    )

    longitude = location.get(
        "longitude"
    )

    accuracy = location.get(
        "accuracy"
    )

    if latitude is None or longitude is None:
        return

    try:

        latitude = float(latitude)

        longitude = float(longitude)

        st.session_state.live_latitude = latitude

        st.session_state.live_longitude = longitude

        st.session_state.live_accuracy = accuracy

        st.session_state.live_area = reverse_geocode(
            latitude,
            longitude
        )

        st.session_state.location_loaded = True

    except Exception:

        st.session_state.location_loaded = False


def get_location():

    area = st.session_state.live_area

    latitude = st.session_state.live_latitude

    longitude = st.session_state.live_longitude

    if (
        area
        and latitude is not None
        and longitude is not None
    ):

        return (
            f"{area}\n"
            f"Latitude: {latitude:.6f}\n"
            f"Longitude: {longitude:.6f}"
        )

    return "Live location not available"


def get_map_url():

    latitude = st.session_state.live_latitude

    longitude = st.session_state.live_longitude

    if latitude is None or longitude is None:

        return None

    return (
        "https://www.google.com/maps/search/?api=1"
        f"&query={latitude},{longitude}"
    )


def get_current_time():

    return datetime.now(
        ZoneInfo("Asia/Kolkata")
    ).strftime(
        "%d-%b-%Y %I:%M:%S %p"
    )


# ============================================================
# DISPLAY LOCATION
# ============================================================

def display_live_location():

    st.markdown(
        """
<div class="location-card">

<div class="location-heading">
📍 Live Location
</div>
""",
        unsafe_allow_html=True
    )

    get_live_location()

    if st.session_state.location_loaded:

        area = st.session_state.live_area

        latitude = st.session_state.live_latitude

        longitude = st.session_state.live_longitude

        accuracy = st.session_state.live_accuracy

        accuracy_text = "Available"

        if accuracy is not None:

            try:

                accuracy_text = (
                    f"{float(accuracy):.1f} meters"
                )

            except Exception:

                accuracy_text = str(
                    accuracy
                )

        st.markdown(
            f"""
<div class="location-line">

<b>Current Area:</b>
{area}
<br>

<b>Latitude:</b>
{latitude:.6f}
&nbsp;&nbsp;

<b>Longitude:</b>
{longitude:.6f}

<br>

<b>GPS Accuracy:</b>
{accuracy_text}

<br>

<b>Location Time:</b>
{get_current_time()}

</div>
""",
            unsafe_allow_html=True
        )

        map_url = get_map_url()

        if map_url:

            st.link_button(
                "🗺️ Open Live Location in Google Maps",
                map_url,
                use_container_width=True
            )

    else:

        st.markdown(
            """
<div class="location-line">

📍 Allow browser location permission to load your live area.

</div>
""",
            unsafe_allow_html=True
        )

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


# ============================================================
# EMAIL ALERT
# ============================================================

def send_email_alert():

    try:

        sender_email = st.secrets[
            "EMAIL_SENDER"
        ]

        sender_password = st.secrets[
            "EMAIL_PASSWORD"
        ]

        receiver_email = st.secrets[
            "EMAIL_RECEIVER"
        ]

        message = EmailMessage()

        message["Subject"] = (
            "EcoBin AI - Garbage Overflow Alert"
        )

        message["From"] = sender_email

        message["To"] = receiver_email

        message.set_content(
            f"""
GARBAGE OVERFLOW DETECTED!

EcoBin AI
Smart Garbage Overflow Detection System

Live Location:
{get_location()}

Google Maps:
{get_map_url() or "Location unavailable"}

Date & Time:
{get_current_time()}

Status:
Violation Detected

Detection Class:
Overflow

This alert was automatically generated by EcoBin AI.
"""
        )

        with smtplib.SMTP(
            "smtp.gmail.com",
            587
        ) as server:

            server.starttls()

            server.login(
                sender_email,
                sender_password
            )

            server.send_message(
                message
            )

        return True

    except Exception as e:

        st.error(
            f"❌ Email alert failed: {e}"
        )

        return False


# ============================================================
# ALERT COOLDOWN - 5 MINUTES
# ============================================================

def generate_alert():

    current_dt = datetime.now(
        ZoneInfo("Asia/Kolkata")
    )

    previous = (
        st.session_state.last_alert_time
    )

    # 5 MINUTE = 300 SECONDS

    if previous is not None:

        difference = (
            current_dt - previous
        ).total_seconds()

        if difference < 300:

            return

    if send_email_alert():

        st.session_state.last_alert_time = current_dt

        st.markdown(
            """
<div class="email-success">

<div class="email-success-title">
📧 ALERT EMAIL SENT SUCCESSFULLY
</div>

<div class="email-success-text">
Garbage overflow alert sent to the configured email address.
</div>

</div>
""",
            unsafe_allow_html=True
        )


# ============================================================
# CLASS HELPERS
# ============================================================

def normalize_class_name(name):

    return (
        str(name)
        .lower()
        .strip()
        .replace("_", " ")
        .replace("-", " ")
    )


def extract_detections(result):

    detections = []

    if result.boxes is None:

        return detections

    for box in result.boxes:

        class_id = int(
            box.cls[0]
        )

        confidence = float(
            box.conf[0]
        )

        class_name = normalize_class_name(
            result.names[class_id]
        )

        detections.append(
            {
                "class": class_name,
                "confidence": confidence
            }
        )

    return detections


# ============================================================
# FINAL PREDICTION
# ============================================================

def get_final_prediction(
    detections
):

    overflow_detections = [

        d for d in detections

        if d["class"] in [

            "overflow",
            "overclass",
            "garbage overflow",
            "overflowing",
            "overflowed"

        ]

        and d["confidence"] >= 0.30
    ]

    normal_detections = [

        d for d in detections

        if d["class"] in [

            "normal",
            "normal bin",
            "non overflow",
            "non-overflow"

        ]
    ]

    if overflow_detections:

        best = max(
            overflow_detections,
            key=lambda x: x["confidence"]
        )

        return (
            "GARBAGE OVERFLOW",
            best["confidence"]
        )

    if normal_detections:

        best = max(
            normal_detections,
            key=lambda x: x["confidence"]
        )

        return (
            "NORMAL",
            best["confidence"]
        )

    return (
        "NO CLEAR DETECTION",
        0.0
    )


# ============================================================
# IMAGE PREDICTION
# ============================================================

def predict_image(
    image,
    model
):

    image_np = np.array(
        image
    )

    results = model.predict(
        source=image_np,
        conf=0.20,
        verbose=False
    )

    result = results[0]

    detections = extract_detections(
        result
    )

    return result, detections


# ============================================================
# SAFE IMAGE DISPLAY
# ============================================================

def display_result_image(result):

    try:

        annotated = result.plot()

        if annotated is not None:

            annotated = cv2.cvtColor(
                annotated,
                cv2.COLOR_BGR2RGB
            )

        st.image(
            annotated,
            use_container_width=True
        )

    except Exception:

        try:

            annotated = result.plot()

            st.image(
                annotated,
                use_container_width=True
            )

        except Exception as e:

            st.error(
                f"Unable to display detection output: {e}"
            )


# ============================================================
# OUTPUT RESULT
# ============================================================

def show_output_result(
    result,
    detections,
    title="AI Prediction"
):

    st.markdown(
        f"""
<div class="output-result">

<div class="output-result-title">
🎯 {title}
</div>
""",
        unsafe_allow_html=True
    )

    display_result_image(
        result
    )

    status, confidence = get_final_prediction(
        detections
    )

    if status == "GARBAGE OVERFLOW":

        st.markdown(
            f"""
<div class="status-overflow">

<div class="status-title">
🚨 Garbage Overflow Detected
</div>

<b>Detection:</b>
Overflow
<br>

<b>Confidence:</b>
{confidence * 100:.2f}%
<br>

<b>Location:</b>
{get_location().replace(chr(10), " | ")}
<br>

<b>Date & Time:</b>
{get_current_time()}
<br>

<b>Status:</b>
Violation Detected

</div>
""",
            unsafe_allow_html=True
        )

        generate_alert()

    elif status == "NORMAL":

        st.markdown(
            f"""
<div class="status-normal">

<div class="status-title">
✅ No Garbage Overflow Detected
</div>

<b>Detection:</b>
Normal
<br>

<b>Confidence:</b>
{confidence * 100:.2f}%
<br>

<b>Location:</b>
{get_location().replace(chr(10), " | ")}
<br>

<b>Date & Time:</b>
{get_current_time()}
<br>

<b>Status:</b>
Normal

</div>
""",
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            """
<div class="status-no-detection">

⚠️ No clear garbage condition detected.
<br>
Please try another image.

</div>
""",
            unsafe_allow_html=True
        )

    if detections:

        st.markdown(
            """
<div class="details-card">

<div class="details-title">
📊 Detection Details
</div>
""",
            unsafe_allow_html=True
        )

        for detection in detections:

            st.markdown(
                f"""
<div class="detail-row">

<b>
{detection["class"].title()}
</b>

&nbsp; — &nbsp;

{detection["confidence"] * 100:.2f}%
confidence

</div>
""",
                unsafe_allow_html=True
            )

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


# ============================================================
# VIDEO PROCESSING
# ============================================================

def process_video(
    video_path,
    model
):

    cap = cv2.VideoCapture(
        video_path
    )

    if not cap.isOpened():

        return (
            "NO CLEAR DETECTION",
            None,
            0.0
        )

    fps = cap.get(
        cv2.CAP_PROP_FPS
    )

    if fps <= 0:

        fps = 25

    width = int(
        cap.get(
            cv2.CAP_PROP_FRAME_WIDTH
        )
    )

    height = int(
        cap.get(
            cv2.CAP_PROP_FRAME_HEIGHT
        )
    )

    total_frames = int(
        cap.get(
            cv2.CAP_PROP_FRAME_COUNT
        )
    )

    raw_output = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".mp4"
    )

    raw_output_path = raw_output.name

    raw_output.close()

    h264_output = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".mp4"
    )

    h264_output_path = h264_output.name

    h264_output.close()

    writer = cv2.VideoWriter(
        raw_output_path,
        cv2.VideoWriter_fourcc(
            *"mp4v"
        ),
        fps,
        (width, height)
    )

    frame_number = 0

    overflow_count = 0

    normal_count = 0

    detection_count = 0

    best_overflow_confidence = 0.0

    progress = st.progress(0)

    while True:

        ret, frame = cap.read()

        if not ret:

            break

        results = model.predict(
            source=frame,
            conf=0.20,
            verbose=False
        )

        result = results[0]

        detections = extract_detections(
            result
        )

        status, confidence = get_final_prediction(
            detections
        )

        if status == "GARBAGE OVERFLOW":

            overflow_count += 1

            detection_count += 1

            best_overflow_confidence = max(
                best_overflow_confidence,
                confidence
            )

        elif status == "NORMAL":

            normal_count += 1

            detection_count += 1

        annotated_frame = result.plot()

        if status == "GARBAGE OVERFLOW":

            label = (
                "GARBAGE OVERFLOW DETECTED"
            )

        elif status == "NORMAL":

            label = "NORMAL"

        else:

            label = (
                "NO CLEAR DETECTION"
            )

        cv2.rectangle(
            annotated_frame,
            (10, 10),
            (560, 72),
            (25, 55, 95),
            -1
        )

        cv2.putText(
            annotated_frame,
            label,
            (25, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.72,
            (255, 255, 255),
            2,
            cv2.LINE_AA
        )

        if confidence > 0:

            cv2.putText(
                annotated_frame,
                f"Confidence: {confidence * 100:.2f}%",
                (15, height - 18),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.62,
                (255, 255, 255),
                2,
                cv2.LINE_AA
            )

        writer.write(
            annotated_frame
        )

        frame_number += 1

        if total_frames > 0:

            progress.progress(
                min(
                    frame_number / total_frames,
                    1.0
                )
            )

    cap.release()

    writer.release()

    progress.empty()


    # ========================================================
    # FFMPEG
    # ========================================================

    try:

        ffmpeg_path = (
            imageio_ffmpeg.get_ffmpeg_exe()
        )

        command = [

            ffmpeg_path,

            "-y",

            "-i",
            raw_output_path,

            "-c:v",
            "libx264",

            "-preset",
            "fast",

            "-crf",
            "23",

            "-pix_fmt",
            "yuv420p",

            "-movflags",
            "+faststart",

            h264_output_path
        ]

        subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )

        final_video_path = (
            h264_output_path
        )

    except Exception:

        final_video_path = (
            raw_output_path
        )

    try:

        with open(
            final_video_path,
            "rb"
        ) as video_file:

            output_video_bytes = (
                video_file.read()
            )

    except Exception:

        output_video_bytes = None


    # ========================================================
    # CLEAN TEMP FILES
    # ========================================================

    for path in [
        raw_output_path,
        h264_output_path
    ]:

        try:

            if os.path.exists(path):

                os.remove(path)

        except Exception:

            pass


    # ========================================================
    # FINAL VIDEO RESULT
    # ========================================================

    if detection_count == 0:

        return (
            "NO CLEAR DETECTION",
            output_video_bytes,
            0.0
        )

    if overflow_count > 0:

        return (
            "GARBAGE OVERFLOW",
            output_video_bytes,
            best_overflow_confidence
        )

    return (
        "NORMAL",
        output_video_bytes,
        0.0
    )


# ============================================================
# UI HELPERS
# ============================================================

def empty_box(message):

    st.markdown(
        f"""
<div class="empty-message">
{message}
</div>
""",
        unsafe_allow_html=True
    )


def section_title(
    icon,
    title
):

    st.markdown(
        f"""
<div class="mode-title">
{icon} {title}
</div>
""",
        unsafe_allow_html=True
    )


def visible_success(message):

    st.markdown(
        f"""
<div class="success-visible">
✅ {message}
</div>
""",
        unsafe_allow_html=True
    )


# ============================================================
# HOME PAGE
# ============================================================

if st.session_state.page == "home":

    # ========================================================
    # TITLE
    # ========================================================

    st.markdown(
        '<div class="hero-title">♻️ EcoBin AI</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
<div class="hero-subtitle">
Smart Garbage Overflow Detection using Artificial Intelligence
</div>
""",
        unsafe_allow_html=True
    )


    # ========================================================
    # HERO + DESCRIPTION
    # ========================================================

    hero_left, hero_right = st.columns(
        [1, 1.25],
        gap="large"
    )


    # ========================================================
    # LEFT HERO
    # ========================================================

    with hero_left:

        logo_path = os.path.join(
            os.path.dirname(__file__),
            "logo.png"
        )

        logo_html = ""

        if os.path.exists(
            logo_path
        ):

            try:

                with open(
                    logo_path,
                    "rb"
                ) as image_file:

                    encoded_logo = (
                        base64.b64encode(
                            image_file.read()
                        ).decode()
                    )

                logo_html = f"""
<img
    src="data:image/png;base64,{encoded_logo}"
    class="hero-project-logo"
/>
"""

            except Exception:

                logo_html = ""


        # ----------------------------------------------------
        # SINGLE HERO CARD
        # ----------------------------------------------------

        st.markdown(
            f"""
<div class="hero-card-new">

    <div class="hero-top-content">

        <div class="program-pill">
            🎓 AICW PROGRAM
        </div>

        <div class="hero-career-new">
            👩🏻‍💻 AI Career for Women
        </div>

        <div class="hero-capstone-new">
            Capstone Project
        </div>

    </div>


    <div class="hero-project-area">

        <div class="hero-project-info">

            <div class="hero-project-name-new">
                ♻️ EcoBin-AI
            </div>

            <div class="hero-project-subtitle">
                📧 Intelligent Safety • Real-Time Detection
            </div>

        </div>


        <div class="hero-logo-container">

            {logo_html}

        </div>

    </div>

</div>
""",
            unsafe_allow_html=True
        )


    # ========================================================
    # RIGHT DESCRIPTION
    # ========================================================

    with hero_right:

        st.markdown(
            """
<div class="description-card">

<div class="description-heading">
🌱 Project Description
</div>

<p>
EcoBin AI is an AI-powered Smart Garbage Overflow Detection System
designed to automatically identify overflowing garbage bins using
computer vision and YOLOv8 object detection.
</p>

<p>
The system analyzes images, camera-captured photos, and CCTV/video
files to identify garbage overflow conditions.
</p>

<p>
The trained YOLOv8 model classifies the detected garbage condition
into two classes: <b>Normal</b> and <b>Overflow</b>.
</p>

<p>
When an overflow condition is detected, EcoBin AI automatically
generates an alert containing the live location, date and time,
and violation status. The alert is also sent to the configured
user's email address.
</p>

</div>
""",
            unsafe_allow_html=True
        )


    # ========================================================
    # SYSTEM CAPABILITIES
    # ========================================================

    st.markdown(
        '<div class="section-title">⚡ System Capabilities</div>',
        unsafe_allow_html=True
    )


    caps = [

        (
            "🖼️",
            "Image Detection",
            "Analyze uploaded garbage images"
        ),

        (
            "📷",
            "Camera Detection",
            "Capture and detect using camera"
        ),

        (
            "🎥",
            "CCTV Analysis",
            "Process recorded video footage"
        ),

        (
            "🚨",
            "Smart Alerts",
            "Location and email notification"
        ),
    ]


    cap_cols = st.columns(
        4,
        gap="medium"
    )


    for col, (
        icon,
        title,
        text
    ) in zip(
        cap_cols,
        caps
    ):

        with col:

            st.markdown(
                f"""
<div class="capability-card">

<div class="capability-icon">
{icon}
</div>

<div class="capability-title">
{title}
</div>

<div class="capability-text">
{text}
</div>

</div>
""",
                unsafe_allow_html=True
            )


    # ========================================================
    # START BUTTON
    # ========================================================

    st.markdown(
        '<div style="height:10px"></div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="primary-btn">',
        unsafe_allow_html=True
    )


    if st.button(
        "🔎  START AI DETECTION",
        key="start_detection",
        use_container_width=True
    ):

        st.session_state.page = "predict"

        st.rerun()


    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


    # ========================================================
    # PROJECT TEAM
    # ========================================================

    st.markdown(
        '<div class="section-title">👥 Project Team</div>',
        unsafe_allow_html=True
    )


    team_col, mail_col, guide_col = st.columns(
        [1.25, 1.25, .85],
        gap="medium"
    )


    # --------------------------------------------------------
    # TEAM MEMBERS
    # --------------------------------------------------------

    with team_col:

        st.markdown(
            """
<div class="team-card">

<div class="team-heading">
TEAM MEMBERS
</div>

<div class="team-text">

1. K.Lalitha Devi<br>
2. Y.Haasini<br>
3. G.Sri Divya<br>
4. N.Sushma sri

</div>

</div>
""",
            unsafe_allow_html=True
        )


    # --------------------------------------------------------
    # GMAIL
    # --------------------------------------------------------

    with mail_col:

        st.markdown(
            """
<div class="team-card">

<div class="team-heading">
GMAIL
</div>

<div class="team-text">

<a href="mailto:lalithadevi825@gmail.com">
lalithadevi825@gmail.com
</a>
<br>

<a href="mailto:haasiniyanamadala@gmail.com">
haasiniyanamadala@gmail.com
</a>
<br>

<a href="mailto:galidivya534@gmail.com">
galidivya534@gmail.com
</a>
<br>

<a href="mailto:nadimpallisushmasri29@gmail.com">
nadimpallisushmasri29@gmail.com
</a>

</div>

</div>
""",
            unsafe_allow_html=True
        )


    # --------------------------------------------------------
    # GUIDE
    # --------------------------------------------------------

    with guide_col:

        st.markdown(
            """
<div class="team-card">

<div class="team-heading">
GUIDE NAME
</div>

<div class="team-text">

<b>
MD. Abdul Aziz
</b>

<br><br>

Trainer, Co-Lead-AICW

</div>

</div>
""",
            unsafe_allow_html=True
        )


    # ========================================================
    # FOOTER
    # ========================================================

    st.markdown(
        """
<div class="footer-text">
EcoBin AI • Smart Garbage Overflow Detection
</div>
""",
        unsafe_allow_html=True
    )


# ============================================================
# PREDICTION PAGE
# ============================================================

else:

    # ========================================================
    # HEADER
    # ========================================================

    top_left, top_right = st.columns(
        [.2, 1],
        gap="medium"
    )


    with top_left:

        if st.button(
            "← Home",
            key="back_home"
        ):

            st.session_state.page = "home"

            st.rerun()


    with top_right:

        st.markdown(
            """
<div class="page-header">

<div class="page-header-title">
♻️ EcoBin AI Overflow Detection
</div>

<div class="page-header-sub">
AI-powered image, camera and CCTV garbage overflow analysis
</div>

</div>
""",
            unsafe_allow_html=True
        )


    # ========================================================
    # LOCATION
    # ========================================================

    display_live_location()


    # ========================================================
    # MODEL
    # ========================================================

    try:

        model = load_model()

    except Exception as e:

        st.error(
            f"❌ best.pt model load avvaledu: {e}"
        )

        st.info(
            "Make sure best.pt is in the same folder as app.py."
        )

        st.stop()


    # ========================================================
    # IMAGE DETECTION
    # ========================================================

    section_title(
        "🖼️",
        "Image Detection"
    )


    image_upload_col, image_input_col, image_output_col = st.columns(
        3,
        gap="medium"
    )


    input_image = None


    # ========================================================
    # IMAGE UPLOAD
    # ========================================================

    with image_upload_col:

        st.markdown(
            """
<div class="io-card">

<div class="io-card-title">
📤 Upload
</div>

<div class="io-description">
Upload a garbage image for AI analysis
</div>
""",
            unsafe_allow_html=True
        )


        uploaded_image = st.file_uploader(
            "Choose image",
            type=[
                "jpg",
                "jpeg",
                "png"
            ],
            key="image_upload",
            label_visibility="collapsed"
        )


        if uploaded_image:

            visible_success(
                "Image uploaded successfully"
            )

        else:

            st.markdown(
                """
<div class="waiting-visible">
📤 Select an image to start detection
</div>
""",
                unsafe_allow_html=True
            )


        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )


    # ========================================================
    # IMAGE INPUT
    # ========================================================

    with image_input_col:

        st.markdown(
            """
<div class="io-card">

<div class="io-card-title">
🖼️ Input
</div>

<div class="io-description">
Selected image preview
</div>
""",
            unsafe_allow_html=True
        )


        if uploaded_image:

            try:

                input_image = Image.open(
                    uploaded_image
                ).convert("RGB")

                st.image(
                    input_image,
                    use_container_width=True
                )

            except Exception as e:

                st.error(
                    f"Image preview error: {e}"
                )

        else:

            empty_box(
                "Your selected image will appear here."
            )


        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )


    # ========================================================
    # IMAGE OUTPUT
    # ========================================================

    with image_output_col:

        st.markdown(
            """
<div class="io-card">

<div class="io-card-title">
🎯 Output
</div>

<div class="io-description">
AI detection result
</div>
""",
            unsafe_allow_html=True
        )


        if uploaded_image and input_image is not None:

            if st.button(
                "🔍  Detect Image",
                key="detect_image",
                use_container_width=True
            ):

                with st.spinner(
                    "🤖 AI is analyzing the image..."
                ):

                    try:

                        result, detections = predict_image(
                            input_image,
                            model
                        )

                        st.session_state.image_result = (
                            result,
                            detections
                        )

                    except Exception as e:

                        st.error(
                            f"❌ Image detection failed: {e}"
                        )


            if st.session_state.image_result is not None:

                result, detections = (
                    st.session_state.image_result
                )

                show_output_result(
                    result,
                    detections,
                    "Image Prediction"
                )

            else:

                st.markdown(
                    """
<div class="waiting-visible">
🔍 Click "Detect Image" to generate AI output
</div>
""",
                    unsafe_allow_html=True
                )

        else:

            empty_box(
                "AI prediction output will appear here."
            )


        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )


    # ========================================================
    # CAMERA DETECTION
    # ========================================================

    section_title(
        "📷",
        "Camera Detection"
    )


    camera_col, camera_input_col, camera_output_col = st.columns(
        3,
        gap="medium"
    )


    camera_pil = None


    # ========================================================
    # CAMERA
    # ========================================================

    with camera_col:

        st.markdown(
            """
<div class="io-card">

<div class="io-card-title">
📷 Camera
</div>

<div class="io-description">
Capture a garbage-bin image
</div>
""",
            unsafe_allow_html=True
        )


        camera_image = st.camera_input(
            "Capture image",
            key="camera",
            label_visibility="collapsed"
        )


        if not camera_image:

            st.markdown(
                """
<div class="waiting-visible">
📷 Camera preview will appear here
</div>
""",
                unsafe_allow_html=True
            )


        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )


    # ========================================================
    # CAMERA INPUT
    # ========================================================

    with camera_input_col:

        st.markdown(
            """
<div class="io-card">

<div class="io-card-title">
🖼️ Input
</div>

<div class="io-description">
Captured image preview
</div>
""",
            unsafe_allow_html=True
        )


        if camera_image:

            try:

                camera_pil = Image.open(
                    camera_image
                ).convert("RGB")

                st.image(
                    camera_pil,
                    use_container_width=True
                )

            except Exception as e:

                st.error(
                    f"Camera preview error: {e}"
                )

        else:

            empty_box(
                "Captured camera image will appear here."
            )


        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )


    # ========================================================
    # CAMERA OUTPUT
    # ========================================================

    with camera_output_col:

        st.markdown(
            """
<div class="io-card">

<div class="io-card-title">
🎯 Output
</div>

<div class="io-description">
AI camera detection result
</div>
""",
            unsafe_allow_html=True
        )


        if camera_image and camera_pil is not None:

            if st.button(
                "🔍  Detect Camera Image",
                key="detect_camera",
                use_container_width=True
            ):

                with st.spinner(
                    "🤖 Analyzing camera image..."
                ):

                    try:

                        result, detections = predict_image(
                            camera_pil,
                            model
                        )

                        st.session_state.camera_result = (
                            result,
                            detections
                        )

                    except Exception as e:

                        st.error(
                            f"❌ Camera detection failed: {e}"
                        )


            if st.session_state.camera_result is not None:

                result, detections = (
                    st.session_state.camera_result
                )

                show_output_result(
                    result,
                    detections,
                    "Camera Prediction"
                )

            else:

                st.markdown(
                    """
<div class="waiting-visible">
🔍 Click "Detect Camera Image" to generate AI output
</div>
""",
                    unsafe_allow_html=True
                )

        else:

            empty_box(
                "Camera prediction output will appear here."
            )


        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )


    # ========================================================
    # CCTV / VIDEO
    # ========================================================

    section_title(
        "🎥",
        "CCTV / Video Detection"
    )


    video_upload_col, video_input_col, video_output_col = st.columns(
        3,
        gap="medium"
    )


    # ========================================================
    # VIDEO UPLOAD
    # ========================================================

    with video_upload_col:

        st.markdown(
            """
<div class="io-card">

<div class="io-card-title">
📤 Upload Video
</div>

<div class="io-description">
Upload CCTV/video footage
</div>
""",
            unsafe_allow_html=True
        )


        uploaded_video = st.file_uploader(
            "Choose CCTV video",
            type=[
                "mp4",
                "avi",
                "mov",
                "mkv",
                "mpeg"
            ],
            key="video_upload",
            label_visibility="collapsed"
        )


        if uploaded_video:

            visible_success(
                "Video uploaded successfully"
            )

        else:

            st.markdown(
                """
<div class="waiting-visible">
🎥 Select a CCTV video to analyze
</div>
""",
                unsafe_allow_html=True
            )


        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )


    # ========================================================
    # VIDEO INPUT
    # ========================================================

    with video_input_col:

        st.markdown(
            """
<div class="io-card">

<div class="io-card-title">
🎬 Input
</div>

<div class="io-description">
Uploaded CCTV video preview
</div>
""",
            unsafe_allow_html=True
        )


        if uploaded_video:

            st.video(
                uploaded_video
            )

        else:

            empty_box(
                "Uploaded CCTV/video will appear here."
            )


        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )


    # ========================================================
    # VIDEO OUTPUT
    # ========================================================

    with video_output_col:

        st.markdown(
            """
<div class="io-card">

<div class="io-card-title">
🎯 Output
</div>

<div class="io-description">
AI processed video result
</div>
""",
            unsafe_allow_html=True
        )


        if uploaded_video:

            if st.button(
                "🎥  Analyze CCTV Video",
                key="detect_video",
                use_container_width=True
            ):

                temp_video = tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".mp4"
                )

                temp_video.write(
                    uploaded_video.getvalue()
                )

                temp_video.close()


                try:

                    with st.spinner(
                        "🤖 AI is analyzing CCTV video..."
                    ):

                        video_result = process_video(
                            temp_video.name,
                            model
                        )

                    st.session_state.video_result = (
                        video_result
                    )

                except Exception as e:

                    st.error(
                        f"❌ Video processing failed: {e}"
                    )

                finally:

                    if os.path.exists(
                        temp_video.name
                    ):

                        os.remove(
                            temp_video.name
                        )


            # =================================================
            # VIDEO RESULT
            # =================================================

            if st.session_state.video_result is not None:

                (
                    video_status,
                    output_video_bytes,
                    video_conf
                ) = st.session_state.video_result


                if output_video_bytes is not None:

                    st.markdown(
                        """
<div class="video-result-box">
""",
                        unsafe_allow_html=True
                    )

                    st.video(
                        output_video_bytes
                    )

                    st.markdown(
                        "</div>",
                        unsafe_allow_html=True
                    )

                else:

                    st.error(
                        "❌ Output video could not be generated."
                    )


                # =================================================
                # VIDEO STATUS
                # =================================================

                if video_status == "GARBAGE OVERFLOW":

                    st.markdown(
                        f"""
<div class="status-overflow">

<div class="status-title">
🚨 Garbage Overflow Detected
</div>

<b>Detection:</b>
Overflow
<br>

<b>Best Confidence:</b>
{video_conf * 100:.2f}%
<br>

<b>Location:</b>
{get_location().replace(chr(10), " | ")}
<br>

<b>Date & Time:</b>
{get_current_time()}
<br>

<b>Status:</b>
Violation Detected

</div>
""",
                        unsafe_allow_html=True
                    )

                    # 5-MINUTE COOLDOWN
                    generate_alert()


                elif video_status == "NORMAL":

                    st.markdown(
                        """
<div class="status-normal">

<div class="status-title">
✅ No Garbage Overflow Detected
</div>

<b>Status:</b>
Normal

</div>
""",
                        unsafe_allow_html=True
                    )


                else:

                    st.markdown(
                        """
<div class="status-no-detection">

⚠️ No clear garbage condition
was detected in the video.

</div>
""",
                        unsafe_allow_html=True
                    )


            else:

                st.markdown(
                    """
<div class="waiting-visible">

🎥 Click "Analyze CCTV Video"
to generate AI output

</div>
""",
                    unsafe_allow_html=True
                )

        else:

            empty_box(
                "Video prediction output will appear here."
            )


        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )


    # ========================================================
    # FOOTER
    # ========================================================

    st.markdown(
        """
<div class="footer-text">
EcoBin AI • AI-Powered Smart Garbage Overflow Detection
</div>
""",
        unsafe_allow_html=True
    )
