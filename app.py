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

from email.message import EmailMessage
from datetime import datetime
from zoneinfo import ZoneInfo

from streamlit_geolocation import streamlit_geolocation


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="EcoBin AI",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# SESSION STATE
# ============================================================

if "page" not in st.session_state:
    st.session_state.page = "home"

if "last_alert_time" not in st.session_state:
    st.session_state.last_alert_time = None

if "image_result" not in st.session_state:
    st.session_state.image_result = None

if "camera_result" not in st.session_state:
    st.session_state.camera_result = None

if "video_result" not in st.session_state:
    st.session_state.video_result = None

if "live_latitude" not in st.session_state:
    st.session_state.live_latitude = None

if "live_longitude" not in st.session_state:
    st.session_state.live_longitude = None

if "live_accuracy" not in st.session_state:
    st.session_state.live_accuracy = None

if "live_area" not in st.session_state:
    st.session_state.live_area = None

if "location_loaded" not in st.session_state:
    st.session_state.location_loaded = False


# ============================================================
# PROFESSIONAL UI CSS
# ============================================================

st.markdown(
    """
<style>

.stApp {
    background:
        linear-gradient(180deg, #f8fafc 0%, #eef3f8 100%);
}

/* Main width */

.block-container {
    max-width: 1450px;
    padding-top: 28px;
    padding-bottom: 40px;
    padding-left: 5%;
    padding-right: 5%;
}

/* Hide Streamlit default elements */

#MainMenu {
    visibility: hidden;
}

header {
    visibility: hidden;
}

footer {
    visibility: hidden;
}


/* ============================================================
   GENERAL TEXT
   ============================================================ */

.page-title {
    text-align: center;
    color: #17345f !important;
    font-size: 36px !important;
    font-weight: 900 !important;
    letter-spacing: -0.5px;
    margin-top: 5px;
    margin-bottom: 8px;
}

.page-subtitle {
    text-align: center;
    color: #64748b !important;
    font-size: 15px !important;
    margin-bottom: 28px;
}

.section-title {
    color: #17345f !important;
    font-size: 21px !important;
    font-weight: 850 !important;
    margin-top: 12px;
    margin-bottom: 14px;
}

.small-section-title {
    color: #334155 !important;
    font-size: 16px !important;
    font-weight: 800 !important;
    margin-bottom: 10px;
}


/* ============================================================
   HOME HERO
   ============================================================ */

.hero-card {
    background: #ffffff;
    border: 1px solid #dbe3ec;
    border-radius: 22px;
    padding: 28px;
    min-height: 310px;
    box-shadow: 0 8px 25px rgba(15, 23, 42, 0.06);
}

.hero-left {
    display: flex;
    flex-direction: column;
    justify-content: center;
    min-height: 250px;
}

.aicw-badge {
    display: inline-block;
    width: fit-content;
    background: #eff6ff;
    color: #17345f !important;
    border: 1px solid #bfdbfe;
    border-radius: 30px;
    padding: 8px 16px;
    font-size: 13px !important;
    font-weight: 800 !important;
    margin-bottom: 16px;
}

.aicw-title {
    color: #17345f !important;
    font-size: 28px !important;
    font-weight: 900 !important;
    line-height: 1.25;
    margin-bottom: 8px;
}

.capstone {
    color: #64748b !important;
    font-size: 17px !important;
    font-weight: 700 !important;
    margin-bottom: 24px;
}

.logo-area {
    text-align: center;
    margin-top: 12px;
    margin-bottom: 8px;
}

.project-mini {
    color: #64748b !important;
    font-size: 12px !important;
    margin-top: 4px;
}


/* ============================================================
   DESCRIPTION
   ============================================================ */

.description-card {
    background: #ffffff;
    border: 1px solid #dbe3ec;
    border-radius: 22px;
    padding: 28px;
    min-height: 310px;
    box-shadow: 0 8px 25px rgba(15, 23, 42, 0.06);
}

.description-heading {
    color: #17345f !important;
    font-size: 22px !important;
    font-weight: 900 !important;
    margin-bottom: 15px;
}

.description-text {
    color: #475569 !important;
    font-size: 15px !important;
    line-height: 1.85 !important;
}


/* ============================================================
   FEATURE CARDS
   ============================================================ */

.feature-card {
    background: #ffffff;
    border: 1px solid #dbe3ec;
    border-radius: 16px;
    padding: 18px;
    text-align: center;
    min-height: 110px;
    box-shadow: 0 4px 15px rgba(15, 23, 42, 0.04);
}

.feature-icon {
    font-size: 25px;
    margin-bottom: 5px;
}

.feature-title {
    color: #26364d !important;
    font-size: 14px !important;
    font-weight: 850 !important;
}

.feature-text {
    color: #64748b !important;
    font-size: 12px !important;
}


/* ============================================================
   TEAM CARDS
   ============================================================ */

.info-card {
    background: #ffffff;
    border: 1px solid #dbe3ec;
    border-radius: 18px;
    padding: 20px;
    min-height: 165px;
    box-shadow: 0 5px 18px rgba(15, 23, 42, 0.05);
}

.info-card-title {
    color: #17345f !important;
    font-size: 14px !important;
    font-weight: 900 !important;
    margin-bottom: 12px;
}

.info-card-text {
    color: #475569 !important;
    font-size: 13px !important;
    line-height: 2 !important;
}


/* ============================================================
   DETECTION PAGE
   ============================================================ */

.detect-title {
    text-align: center;
    color: #17345f !important;
    font-size: 32px !important;
    font-weight: 900 !important;
    margin-bottom: 5px;
}

.detect-subtitle {
    text-align: center;
    color: #64748b !important;
    font-size: 14px !important;
    margin-bottom: 25px;
}


/* ============================================================
   LOCATION
   ============================================================ */

.location-wrapper {
    background: #ffffff;
    border: 1px solid #bfdbfe;
    border-radius: 18px;
    padding: 20px;
    margin-bottom: 25px;
    box-shadow: 0 5px 18px rgba(37, 99, 235, 0.05);
}

.location-title {
    color: #17345f !important;
    font-size: 17px !important;
    font-weight: 900 !important;
    margin-bottom: 10px;
}

.location-box {
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    border-radius: 13px;
    padding: 16px;
    color: #1e3a8a !important;
    line-height: 1.8;
}


/* ============================================================
   DETECTION CARDS
   ============================================================ */

.detect-card {
    background: #ffffff;
    border: 1px solid #dbe3ec;
    border-radius: 18px;
    padding: 20px;
    min-height: 235px;
    box-shadow: 0 5px 18px rgba(15, 23, 42, 0.05);
}

.detect-card-title {
    color: #17345f !important;
    font-size: 17px !important;
    font-weight: 900 !important;
    margin-bottom: 15px;
}

.empty-state {
    min-height: 155px;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    color: #94a3b8 !important;
    font-size: 14px !important;
    line-height: 1.7;
    padding: 20px;
}

.input-state {
    background: #f8fafc;
    border: 1px dashed #cbd5e1;
    border-radius: 12px;
    min-height: 145px;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    color: #64748b !important;
    padding: 18px;
}


/* ============================================================
   DETECT BUTTON
   ============================================================ */

.detect-button-area {
    margin-top: 14px;
    margin-bottom: 20px;
}

div.stButton > button {
    width: 100%;
    min-height: 46px;
    border-radius: 10px !important;
    border: 1px solid #17345f !important;
    background: #17345f !important;
    color: #ffffff !important;
    font-size: 14px !important;
    font-weight: 800 !important;
    box-shadow: 0 5px 12px rgba(23, 52, 95, 0.18);
}

div.stButton > button:hover {
    background: #214878 !important;
    border-color: #214878 !important;
    color: #ffffff !important;
}


/* ============================================================
   RESULT SECTION
   ============================================================ */

.result-section {
    background: #ffffff;
    border: 1px solid #dbe3ec;
    border-radius: 20px;
    padding: 24px;
    margin-top: 18px;
    margin-bottom: 25px;
    box-shadow: 0 7px 22px rgba(15, 23, 42, 0.06);
}

.result-heading {
    color: #17345f !important;
    font-size: 20px !important;
    font-weight: 900 !important;
    margin-bottom: 15px;
}

.result-image {
    border-radius: 14px;
    overflow: hidden;
}


/* ============================================================
   STATUS BOXES
   ============================================================ */

.alert-box {
    background: #fff1f2;
    border: 2px solid #ef4444;
    border-radius: 15px;
    padding: 20px;
    color: #991b1b !important;
    line-height: 1.8;
    margin-top: 15px;
}

.normal-box {
    background: #f0fdf4;
    border: 2px solid #22c55e;
    border-radius: 15px;
    padding: 20px;
    color: #166534 !important;
    line-height: 1.8;
    margin-top: 15px;
}

.no-detection-box {
    background: #fffbeb;
    border: 2px solid #f59e0b;
    border-radius: 15px;
    padding: 20px;
    color: #92400e !important;
    line-height: 1.8;
    margin-top: 15px;
}


/* ============================================================
   DETAIL CARDS
   ============================================================ */

.detail-card {
    background: #f8fafc;
    border: 1px solid #dbe3ec;
    border-radius: 14px;
    padding: 16px;
    margin-top: 10px;
}

.detail-name {
    color: #334155 !important;
    font-size: 14px !important;
    font-weight: 800 !important;
}

.detail-confidence {
    color: #17345f !important;
    font-size: 17px !important;
    font-weight: 900 !important;
}


/* ============================================================
   EMAIL
   ============================================================ */

.email-success {
    background: #dcfce7;
    border: 2px solid #15803d;
    border-radius: 14px;
    padding: 18px;
    margin-top: 15px;
    text-align: center;
}

.email-success-title {
    color: #14532d !important;
    font-size: 18px !important;
    font-weight: 900 !important;
}

.email-success-text {
    color: #166534 !important;
    font-size: 14px !important;
    font-weight: 700 !important;
}

.email-error {
    background: #fef2f2;
    border: 2px solid #dc2626;
    border-radius: 12px;
    padding: 15px;
    margin-top: 12px;
    color: #991b1b !important;
    font-weight: 700 !important;
}


/* ============================================================
   FOOTER
   ============================================================ */

.footer-text {
    text-align: center;
    color: #64748b;
    margin-top: 35px;
    padding-top: 20px;
    border-top: 1px solid #dbe3ec;
    font-size: 12px;
}


/* ============================================================
   FILE UPLOADER
   ============================================================ */

[data-testid="stFileUploader"] {
    background: #f8fafc;
    border-radius: 12px;
}


/* ============================================================
   MOBILE
   ============================================================ */

@media(max-width: 900px) {

    .block-container {
        padding-left: 4%;
        padding-right: 4%;
    }

    .page-title {
        font-size: 27px !important;
    }

    .aicw-title {
        font-size: 24px !important;
    }

    .detect-title {
        font-size: 26px !important;
    }

}

</style>
""",
    unsafe_allow_html=True
)


