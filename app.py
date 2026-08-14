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
import textwrap

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
# HTML HELPER
# ============================================================

def render_html(html):
    """
    Removes Python indentation from HTML so Streamlit
    doesn't display the HTML as a code block.
    """
    st.markdown(
        textwrap.dedent(html),
        unsafe_allow_html=True
    )


# ============================================================
# PREMIUM DARK UI
# ============================================================

render_html(
"""
<style>

:root {
    --bg: #050b14;
    --bg2: #08111e;
    --card: #0b1626;
    --card2: #0e1b2d;

    --green: #22c55e;
    --green2: #16a34a;

    --blue: #3b82f6;
    --purple: #7c5cff;

    --text: #f8fafc;
    --text2: #dbeafe;
    --muted: #94a3b8;

    --border: #203754;

    --danger: #ef4444;
    --warning: #fb923c;
}


.stApp {

    background:
        radial-gradient(
            circle at 8% 5%,
            rgba(34,197,94,.08),
            transparent 25%
        ),

        radial-gradient(
            circle at 90% 8%,
            rgba(59,130,246,.10),
            transparent 28%
        ),

        radial-gradient(
            circle at 50% 90%,
            rgba(124,92,255,.06),
            transparent 28%
        ),

        #050b14;

    color: var(--text);
}


.block-container {

    max-width: 1280px;

    padding:
        22px
        4%
        30px
        4%;
}


/* ============================================================
   HIDE STREAMLIT DEFAULT
   ============================================================ */

#MainMenu,
footer,
header {
    visibility: hidden;
}


.stMarkdown,
.stMarkdown p,
.stMarkdown li {
    color: var(--text);
}


/* ============================================================
   HERO TITLE
   ============================================================ */

.hero-title {

    text-align: center;

    color: #f8fafc;

    font-size: 30px;

    font-weight: 900;

    letter-spacing: -.5px;

    margin: 0;
}


.hero-subtitle {

    text-align: center;

    color: #94a3b8;

    font-size: 13px;

    margin:
        5px
        0
        22px
        0;
}


/* ============================================================
   HOME HERO CARD
   ============================================================ */

.hero-card {

    min-height: 330px;

    background:
        radial-gradient(
            circle at 95% 100%,
            rgba(34,197,94,.09),
            transparent 28%
        ),

        radial-gradient(
            circle at 10% 0%,
            rgba(59,130,246,.07),
            transparent 25%
        ),

        #0a1422;

    border:
        1px solid
        #203754;

    border-radius: 22px;

    padding:
        38px
        40px
        30px
        40px;

    box-shadow:
        0 18px 50px
        rgba(0,0,0,.35);

    position: relative;

    overflow: hidden;

    box-sizing: border-box;
}


/* TOP GRADIENT LINE */

.hero-card:before {

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
            #2f80ed,
            #7c5cff
        );
}


/* ============================================================
   HERO TOP
   ============================================================ */

.hero-top-content {

    position: relative;

    z-index: 2;
}


/* PROGRAM */

.program-pill {

    display: inline-flex;

    align-items: center;

    width: fit-content;

    padding:
        10px
        16px;

    border-radius: 999px;

    background:
        rgba(37,99,235,.10);

    color: #bfdbfe;

    border:
        1px solid
        #294b75;

    font-size: 12px;

    font-weight: 850;

    margin-bottom: 23px;
}


/* CAREER */

.hero-career-new {

    color: #f8fafc;

    font-size: 34px;

    font-weight: 900;

    line-height: 1.18;

    letter-spacing: -.8px;

    margin: 0;
}


/* CAPSTONE */

.hero-capstone-new {

    color: #94a3b8;

    font-size: 18px;

    font-weight: 750;

    margin-top: 12px;
}


/* ============================================================
   HERO PROJECT AREA
   ============================================================ */

.hero-project-area {

    display: flex;

    align-items: center;

    justify-content: space-between;

    gap: 25px;

    margin-top: 46px;

    position: relative;

    z-index: 2;
}


.hero-project-info {

    flex: 1;

    min-width: 0;
}


/* PROJECT NAME */

.hero-project-name-new {

    color: #22c55e;

    font-size: 25px;

    font-weight: 900;

    line-height: 1.2;
}


/* PROJECT SUBTITLE */

.hero-project-subtitle-new {

    color: #94a3b8;

    font-size: 13px;

    font-weight: 700;

    margin-top: 8px;
}


/* ============================================================
   HERO LOGO
   ============================================================ */

.hero-logo-container {

    width: 108px;

    height: 108px;

    flex-shrink: 0;

    display: flex;

    align-items: center;

    justify-content: center;
}


.hero-logo-inside {

    width: 100px;

    height: 100px;

    object-fit: contain;

    border-radius: 17px;

    background: #ffffff;

    padding: 5px;

    border:
        1px solid
        rgba(255,255,255,.15);

    box-shadow:
        0 10px 30px
        rgba(0,0,0,.40);
}


/* ============================================================
   DESCRIPTION CARD
   ============================================================ */

.description-card {

    min-height: 330px;

    background:
        linear-gradient(
            145deg,
            #0c1828,
            #091321
        );

    border:
        1px solid
        #203754;

    border-radius: 22px;

    padding:
        25px
        27px;

    box-shadow:
        0 18px 45px
        rgba(0,0,0,.28);

    overflow: hidden;
}


.description-heading {

    color: #e2e8f0;

    font-size: 17px;

    font-weight: 900;

    margin-bottom: 14px;
}


.description-card p {

    color: #94a3b8;

    font-size: 12px;

    line-height: 1.8;

    margin:
        0
        0
        13px
        0;
}


.description-card b {

    color: #cbd5e1;
}


/* ============================================================
   SECTION TITLE
   ============================================================ */

.section-title {

    color: #e2e8f0;

    font-size: 18px;

    font-weight: 900;

    margin:
        16px
        0
        10px
        0;
}


/* ============================================================
   CAPABILITY CARDS
   ============================================================ */

.capability-card {

    background:
        linear-gradient(
            145deg,
            #0d1a2b,
            #091422
        );

    border:
        1px solid
        #203754;

    border-radius: 16px;

    padding:
        16px
        12px;

    min-height: 110px;

    text-align: center;

    box-shadow:
        0 8px 25px
        rgba(0,0,0,.20);
}


.capability-icon {

    font-size: 21px;

    margin-bottom: 5px;
}


.capability-title {

    color: #e2e8f0;

    font-size: 13px;

    font-weight: 900;
}


.capability-text {

    color: #94a3b8;

    font-size: 10.5px;

    line-height: 1.45;

    margin-top: 5px;
}


/* ============================================================
   TEAM
   ============================================================ */

.team-card {

    background:
        linear-gradient(
            145deg,
            #0d1a2b,
            #091422
        );

    border:
        1px solid
        #203754;

    border-radius: 17px;

    padding: 19px;

    min-height: 150px;

    box-shadow:
        0 8px 25px
        rgba(0,0,0,.18);
}


.team-heading {

    color: #cbd5e1;

    font-size: 11px;

    font-weight: 900;

    letter-spacing: .3px;

    margin-bottom: 10px;
}


.team-text {

    color: #94a3b8;

    font-size: 11px;

    line-height: 1.9;
}


.team-text a {

    color: #60a5fa;

    text-decoration: none;
}


/* ============================================================
   FOOTER
   ============================================================ */

.footer-text {

    text-align: center;

    color: #64748b;

    font-size: 11px;

    margin-top: 22px;
}


/* ============================================================
   PREDICTION PAGE HEADER
   ============================================================ */

.page-header {

    background:
        linear-gradient(
            135deg,
            #10243d,
            #0c1b2e
        );

    border:
        1px solid
        #254464;

    border-radius: 20px;

    padding:
        22px
        25px;

    color: white;

    margin-bottom: 15px;

    box-shadow:
        0 12px 35px
        rgba(0,0,0,.28);
}


.page-header-title {

    font-size: 26px;

    font-weight: 900;

    margin: 0;
}


.page-header-sub {

    color: #94a3b8;

    font-size: 12px;

    margin-top: 5px;
}


/* ============================================================
   LOCATION
   ============================================================ */

.location-card {

    background:
        linear-gradient(
            135deg,
            rgba(30,64,175,.12),
            rgba(22,163,74,.08)
        );

    border:
        1px solid
        #254464;

    border-radius: 16px;

    padding:
        15px
        18px;

    margin:
        8px
        0
        17px
        0;
}


.location-heading {

    color: #dbeafe;

    font-size: 15px;

    font-weight: 900;

    margin-bottom: 9px;
}


.location-line {

    color: #94a3b8 !important;

    font-size: 12px;

    line-height: 1.7;
}


/* ============================================================
   MODE TITLE
   ============================================================ */

.mode-title {

    color: #e2e8f0;

    font-size: 19px;

    font-weight: 900;

    margin:
        23px
        0
        11px
        0;
}


/* ============================================================
   IO CARDS
   ============================================================ */

.io-card {

    background:
        linear-gradient(
            145deg,
            #0c1828,
            #091422
        );

    border:
        1px solid
        #203754;

    border-radius: 17px;

    padding: 14px;

    min-height: 0 !important;

    height: auto !important;

    box-shadow:
        0 8px 25px
        rgba(0,0,0,.22);

    overflow: hidden;
}


.io-card-title {

    color: #dbeafe !important;

    font-size: 15px;

    font-weight: 900;

    margin-bottom: 7px;
}


.io-description {

    color: #94a3b8 !important;

    font-size: 11px;

    font-weight: 600;

    margin-bottom: 8px;
}


/* ============================================================
   EMPTY MESSAGE
   ============================================================ */

.empty-message {

    min-height: 120px;

    display: flex;

    align-items: center;

    justify-content: center;

    text-align: center;

    color: #94a3b8 !important;

    background:
        #081321;

    border:
        1px dashed
        #35516f;

    border-radius: 12px;

    padding: 15px;

    font-size: 12px;

    font-weight: 700;
}


/* ============================================================
   FILE UPLOADER
   ============================================================ */

div[data-testid="stFileUploader"] {

    color: #cbd5e1 !important;
}


div[data-testid="stFileUploader"] label {

    color: #cbd5e1 !important;

    font-weight: 700 !important;
}


div[data-testid="stFileUploaderDropzone"] {

    background:
        #081321 !important;

    border:
        1px dashed
        #35516f !important;

    border-radius:
        11px !important;

    padding:
        10px !important;
}


div[data-testid="stFileUploaderDropzoneInstructions"] {

    color: #94a3b8 !important;
}


div[data-testid="stFileUploaderDropzoneInstructions"] span {

    color: #cbd5e1 !important;
}


div[data-testid="stFileUploaderDropzoneInstructions"] small {

    color: #64748b !important;
}


div[data-testid="stFileUploaderDropzone"] button {

    color: #ffffff !important;

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
        #081321;

    border:
        1px solid
        #203754;

    border-radius: 12px;

    padding: 7px;

    text-align: center;

    margin-top: 5px;
}


.preview-label {

    color: #94a3b8 !important;

    font-size: 11px;

    font-weight: 700;

    margin-bottom: 5px;
}


/* ============================================================
   BUTTONS
   ============================================================ */

div.stButton > button {

    width: 100%;

    border-radius:
        10px !important;

    min-height:
        42px;

    font-weight:
        800 !important;

    border:
        1px solid
        #294866 !important;

    color:
        #dbeafe !important;

    background:
        #0d1a2b !important;

    transition:
        all .2s ease;
}


div.stButton > button:hover {

    border-color:
        #3b82f6 !important;

    color:
        #ffffff !important;

    background:
        #10243d !important;

    box-shadow:
        0 5px 18px
        rgba(59,130,246,.18);
}


.primary-btn div.stButton > button {

    background:
        linear-gradient(
            135deg,
            #16a34a,
            #15803d
        ) !important;

    color:
        #ffffff !important;

    border:
        none !important;
}


/* ============================================================
   VISIBLE STATUS
   ============================================================ */

.success-visible {

    background:
        rgba(22,163,74,.12) !important;

    border:
        1.5px solid
        #22c55e !important;

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
        rgba(37,99,235,.10) !important;

    border:
        1px solid
        #294b75 !important;

    border-radius:
        10px !important;

    padding:
        10px !important;

    color:
        #93c5fd !important;

    font-size:
        11px !important;

    font-weight:
        700 !important;

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
        #081321;

    border:
        1px solid
        #203754;

    border-radius:
        13px;

    padding:
        9px;
}


.output-result-title {

    color:
        #dbeafe !important;

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
        2px solid
        #ef4444 !important;

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
        rgba(20,83,45,.18) !important;

    border:
        2px solid
        #22c55e !important;

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
        rgba(124,45,18,.18) !important;

    border:
        2px solid
        #fb923c !important;

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
        1px solid
        #203754 !important;

    border-radius:
        11px;

    padding:
        10px 12px;

    margin-top:
        9px;
}


.details-title {

    color:
        #dbeafe !important;

    font-size:
        12px;

    font-weight:
        900;

    margin-bottom:
        5px;
}


.detail-row {

    color:
        #94a3b8 !important;

    font-size:
        11px;

    padding:
        5px 0;

    border-bottom:
        1px solid
        #172a40;
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
        2px solid
        #22c55e !important;

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
        #4ade80 !important;

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
        #081321;

    border:
        1px solid
        #203754;

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
   STREAMLIT TEXT INPUT / SELECTED FILE
   ============================================================ */

.stFileUploader,
.stTextInput,
.stSelectbox {

    color: #e2e8f0;
}


/* ============================================================
   RESPONSIVE
   ============================================================ */

@media (max-width: 900px) {

    .hero-card {

        min-height:
            auto;

        padding:
            30px 25px 25px 25px;
    }

    .hero-career-new {

        font-size:
            27px;
    }

    .hero-project-area {

        margin-top:
            35px;
    }

    .description-card {

        margin-top:
            12px;

        min-height:
            auto;
    }
}


@media (max-width: 600px) {

    .hero-project-area {

        align-items:
            flex-start;
    }

    .hero-logo-container {

        width:
            82px;

        height:
            82px;
    }

    .hero-logo-inside {

        width:
            76px;

        height:
            76px;
    }

    .hero-project-name-new {

        font-size:
            21px;
    }

    .hero-project-subtitle-new {

        font-size:
            10px;
    }
}

</style>
"""
)