# ============================================================
# LOGO
# ============================================================

def show_logo(width=105):

    logo_path = os.path.join(
        os.path.dirname(__file__),
        "logo.png"
    )

    if os.path.exists(logo_path):

        st.markdown(
            '<div class="logo-area">',
            unsafe_allow_html=True
        )

        st.image(
            logo_path,
            width=width
        )

        st.markdown(
            '<div class="project-mini">EcoBin AI</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
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
def reverse_geocode(latitude, longitude):

    try:

        url = "https://nominatim.openstreetmap.org/reverse"

        params = {
            "lat": latitude,
            "lon": longitude,
            "format": "jsonv2",
            "addressdetails": 1,
            "zoom": 18,
            "accept-language": "en"
        }

        headers = {
            "User-Agent":
                "EcoBin-AI-Garbage-Overflow-Detection/1.0"
        }

        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        address = data.get("address", {})

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

        state = address.get("state", "")
        postcode = address.get("postcode", "")

        parts = []

        if area:
            parts.append(area)

        if city and city != area:
            parts.append(city)

        if state:
            parts.append(state)

        if postcode:
            parts.append(postcode)

        if parts:
            return ", ".join(parts)

        display_name = data.get("display_name")

        if display_name:
            return display_name

        return "Area name unavailable"

    except Exception:

        return "Area name unavailable"


# ============================================================
# LIVE LOCATION
# ============================================================

def get_live_location():

    location = streamlit_geolocation()

    if not location:
        return

    latitude = location.get("latitude")
    longitude = location.get("longitude")
    accuracy = location.get("accuracy")

    if latitude is None or longitude is None:
        return

    try:

        latitude = float(latitude)
        longitude = float(longitude)

        st.session_state.live_latitude = latitude
        st.session_state.live_longitude = longitude
        st.session_state.live_accuracy = accuracy

        area = reverse_geocode(
            latitude,
            longitude
        )

        st.session_state.live_area = area
        st.session_state.location_loaded = True

    except Exception:

        st.session_state.location_loaded = False


# ============================================================
# LOCATION TEXT
# ============================================================

def get_location():

    area = st.session_state.live_area
    latitude = st.session_state.live_latitude
    longitude = st.session_state.live_longitude

    if area and latitude is not None and longitude is not None:

        return (
            f"{area}\n"
            f"Latitude: {latitude:.6f}\n"
            f"Longitude: {longitude:.6f}"
        )

    return "Live location not available"


# ============================================================
# MAP URL
# ============================================================

def get_map_url():

    latitude = st.session_state.live_latitude
    longitude = st.session_state.live_longitude

    if latitude is None or longitude is None:
        return None

    return (
        "https://www.google.com/maps/search/?api=1"
        f"&query={latitude},{longitude}"
    )


# ============================================================
# CURRENT TIME
# ============================================================

def get_current_time():

    india_time = datetime.now(
        ZoneInfo("Asia/Kolkata")
    )

    return india_time.strftime(
        "%d-%b-%Y %I:%M:%S %p"
    )


# ============================================================
# LOCATION DISPLAY
# ============================================================

def display_live_location():

    st.markdown(
        """
<div class="location-wrapper">

<div class="location-title">
    📍 Live Location
</div>

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
                accuracy_text = f"{float(accuracy):.1f} meters"

            except Exception:
                accuracy_text = str(accuracy)

        st.markdown(
            f"""
<div class="location-box">

<b>📍 Current Area</b><br>
{area}<br><br>

<b>Latitude:</b> {latitude:.6f}<br>

<b>Longitude:</b> {longitude:.6f}<br>

<b>GPS Accuracy:</b> {accuracy_text}<br><br>

<b>🕒 Location Time:</b>
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

        st.info(
            "📍 Allow location permission in your browser "
            "to display your current area."
        )


# ============================================================
# SEND EMAIL
# ============================================================

def send_email_alert():

    try:

        sender_email = st.secrets["EMAIL_SENDER"]
        sender_password = st.secrets["EMAIL_PASSWORD"]
        receiver_email = st.secrets["EMAIL_RECEIVER"]

        message = EmailMessage()

        message["Subject"] = (
            "EcoBin AI - Garbage Overflow Alert"
        )

        message["From"] = sender_email
        message["To"] = receiver_email

        message.set_content(
            f"""
GARBAGE OVERFLOW DETECTED!

EcoBin AI - Smart Garbage Overflow Detection System

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

            server.send_message(message)

        return True

    except Exception as e:

        st.markdown(
            f"""
<div class="email-error">
❌ Email alert failed: {str(e)}
</div>
""",
            unsafe_allow_html=True
        )

        return False


# ============================================================
# GENERATE ALERT
# ============================================================

def generate_alert():

    current_dt = datetime.now(
        ZoneInfo("Asia/Kolkata")
    )

    previous = st.session_state.last_alert_time

    if previous is not None:

        difference = (
            current_dt - previous
        ).total_seconds()

        if difference < 300:
            return

    email_sent = send_email_alert()

    if email_sent:

        st.session_state.last_alert_time = current_dt

        st.markdown(
            """
<div class="email-success">

<div class="email-success-title">
📧 ALERT EMAIL SENT SUCCESSFULLY
</div>

<div class="email-success-text">
The garbage overflow alert has been successfully
sent to the configured email address.
</div>

</div>
""",
            unsafe_allow_html=True
        )


# ============================================================
# NORMALIZE CLASS NAME
# ============================================================

def normalize_class_name(name):

    name = str(name).lower().strip()

    name = name.replace("_", " ")
    name = name.replace("-", " ")

    return name


# ============================================================
# EXTRACT DETECTIONS
# ============================================================

def extract_detections(result):

    detections = []

    if result.boxes is None:
        return detections

    for box in result.boxes:

        class_id = int(box.cls[0])

        confidence = float(box.conf[0])

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

def get_final_prediction(detections):

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
# PREDICT IMAGE
# ============================================================

def predict_image(image, model):

    image_np = np.array(image)

    results = model.predict(
        source=image_np,
        conf=0.20,
        verbose=False
    )

    result = results[0]

    detections = extract_detections(result)

    return result, detections


# ============================================================
# RESULT DISPLAY
# ============================================================

def display_prediction(
    result,
    detections,
    title="Prediction Result"
):

    status, confidence = get_final_prediction(
        detections
    )

    # --------------------------------------------------------
    # RESULT HEADER
    # --------------------------------------------------------

    st.markdown(
        f"""
<div class="result-section">

<div class="result-heading">
    {title}
</div>

</div>
""",
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # OUTPUT IMAGE
    # --------------------------------------------------------

    annotated = result.plot()

    st.markdown(
        '<div class="result-image">',
        unsafe_allow_html=True
    )

    st.image(
        annotated,
        use_container_width=True
    )

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    if status == "GARBAGE OVERFLOW":

        st.markdown(
            f"""
<div class="alert-box">

<h3>🚨 Garbage Overflow Detected</h3>

<b>Detection:</b> Overflow<br><br>

<b>Confidence:</b>
{confidence * 100:.2f}%<br><br>

<b>📍 Location:</b><br>
{get_location().replace(chr(10), "<br>")}<br><br>

<b>🕒 Date & Time:</b>
{get_current_time()}<br><br>

<b>⚠️ Status:</b>
Violation Detected

</div>
""",
            unsafe_allow_html=True
        )

        generate_alert()

    elif status == "NORMAL":

        st.markdown(
            f"""
<div class="normal-box">

<h3>✅ No Garbage Overflow Detected</h3>

<b>Detection:</b> Normal<br><br>

<b>Confidence:</b>
{confidence * 100:.2f}%<br><br>

<b>📍 Location:</b><br>
{get_location().replace(chr(10), "<br>")}<br><br>

<b>🕒 Date & Time:</b>
{get_current_time()}<br><br>

<b>Status:</b>
Normal

</div>
""",
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            """
<div class="no-detection-box">

<h3>⚠️ No Clear Detection</h3>

The AI could not confidently identify
Normal or Overflow condition.

Please try another image with a clearer
view of the garbage bin.

</div>
""",
            unsafe_allow_html=True
        )

    # --------------------------------------------------------
    # DETECTION DETAILS - SEPARATE SECTION
    # --------------------------------------------------------

    st.markdown(
        """
<div class="section-title">
    🔎 Detection Details
</div>
""",
        unsafe_allow_html=True
    )

    if detections:

        detail_cols = st.columns(
            min(len(detections), 3),
            gap="medium"
        )

        for index, detection in enumerate(detections):

            with detail_cols[index % len(detail_cols)]:

                st.markdown(
                    f"""
<div class="detail-card">

<div class="detail-name">
    🏷️ {detection["class"].title()}
</div>

<div class="detail-confidence">
    {detection["confidence"] * 100:.2f}%
</div>

<div style="color:#64748b;font-size:12px;margin-top:5px;">
    Detection Confidence
</div>

</div>
""",
                    unsafe_allow_html=True
                )

    else:

        st.info(
            "No object detections were returned by the model."
        )


# ============================================================
# VIDEO PROCESSING
# ============================================================

def process_video(video_path, model):

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():

        return (
            "NO CLEAR DETECTION",
            None,
            0.0
        )

    fps = cap.get(cv2.CAP_PROP_FPS)

    if fps <= 0:
        fps = 25

    width = int(
        cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    )

    height = int(
        cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    )

    total_frames = int(
        cap.get(cv2.CAP_PROP_FRAME_COUNT)
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

    fourcc = cv2.VideoWriter_fourcc(
        *"mp4v"
    )

    writer = cv2.VideoWriter(
        raw_output_path,
        fourcc,
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

        detections = extract_detections(result)

        status, confidence = get_final_prediction(
            detections
        )

        if status == "GARBAGE OVERFLOW":

            overflow_count += 1
            detection_count += 1

            if confidence > best_overflow_confidence:

                best_overflow_confidence = confidence

        elif status == "NORMAL":

            normal_count += 1
            detection_count += 1

        annotated_frame = result.plot()

        if status == "GARBAGE OVERFLOW":

            cv2.rectangle(
                annotated_frame,
                (10, 10),
                (520, 80),
                (0, 0, 255),
                -1
            )

            cv2.putText(
                annotated_frame,
                "GARBAGE OVERFLOW DETECTED",
                (25, 55),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.80,
                (255, 255, 255),
                2,
                cv2.LINE_AA
            )

        elif status == "NORMAL":

            cv2.rectangle(
                annotated_frame,
                (10, 10),
                (300, 80),
                (0, 150, 0),
                -1
            )

            cv2.putText(
                annotated_frame,
                "NORMAL",
                (25, 55),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.80,
                (255, 255, 255),
                2,
                cv2.LINE_AA
            )

        else:

            cv2.rectangle(
                annotated_frame,
                (10, 10),
                (370, 80),
                (80, 80, 80),
                -1
            )

            cv2.putText(
                annotated_frame,
                "NO CLEAR DETECTION",
                (25, 55),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.70,
                (255, 255, 255),
                2,
                cv2.LINE_AA
            )

        if confidence > 0:

            cv2.putText(
                annotated_frame,
                f"Confidence: {confidence * 100:.2f}%",
                (15, height - 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (255, 255, 255),
                2,
                cv2.LINE_AA
            )

        writer.write(annotated_frame)

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

    # --------------------------------------------------------
    # H264 CONVERSION
    # --------------------------------------------------------

    try:

        ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()

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

        final_video_path = h264_output_path

    except Exception:

        final_video_path = raw_output_path

    # --------------------------------------------------------
    # READ VIDEO
    # --------------------------------------------------------

    try:

        with open(
            final_video_path,
            "rb"
        ) as video_file:

            output_video_bytes = video_file.read()

    except Exception:

        output_video_bytes = None

    # --------------------------------------------------------
    # CLEANUP
    # --------------------------------------------------------

    try:

        if os.path.exists(raw_output_path):
            os.remove(raw_output_path)

        if os.path.exists(h264_output_path):
            os.remove(h264_output_path)

    except Exception:

        pass

    # --------------------------------------------------------
    # FINAL RESULT
    # --------------------------------------------------------

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
# HOME PAGE
# ============================================================

if st.session_state.page == "home":

    # --------------------------------------------------------
    # TITLE
    # --------------------------------------------------------

    st.markdown(
        """
<div class="page-title">
    ♻️ EcoBin AI
</div>

<div class="page-subtitle">
    Smart Garbage Overflow Detection using Artificial Intelligence
</div>
""",
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # HERO SECTION
    # --------------------------------------------------------

    left_col, right_col = st.columns(
        [0.42, 0.58],
        gap="large"
    )

    # --------------------------------------------------------
    # LEFT HERO
    # --------------------------------------------------------

    with left_col:

        st.markdown(
            '<div class="hero-card">',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="hero-left">',
            unsafe_allow_html=True
        )

        st.markdown(
            """
<div class="aicw-badge">
    🎓 AICW PROGRAM
</div>

<div class="aicw-title">
    AI Career for Women
</div>

<div class="capstone">
    Capstone Project
</div>
""",
            unsafe_allow_html=True
        )

        # ----------------------------------------------------
        # LOGO MOVED HERE
        # ----------------------------------------------------

        show_logo(
            width=115
        )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )

    # --------------------------------------------------------
    # RIGHT HERO
    # --------------------------------------------------------

    with right_col:

        st.markdown(
            """
<div class="description-card">

<div class="description-heading">
    🌱 Project Description
</div>

<div class="description-text">

<b>EcoBin AI</b> is an AI-powered Smart Garbage Overflow
Detection System designed to automatically identify
overflowing garbage bins using computer vision and
YOLOv8 object detection.

<br><br>

The system analyzes <b>images, camera-captured photos,
and CCTV/video files</b> to identify garbage overflow
conditions.

<br><br>

The trained YOLOv8 model classifies the detected garbage
condition into two classes:
<b>Normal</b> and <b>Overflow</b>.

<br><br>

When an overflow condition is detected, EcoBin AI
automatically generates an alert containing the
<b>live location, date, time and violation status</b>.
The alert is also sent to the configured user's email.

</div>

</div>
""",
            unsafe_allow_html=True
        )

    st.write("")
    st.write("")


    # --------------------------------------------------------
    # FEATURES
    # --------------------------------------------------------

    st.markdown(
        """
<div class="section-title">
    ⚡ System Capabilities
</div>
""",
        unsafe_allow_html=True
    )

    f1, f2, f3, f4 = st.columns(
        4,
        gap="medium"
    )

    with f1:

        st.markdown(
            """
<div class="feature-card">

<div class="feature-icon">🖼️</div>

<div class="feature-title">
Image Detection
</div>

<div class="feature-text">
Analyze uploaded garbage images
</div>

</div>
""",
            unsafe_allow_html=True
        )

    with f2:

        st.markdown(
            """
<div class="feature-card">

<div class="feature-icon">📷</div>

<div class="feature-title">
Camera Detection
</div>

<div class="feature-text">
Capture and detect using camera
</div>

</div>
""",
            unsafe_allow_html=True
        )

    with f3:

        st.markdown(
            """
<div class="feature-card">

<div class="feature-icon">🎥</div>

<div class="feature-title">
CCTV Analysis
</div>

<div class="feature-text">
Process recorded video footage
</div>

</div>
""",
            unsafe_allow_html=True
        )

    with f4:

        st.markdown(
            """
<div class="feature-card">

<div class="feature-icon">🚨</div>

<div class="feature-title">
Smart Alerts
</div>

<div class="feature-text">
Location and email notification
</div>

</div>
""",
            unsafe_allow_html=True
        )


    st.write("")
    st.write("")


    # --------------------------------------------------------
    # PREDICT BUTTON
    # --------------------------------------------------------

    predict_left, predict_middle, predict_right = st.columns(
        [1, 1.2, 1]
    )

    with predict_middle:

        if st.button(
            "🔍  START AI DETECTION",
            key="predict",
            use_container_width=True
        ):

            st.session_state.page = "predict"

            st.rerun()


    st.write("")
    st.write("")


    # --------------------------------------------------------
    # TEAM DETAILS
    # --------------------------------------------------------

    st.markdown(
        """
<div class="section-title">
    👥 Project Team
</div>
""",
        unsafe_allow_html=True
    )

    team_col, gmail_col, guide_col = st.columns(
        [1.1, 1.1, 0.8],
        gap="medium"
    )

    with team_col:

        st.markdown(
            """
<div class="info-card">

<div class="info-card-title">
TEAM MEMBERS
</div>

<div class="info-card-text">

1. K.Lalitha Devi<br>
2. Y.Haasini<br>
3. G.Sri Divya<br>
4. N.Sushma Sri

</div>

</div>
""",
            unsafe_allow_html=True
        )

    with gmail_col:

        st.markdown(
            """
<div class="info-card">

<div class="info-card-title">
GMAIL
</div>

<div class="info-card-text">

lalithadevi825@gmail.com<br>
haasiniyanamadala@gmail.com<br>
galidivya534@gmail.com<br>
nadimpallisushmasri29@gmail.com

</div>

</div>
""",
            unsafe_allow_html=True
        )

    with guide_col:

        st.markdown(
            """
<div class="info-card">

<div class="info-card-title">
GUIDE NAME
</div>

<div class="info-card-text">

<b>MD. Abdul Aziz</b><br><br>

Trainer, Co-Lead-AICW

</div>

</div>
""",
            unsafe_allow_html=True
        )


    # --------------------------------------------------------
    # FOOTER
    # --------------------------------------------------------

    st.markdown(
        """
<div class="footer-text">
    EcoBin AI • Smart Garbage Overflow Detection • AICW Capstone Project
</div>
""",
        unsafe_allow_html=True
    )


# ============================================================
# PREDICTION PAGE
# ============================================================

else:

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    st.markdown(
        """
<div class="detect-title">
    ♻️ EcoBin AI
</div>

<div class="detect-subtitle">
    AI-Powered Smart Garbage Overflow Detection System
</div>
""",
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # BACK BUTTON
    # --------------------------------------------------------

    if st.button(
        "←  Back to Home",
        key="back"
    ):

        st.session_state.page = "home"

        st.rerun()


    st.write("")


    # --------------------------------------------------------
    # LOCATION
    # --------------------------------------------------------

    display_live_location()

    st.write("")


    # --------------------------------------------------------
    # MODEL
    # --------------------------------------------------------

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

    st.markdown(
        """
<div class="section-title">
    🖼️ Image Detection
</div>
""",
        unsafe_allow_html=True
    )


    image_upload_col, image_input_col, image_output_col = st.columns(
        3,
        gap="medium"
    )


    # --------------------------------------------------------
    # UPLOAD
    # --------------------------------------------------------

    with image_upload_col:

        st.markdown(
            """
<div class="detect-card">

<div class="detect-card-title">
📤 Upload
</div>

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
            key="image_upload"
        )


    # --------------------------------------------------------
    # INPUT
    # --------------------------------------------------------

    with image_input_col:

        st.markdown(
            """
<div class="detect-card">

<div class="detect-card-title">
📥 Input
</div>

</div>
""",
            unsafe_allow_html=True
        )

        input_image = None

        if uploaded_image:

            input_image = Image.open(
                uploaded_image
            ).convert("RGB")

            st.image(
                input_image,
                use_container_width=True
            )

        else:

            st.markdown(
                """
<div class="input-state">
    🖼️ Your uploaded image<br>
    will appear here.
</div>
""",
                unsafe_allow_html=True
            )


    # --------------------------------------------------------
    # OUTPUT
    # --------------------------------------------------------

    with image_output_col:

        st.markdown(
            """
<div class="detect-card">

<div class="detect-card-title">
📤 Output
</div>

</div>
""",
            unsafe_allow_html=True
        )

        if st.session_state.image_result is None:

            st.markdown(
                """
<div class="empty-state">
    🤖 AI prediction output<br>
    will appear here after detection.
</div>
""",
                unsafe_allow_html=True
            )

        else:

            st.success(
                "Prediction completed successfully."
            )


    # --------------------------------------------------------
    # IMAGE DETECT BUTTON
    # --------------------------------------------------------

    if uploaded_image and input_image is not None:

        if st.button(
            "🔍  DETECT IMAGE",
            key="detect_image",
            use_container_width=True
        ):

            with st.spinner(
                "🤖 AI is analyzing the image..."
            ):

                result, detections = predict_image(
                    input_image,
                    model
                )

            st.session_state.image_result = (
                result,
                detections
            )


    # --------------------------------------------------------
    # IMAGE RESULT BELOW CARDS
    # --------------------------------------------------------

    if st.session_state.image_result is not None:

        result, detections = (
            st.session_state.image_result
        )

        display_prediction(
            result,
            detections,
            "🧠 Image Prediction Result"
        )


    st.write("")
    st.write("")


    # ========================================================
    # CAMERA DETECTION
    # ========================================================

    st.markdown(
        """
<div class="section-title">
    📷 Camera Detection
</div>
""",
        unsafe_allow_html=True
    )


    camera_col, camera_input_col, camera_output_col = st.columns(
        3,
        gap="medium"
    )


    # --------------------------------------------------------
    # CAMERA
    # --------------------------------------------------------

    with camera_col:

        st.markdown(
            """
<div class="detect-card">

<div class="detect-card-title">
📷 Camera
</div>

</div>
""",
            unsafe_allow_html=True
        )

        camera_image = st.camera_input(
            "Capture Image",
            key="camera"
        )


    # --------------------------------------------------------
    # CAMERA INPUT
    # --------------------------------------------------------

    with camera_input_col:

        st.markdown(
            """
<div class="detect-card">

<div class="detect-card-title">
📥 Input
</div>

</div>
""",
            unsafe_allow_html=True
        )

        camera_pil = None

        if camera_image:

            camera_pil = Image.open(
                camera_image
            ).convert("RGB")

            st.image(
                camera_pil,
                use_container_width=True
            )

        else:

            st.markdown(
                """
<div class="input-state">
    📷 Captured camera image<br>
    will appear here.
</div>
""",
                unsafe_allow_html=True
            )


    # --------------------------------------------------------
    # CAMERA OUTPUT
    # --------------------------------------------------------

    with camera_output_col:

        st.markdown(
            """
<div class="detect-card">

<div class="detect-card-title">
📤 Output
</div>

</div>
""",
            unsafe_allow_html=True
        )

        if st.session_state.camera_result is None:

            st.markdown(
                """
<div class="empty-state">
    🤖 Camera prediction output<br>
    will appear here.
</div>
""",
                unsafe_allow_html=True
            )

        else:

            st.success(
                "Camera prediction completed."
            )


    # --------------------------------------------------------
    # CAMERA DETECT
    # --------------------------------------------------------

    if camera_image and camera_pil is not None:

        if st.button(
            "🔍  DETECT CAMERA IMAGE",
            key="detect_camera",
            use_container_width=True
        ):

            with st.spinner(
                "🤖 Analyzing camera image..."
            ):

                result, detections = predict_image(
                    camera_pil,
                    model
                )

            st.session_state.camera_result = (
                result,
                detections
            )


    # --------------------------------------------------------
    # CAMERA RESULT
    # --------------------------------------------------------

    if st.session_state.camera_result is not None:

        result, detections = (
            st.session_state.camera_result
        )

        display_prediction(
            result,
            detections,
            "🧠 Camera Prediction Result"
        )


    st.write("")
    st.write("")


    # ========================================================
    # VIDEO / CCTV
    # ========================================================

    st.markdown(
        """
<div class="section-title">
    🎥 Video / CCTV Detection
</div>
""",
        unsafe_allow_html=True
    )


    video_upload_col, video_input_col, video_output_col = st.columns(
        3,
        gap="medium"
    )


    # --------------------------------------------------------
    # VIDEO UPLOAD
    # --------------------------------------------------------

    with video_upload_col:

        st.markdown(
            """
<div class="detect-card">

<div class="detect-card-title">
📤 Upload Video
</div>

</div>
""",
            unsafe_allow_html=True
        )

        uploaded_video = st.file_uploader(
            "Choose video",
            type=[
                "mp4",
                "avi",
                "mov",
                "mkv",
                "mpeg"
            ],
            key="video_upload"
        )


    # --------------------------------------------------------
    # VIDEO INPUT
    # --------------------------------------------------------

    with video_input_col:

        st.markdown(
            """
<div class="detect-card">

<div class="detect-card-title">
📥 Input
</div>

</div>
""",
            unsafe_allow_html=True
        )

        if uploaded_video:

            st.video(
                uploaded_video
            )

        else:

            st.markdown(
                """
<div class="input-state">
    🎥 Uploaded CCTV/video<br>
    will appear here.
</div>
""",
                unsafe_allow_html=True
            )


    # --------------------------------------------------------
    # VIDEO OUTPUT
    # --------------------------------------------------------

    with video_output_col:

        st.markdown(
            """
<div class="detect-card">

<div class="detect-card-title">
📤 Output
</div>

</div>
""",
            unsafe_allow_html=True
        )

        if st.session_state.video_result is None:

            st.markdown(
                """
<div class="empty-state">
    🎬 Processed AI video<br>
    will appear here.
</div>
""",
                unsafe_allow_html=True
            )

        else:

            st.success(
                "Video processing completed."
            )


    # --------------------------------------------------------
    # VIDEO BUTTON
    # --------------------------------------------------------

    if uploaded_video:

        if st.button(
            "🎥  ANALYZE CCTV VIDEO",
            key="detect_video",
            use_container_width=True
        ):

            video_bytes = uploaded_video.getvalue()

            temp_video = tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".mp4"
            )

            temp_video.write(
                video_bytes
            )

            temp_video.close()

            try:

                with st.spinner(
                    "🤖 AI is analyzing CCTV video and generating output..."
                ):

                    (
                        video_status,
                        output_video_bytes,
                        video_conf
                    ) = process_video(
                        temp_video.name,
                        model
                    )

                st.session_state.video_result = (
                    video_status,
                    output_video_bytes,
                    video_conf
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


    # ========================================================
    # VIDEO RESULT
    # ========================================================

    if st.session_state.video_result is not None:

        (
            video_status,
            output_video_bytes,
            video_conf
        ) = st.session_state.video_result


        st.markdown(
            """
<div class="result-section">

<div class="result-heading">
    🎬 AI Processed Output Video
</div>

</div>
""",
            unsafe_allow_html=True
        )


        if output_video_bytes is not None:

            st.video(
                output_video_bytes
            )

        else:

            st.error(
                "❌ Output video could not be generated."
            )


        # ----------------------------------------------------
        # VIDEO OVERFLOW
        # ----------------------------------------------------

        if video_status == "GARBAGE OVERFLOW":

            st.markdown(
                f"""
<div class="alert-box">

<h3>🚨 Garbage Overflow Detected</h3>

<b>Detection:</b> Overflow<br><br>

<b>Confidence:</b>
{video_conf * 100:.2f}%<br><br>

<b>📍 Location:</b><br>
{get_location().replace(chr(10), "<br>")}<br><br>

<b>🕒 Date & Time:</b>
{get_current_time()}<br><br>

<b>⚠️ Status:</b>
Violation Detected

</div>
""",
                unsafe_allow_html=True
            )

            generate_alert()


        # ----------------------------------------------------
        # VIDEO NORMAL
        # ----------------------------------------------------

        elif video_status == "NORMAL":

            st.markdown(
                """
<div class="normal-box">

<h3>✅ No Garbage Overflow Detected</h3>

<b>Status:</b>
Normal

</div>
""",
                unsafe_allow_html=True
            )


        # ----------------------------------------------------
        # VIDEO NO CLEAR
        # ----------------------------------------------------

        else:

            st.markdown(
                """
<div class="no-detection-box">

<h3>⚠️ No Clear Detection</h3>

No clear garbage condition was detected
in the uploaded video.

</div>
""",
                unsafe_allow_html=True
            )


    # --------------------------------------------------------
    # FOOTER
    # --------------------------------------------------------

    st.markdown(
        """
<div class="footer-text">
    EcoBin AI • AI-Powered Garbage Overflow Detection System
</div>
""",
        unsafe_allow_html=True
    )