# ============================================================
# HELPERS
# ============================================================

def get_logo_base64():

    logo_path = os.path.join(
        os.path.dirname(__file__),
        "logo.png"
    )

    if not os.path.exists(logo_path):
        return None

    try:

        with open(
            logo_path,
            "rb"
        ) as f:

            return base64.b64encode(
                f.read()
            ).decode()

    except Exception:

        return None


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

    if (
        latitude is None
        or longitude is None
    ):

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

    render_html(
    """
    <div class="location-card">

    <div class="location-heading">
    📍 Live Location
    </div>
    """
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

        render_html(
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
        """
        )

        map_url = get_map_url()

        if map_url:

            st.link_button(
                "🗺️ Open Live Location in Google Maps",
                map_url,
                use_container_width=True
            )

    else:

        render_html(
        """
        <div class="location-line">
        📍 Allow browser location permission to load your live area.
        </div>
        """
        )

    render_html(
        """
        </div>
        """
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
# ALERT COOLDOWN
# ============================================================

def generate_alert():

    current_dt = datetime.now(
        ZoneInfo("Asia/Kolkata")
    )

    previous = (
        st.session_state.last_alert_time
    )

    # 5 MINUTE COOLDOWN
    if previous is not None:

        difference = (
            current_dt - previous
        ).total_seconds()

        if difference < 300:
            return

    if send_email_alert():

        st.session_state.last_alert_time = current_dt

        render_html(
        """
        <div class="email-success">

        <div class="email-success-title">
        📧 ALERT EMAIL SENT SUCCESSFULLY
        </div>

        <div class="email-success-text">
        Garbage overflow alert sent to the configured email address.
        </div>

        </div>
        """
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

    return (
        result,
        detections
    )


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

    render_html(
    f"""
    <div class="output-result">

    <div class="output-result-title">
    🎯 {title}
    </div>
    """
    )

    display_result_image(
        result
    )

    status, confidence = get_final_prediction(
        detections
    )

    if status == "GARBAGE OVERFLOW":

        render_html(
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
        """
        )

        generate_alert()

    elif status == "NORMAL":

        render_html(
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
        """
        )

    else:

        render_html(
        """
        <div class="status-no-detection">

        ⚠️ No clear garbage condition detected.
        <br>
        Please try another image.

        </div>
        """
        )

    if detections:

        render_html(
        """
        <div class="details-card">

        <div class="details-title">
        📊 Detection Details
        </div>
        """
        )

        for detection in detections:

            render_html(
            f"""
            <div class="detail-row">

            <b>
            {detection["class"].title()}
            </b>

            &nbsp; — &nbsp;

            {detection["confidence"] * 100:.2f}%
            confidence

            </div>
            """
            )

        render_html(
        """
        </div>
        """
        )

    render_html(
    """
    </div>
    """
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
            (10, 25, 45),
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
    # FFMPEG CONVERSION
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

    # CLEAN TEMP FILES

    for path in [
        raw_output_path,
        h264_output_path
    ]:

        try:

            if os.path.exists(path):

                os.remove(path)

        except Exception:
            pass

    # FINAL RESULT

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

    render_html(
    f"""
    <div class="empty-message">
    {message}
    </div>
    """
    )


def section_title(
    icon,
    title
):

    render_html(
    f"""
    <div class="mode-title">
    {icon} {title}
    </div>
    """
    )


def visible_success(message):

    render_html(
    f"""
    <div class="success-visible">
    ✅ {message}
    </div>
    """
    )


# ============================================================
# HOME PAGE
# ============================================================

if st.session_state.page == "home":

    # ========================================================
    # HERO TITLE
    # ========================================================

    render_html(
    """
    <div class="hero-title">
    ♻️ EcoBin AI
    </div>

    <div class="hero-subtitle">
    Smart Garbage Overflow Detection using Artificial Intelligence
    </div>
    """
    )

    hero_left, hero_right = st.columns(
        [1, 1.25],
        gap="large"
    )

    # ========================================================
    # HERO LEFT
    # ========================================================

    with hero_left:

        logo_base64 = get_logo_base64()

        if logo_base64:

            logo_html = f"""
            <img
                src="data:image/png;base64,{logo_base64}"
                class="hero-logo-inside"
            />
            """

        else:

            logo_html = """
            <div
                style="
                color:#94a3b8;
                font-size:11px;
                text-align:center;
                "
            >
            Logo not found
            </div>
            """

        render_html(
        f"""
        <div class="hero-card">

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

        <div class="hero-project-subtitle-new">
        📧 Intelligent Safety • Real-Time Detection
        </div>

        </div>


        <div class="hero-logo-container">
        {logo_html}
        </div>

        </div>

        </div>
        """
        )


    # ========================================================
    # HERO RIGHT
    # ========================================================

    with hero_right:

        render_html(
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
        """
        )


    # ========================================================
    # SYSTEM CAPABILITIES
    # ========================================================
    # NO EXTRA SPACER HERE

    render_html(
    """
    <div class="section-title">
    ⚡ System Capabilities
    </div>
    """
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

            render_html(
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
            """
            )


    # ========================================================
    # START BUTTON
    # ========================================================

    render_html(
    """
    <div style="height:12px;"></div>
    """
    )

    render_html(
    """
    <div class="primary-btn">
    """
    )

    if st.button(
        "🔎  START AI DETECTION",
        key="start_detection",
        use_container_width=True
    ):

        st.session_state.page = "predict"

        st.rerun()

    render_html(
    """
    </div>
    """
    )


    # ========================================================
    # TEAM
    # ========================================================

    render_html(
    """
    <div class="section-title">
    👥 Project Team
    </div>
    """
    )

    team_col, mail_col, guide_col = st.columns(
        [1.25, 1.25, .85],
        gap="medium"
    )


    # TEAM MEMBERS

    with team_col:

        render_html(
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
        """
        )


    # GMAIL

    with mail_col:

        render_html(
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
        """
        )


    # GUIDE

    with guide_col:

        render_html(
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
        """
        )


    # ========================================================
    # FOOTER
    # ========================================================

    render_html(
    """
    <div class="footer-text">
    EcoBin AI • Smart Garbage Overflow Detection
    </div>
    """
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

        render_html(
        """
        <div class="page-header">

        <div class="page-header-title">
        ♻️ EcoBin AI Overflow Detection
        </div>

        <div class="page-header-sub">
        AI-powered image, camera and CCTV garbage overflow analysis
        </div>

        </div>
        """
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

        render_html(
        """
        <div class="io-card">

        <div class="io-card-title">
        📤 Upload
        </div>

        <div class="io-description">
        Upload a garbage image for AI analysis
        </div>
        """
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

            render_html(
            """
            <div class="waiting-visible">
            📤 Select an image to start detection
            </div>
            """
            )

        render_html(
        """
        </div>
        """
        )


    # ========================================================
    # IMAGE INPUT
    # ========================================================

    with image_input_col:

        render_html(
        """
        <div class="io-card">

        <div class="io-card-title">
        🖼️ Input
        </div>

        <div class="io-description">
        Selected image preview
        </div>
        """
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

        render_html(
        """
        </div>
        """
        )


    # ========================================================
    # IMAGE OUTPUT
    # ========================================================

    with image_output_col:

        render_html(
        """
        <div class="io-card">

        <div class="io-card-title">
        🎯 Output
        </div>

        <div class="io-description">
        AI detection result
        </div>
        """
        )

        if (
            uploaded_image
            and input_image is not None
        ):

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

                render_html(
                """
                <div class="waiting-visible">
                🔍 Click "Detect Image" to generate AI output
                </div>
                """
                )

        else:

            empty_box(
                "AI prediction output will appear here."
            )

        render_html(
        """
        </div>
        """
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

        render_html(
        """
        <div class="io-card">

        <div class="io-card-title">
        📷 Camera
        </div>

        <div class="io-description">
        Capture a garbage-bin image
        </div>
        """
        )

        camera_image = st.camera_input(
            "Capture image",
            key="camera",
            label_visibility="collapsed"
        )

        if not camera_image:

            render_html(
            """
            <div class="waiting-visible">
            📷 Camera preview will appear here
            </div>
            """
            )

        render_html(
        """
        </div>
        """
        )


    # ========================================================
    # CAMERA INPUT
    # ========================================================

    with camera_input_col:

        render_html(
        """
        <div class="io-card">

        <div class="io-card-title">
        🖼️ Input
        </div>

        <div class="io-description">
        Captured image preview
        </div>
        """
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

        render_html(
        """
        </div>
        """
        )


    # ========================================================
    # CAMERA OUTPUT
    # ========================================================

    with camera_output_col:

        render_html(
        """
        <div class="io-card">

        <div class="io-card-title">
        🎯 Output
        </div>

        <div class="io-description">
        AI camera detection result
        </div>
        """
        )

        if (
            camera_image
            and camera_pil is not None
        ):

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

                render_html(
                """
                <div class="waiting-visible">
                🔍 Click "Detect Camera Image" to generate AI output
                </div>
                """
                )

        else:

            empty_box(
                "Camera prediction output will appear here."
            )

        render_html(
        """
        </div>
        """
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

        render_html(
        """
        <div class="io-card">

        <div class="io-card-title">
        📤 Upload Video
        </div>

        <div class="io-description">
        Upload CCTV/video footage
        </div>
        """
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

            render_html(
            """
            <div class="waiting-visible">
            🎥 Select a CCTV video to analyze
            </div>
            """
            )

        render_html(
        """
        </div>
        """
        )


    # ========================================================
    # VIDEO INPUT
    # ========================================================

    with video_input_col:

        render_html(
        """
        <div class="io-card">

        <div class="io-card-title">
        🎬 Input
        </div>

        <div class="io-description">
        Uploaded CCTV video preview
        </div>
        """
        )

        if uploaded_video:

            st.video(
                uploaded_video
            )

        else:

            empty_box(
                "Uploaded CCTV/video will appear here."
            )

        render_html(
        """
        </div>
        """
        )


    # ========================================================
    # VIDEO OUTPUT
    # ========================================================

    with video_output_col:

        render_html(
        """
        <div class="io-card">

        <div class="io-card-title">
        🎯 Output
        </div>

        <div class="io-description">
        AI processed video result
        </div>
        """
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

                    render_html(
                    """
                    <div class="video-result-box">
                    """
                    )

                    st.video(
                        output_video_bytes
                    )

                    render_html(
                    """
                    </div>
                    """
                    )

                else:

                    st.error(
                        "❌ Output video could not be generated."
                    )


                # VIDEO STATUS

                if video_status == "GARBAGE OVERFLOW":

                    render_html(
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
                    """
                    )

                    generate_alert()

                elif video_status == "NORMAL":

                    render_html(
                    """
                    <div class="status-normal">

                    <div class="status-title">
                    ✅ No Garbage Overflow Detected
                    </div>

                    <b>Status:</b>
                    Normal

                    </div>
                    """
                    )

                else:

                    render_html(
                    """
                    <div class="status-no-detection">

                    ⚠️ No clear garbage condition
                    was detected in the video.

                    </div>
                    """
                    )

            else:

                render_html(
                """
                <div class="waiting-visible">
                🎥 Click "Analyze CCTV Video"
                to generate AI output
                </div>
                """
                )

        else:

            empty_box(
                "Video prediction output will appear here."
            )

        render_html(
        """
        </div>
        """
        )


    # ========================================================
    # FOOTER
    # ========================================================

    render_html(
    """
    <div class="footer-text">
    EcoBin AI • AI-Powered Smart Garbage Overflow Detection
    </div>
    """
    )
