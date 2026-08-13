import streamlit as st
from ultralytics import YOLO
from PIL import Image
import numpy as np
import cv2
import tempfile
import os
import json
import smtplib
import requests
from email.message import EmailMessage
from datetime import datetime, timedelta
from textwrap import dedent
from zoneinfo import ZoneInfo

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="EcoBin AI",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================
# SESSION STATE
# ============================================================

defaults = {
    "page": "home",
    "location": None,
    "location_name": None,
    "email_error": None,
    "result_image": None,
    "detections": [],
    "image_alerts": [],
    "video_output": None,
    "last_alert_time": None,
    "last_alert_key": None,
    "video_alert_sent": False,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ============================================================
# DETECTION SETTINGS
# Your trained model classes:
# 0 = Normal
# 1 = Overflow
# 2 = Person_Throwing_Garbage
# ============================================================

GENERAL_CONFIDENCE = 0.30
OVERFLOW_CONFIDENCE = 0.50
THROWING_CONFIDENCE = 0.50

# Alert is generated only after this many consecutive video frames
# contain an overflow detection. This reduces false alerts.
OVERFLOW_CONFIRM_FRAMES = 3

# Alert cooldown
ALERT_COOLDOWN_MINUTES = 5

# ============================================================
# HTML HELPER
# ============================================================

def render_html(content):
    st.html(dedent(content))


# ============================================================
# GLOBAL CSS
# ============================================================

st.html(
    """
    <style>
    .stApp {
        background:
            radial-gradient(circle at 10% 10%, rgba(34,197,94,0.13), transparent 30%),
            radial-gradient(circle at 90% 15%, rgba(6,182,212,0.12), transparent 28%),
            radial-gradient(circle at 50% 100%, rgba(16,185,129,0.08), transparent 35%),
            #07110d;
        color: #f8fafc;
    }

    .block-container {
        max-width: 1400px;
        padding-top: 30px;
        padding-bottom: 50px;
        padding-left: 5%;
        padding-right: 5%;
    }

    #MainMenu, header, footer {
        visibility: hidden;
    }

    .home-hero {
        text-align: center;
        padding: 18px 20px 30px 20px;
    }

    .hero-badge {
        display: inline-block;
        padding: 7px 15px;
        border-radius: 30px;
        background: rgba(34,197,94,0.12);
        border: 1px solid rgba(74,222,128,0.30);
        color: #86efac;
        font-size: 13px;
        font-weight: 700;
        margin-bottom: 15px;
    }

    .hero-title {
        font-size: 56px;
        line-height: 1.1;
        font-weight: 900;
        letter-spacing: -2px;
        background: linear-gradient(90deg,#ffffff,#86efac,#67e8f9);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .hero-subtitle {
        color: #cbd5e1;
        font-size: 19px;
        font-weight: 600;
        margin-top: 10px;
    }

    .home-card, .team-card, .guide-card {
        background: linear-gradient(145deg,rgba(20,42,31,0.88),rgba(8,24,17,0.80));
        border: 1px solid rgba(148,163,184,0.16);
        border-radius: 24px;
        padding: 28px;
        box-shadow: 0 18px 50px rgba(0,0,0,0.25);
    }

    .home-card {
        min-height: 250px;
    }

    .aicw-card {
        min-height: 330px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    .aicw-icon {
        font-size: 58px;
        margin-bottom: 15px;
    }

    .aicw-title {
        font-size: 30px;
        font-weight: 900;
        color: #ffffff;
    }

    .aicw-subtitle {
        color: #86efac;
        font-size: 18px;
        font-weight: 700;
        margin-top: 8px;
    }

    .capstone {
        margin-top: 22px;
        padding: 9px 15px;
        border-radius: 30px;
        background: rgba(34,197,94,0.10);
        border: 1px solid rgba(74,222,128,0.25);
        color: #86efac;
        font-weight: 700;
        display: inline-block;
    }

    .about-title, .card-title {
        color: #ffffff;
        font-size: 20px;
        font-weight: 900;
        margin-bottom: 12px;
    }

    .about-text {
        color: #aab5c7;
        font-size: 14px;
        line-height: 1.8;
    }

    .team-heading {
        color: #f8fafc;
        font-size: 22px;
        font-weight: 900;
        margin: 12px 0 16px 0;
    }

    .team-card {
        min-height: 165px;
        padding: 20px;
        border-radius: 20px;
    }

    .avatar {
        width: 56px;
        height: 56px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 28px;
        background: linear-gradient(135deg,#16a34a,#06b6d4);
        margin-bottom: 12px;
    }

    .member-name {
        color: #f8fafc;
        font-weight: 800;
        font-size: 15px;
    }

    .member-role {
        color: #94a3b8;
        font-size: 12px;
        margin-top: 4px;
    }

    .detect-title {
        text-align: center;
        font-size: 44px;
        font-weight: 900;
        background: linear-gradient(90deg,#86efac,#67e8f9,#ffffff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .detect-subtitle {
        text-align: center;
        color: #94a3b8;
        font-size: 15px;
        margin-bottom: 28px;
    }

    .safe-box {
        margin-top: 16px;
        padding: 18px;
        border-radius: 16px;
        background: rgba(16,185,129,0.10);
        border: 1px solid rgba(52,211,153,0.35);
        color: #6ee7b7 !important;
        font-weight: 800;
    }

    .overflow-box {
        margin-top: 16px;
        padding: 20px;
        border-radius: 17px;
        background: linear-gradient(135deg,rgba(239,68,68,0.14),rgba(127,29,29,0.12));
        border: 1px solid rgba(248,113,113,0.42);
        box-shadow: 0 10px 30px rgba(239,68,68,0.12);
    }

    .overflow-title {
        color: #fca5a5 !important;
        font-size: 18px;
        font-weight: 900;
    }

    .overflow-text {
        color: #fecaca !important;
        font-size: 14px;
        font-weight: 700;
        margin-top: 8px;
    }

    .warning-box {
        margin-top: 16px;
        padding: 18px;
        border-radius: 16px;
        background: rgba(245,158,11,0.10);
        border: 1px solid rgba(251,191,36,0.30);
        color: #fde68a !important;
        font-weight: 800;
    }

    .footer {
        text-align: center;
        color: #64748b;
        font-size: 13px;
        padding: 35px 0 10px 0;
    }

    div.stButton > button {
        width: 100%;
        min-height: 48px;
        border-radius: 13px !important;
        background: linear-gradient(135deg,#16a34a,#0891b2) !important;
        color: white !important;
        border: 1px solid rgba(134,239,172,0.35) !important;
        font-size: 14px !important;
        font-weight: 800 !important;
        box-shadow: 0 8px 25px rgba(22,163,74,0.20);
        transition: 0.25s ease;
    }

    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 35px rgba(22,163,74,0.35);
    }

    div[data-testid="stFileUploader"] {
        background: rgba(15,23,42,0.55);
        border: 1px dashed rgba(74,222,128,0.40);
        border-radius: 16px;
        padding: 10px;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: linear-gradient(145deg,rgba(20,42,31,0.80),rgba(8,24,17,0.72)) !important;
        border: 1px solid rgba(148,163,184,0.14) !important;
        border-radius: 20px !important;
        box-shadow: 0 15px 40px rgba(0,0,0,0.20);
        padding: 10px !important;
    }

    .stMarkdown, .stMarkdown p, .stMarkdown li {
        color: #cbd5e1;
    }

    label {
        color: #cbd5e1 !important;
    }

    @media(max-width:900px) {
        .hero-title { font-size: 38px; }
        .detect-title { font-size: 30px; }
        .block-container { padding-left: 4%; padding-right: 4%; }
    }
    </style>
    """
)

# ============================================================
# LOAD YOLO MODEL
# Put best.pt in the same folder as app.py
# ============================================================

@st.cache_resource
def load_model():
    model_path = os.path.join(os.path.dirname(__file__), "best.pt")
    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"best.pt not found. Put best.pt in the same folder as app.py.\nPath: {model_path}"
        )
    return YOLO(model_path)

# ============================================================
# CLASS HELPERS
# ============================================================

def normalize_class_name(name):
    return str(name).lower().strip().replace("_", "-").replace(" ", "-")

def is_overflow(name, confidence):
    normalized = normalize_class_name(name)
    return normalized in {"overflow", "garbage-overflow"} and confidence >= OVERFLOW_CONFIDENCE

def is_throwing(name, confidence):
    normalized = normalize_class_name(name)
    return normalized in {
        "person-throwing-garbage",
        "person-throwing",
        "throwing-garbage",
    } and confidence >= THROWING_CONFIDENCE

def extract_detections(result):
    detections = []

    if result.boxes is None:
        return detections

    for box in result.boxes:
        class_id = int(box.cls[0])
        confidence = float(box.conf[0])

        name = str(result.names[class_id])

        x1, y1, x2, y2 = map(
            int,
            box.xyxy[0].tolist()
        )

        overflow = is_overflow(name, confidence)
        throwing = is_throwing(name, confidence)

        detections.append({
            "name": name,
            "confidence": confidence,
            "box": (x1, y1, x2, y2),
            "overflow": overflow,
            "throwing": throwing,
            "alert": overflow or throwing,
        })

    return detections

def get_alerts(detections):
    alerts = []

    for detection in detections:
        if detection["alert"]:
            alerts.append(
                (
                    detection["name"],
                    detection["confidence"],
                    detection["overflow"],
                    detection["throwing"],
                )
            )

    return alerts

# ============================================================
# DRAW CUSTOM BOXES
# ============================================================

def draw_custom_boxes(frame, detections):
    output = frame.copy()

    for detection in detections:
        name = detection["name"]
        confidence = detection["confidence"]
        x1, y1, x2, y2 = detection["box"]

        if detection["overflow"]:
            color = (40, 40, 255)          # red
        elif detection["throwing"]:
            color = (0, 165, 255)          # orange
        else:
            color = (0, 220, 120)          # green

        cv2.rectangle(
            output,
            (x1, y1),
            (x2, y2),
            color,
            3
        )

        label = f"{name} {confidence * 100:.1f}%"

        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.55
        thickness = 2

        (tw, th), _ = cv2.getTextSize(
            label,
            font,
            font_scale,
            thickness
        )

        label_y = max(y1, th + 10)

        cv2.rectangle(
            output,
            (x1, label_y - th - 10),
            (x1 + tw + 10, label_y),
            color,
            -1
        )

        cv2.putText(
            output,
            label,
            (x1 + 5, label_y - 5),
            font,
            font_scale,
            (255, 255, 255),
            thickness,
            cv2.LINE_AA
        )

    return output

# ============================================================
# LOCATION
# ============================================================

def get_live_location():
    js_code = """
    (async () => {
        try {
            if (!navigator.geolocation) {
                return "LOCATION_NOT_SUPPORTED";
            }

            const position = await new Promise((resolve, reject) => {
                navigator.geolocation.getCurrentPosition(
                    resolve,
                    reject,
                    {
                        enableHighAccuracy: true,
                        timeout: 10000,
                        maximumAge: 0
                    }
                );
            });

            return JSON.stringify({
                latitude: position.coords.latitude,
                longitude: position.coords.longitude
            });

        } catch(error) {
            return "LOCATION_ERROR:" + error.message;
        }
    })();
    """

    try:
        from streamlit_js_eval import streamlit_js_eval
        return streamlit_js_eval(
            js_expressions=js_code,
            want_output=True,
            key="location_request"
        )
    except Exception as e:
        return "LOCATION_ERROR:" + str(e)

def reverse_geocode(latitude, longitude):
    """
    Converts GPS coordinates into a readable area/place name.
    Uses OpenStreetMap Nominatim.
    """
    try:
        response = requests.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={
                "lat": latitude,
                "lon": longitude,
                "format": "jsonv2",
                "zoom": 18,
                "addressdetails": 1,
            },
            headers={
                "User-Agent": "EcoBin-AI/1.0"
            },
            timeout=10,
        )

        if response.status_code != 200:
            return None

        data = response.json()
        address = data.get("address", {})

        area = (
            address.get("suburb")
            or address.get("neighbourhood")
            or address.get("village")
            or address.get("town")
            or address.get("city")
            or address.get("municipality")
            or address.get("county")
        )

        state = address.get("state")
        country = address.get("country")

        parts = [x for x in [area, state, country] if x]

        if parts:
            return ", ".join(parts)

        return data.get("display_name")

    except Exception:
        return None

def enable_location():
    location_result = get_live_location()

    if (
        isinstance(location_result, str)
        and location_result.startswith("{")
    ):
        try:
            location_data = json.loads(location_result)

            latitude = float(location_data["latitude"])
            longitude = float(location_data["longitude"])

            st.session_state.location = {
                "latitude": latitude,
                "longitude": longitude,
            }

            area_name = reverse_geocode(latitude, longitude)
            st.session_state.location_name = area_name

            return True

        except Exception as e:
            st.session_state.location_name = None
            st.warning(f"Location data could not be read: {e}")
            return False

    st.warning(
        "Location permission was not available. "
        "Please allow location access in your browser."
    )
    return False

# ============================================================
# EMAIL ALERT
# ============================================================

def send_email_alert(alerts, source="image", location_data=None, location_name=None):
    try:
        required = [
            "EMAIL_SENDER",
            "EMAIL_PASSWORD",
            "EMAIL_RECEIVER",
        ]

        missing = [
            key for key in required
            if key not in st.secrets
        ]

        if missing:
            st.session_state.email_error = (
                "Missing Streamlit secrets: " + ", ".join(missing)
            )
            return False

        sender = st.secrets["EMAIL_SENDER"]
        password = st.secrets["EMAIL_PASSWORD"]
        receiver = st.secrets["EMAIL_RECEIVER"]

        now = datetime.now(ZoneInfo("Asia/Kolkata"))

        date_text = now.strftime("%d-%b-%Y")
        time_text = now.strftime("%I:%M:%S %p")

        alert_names = sorted(
            set(
                name for name, confidence, overflow, throwing in alerts
            )
        )

        alert_text = ", ".join(alert_names)

        if location_data:
            latitude = location_data["latitude"]
            longitude = location_data["longitude"]

            maps_link = (
                "https://www.google.com/maps/search/?api=1&query="
                f"{latitude},{longitude}"
            )

            location_text = (
                f"Area / Location : {location_name or 'Area name unavailable'}\n"
                f"Latitude        : {latitude:.6f}\n"
                f"Longitude       : {longitude:.6f}\n"
                f"Google Maps     : {maps_link}"
            )
        else:
            location_text = "Location : Not available"

        subject = f"🚨 EcoBin AI Alert | {alert_text}"

        body = f"""
ECOBIN AI
AI-POWERED SMART GARBAGE MONITORING SYSTEM
================================================

🚨 GARBAGE SAFETY ALERT DETECTED

EcoBin AI has detected a garbage-related event that
requires attention.

------------------------------------------------
DETECTION DETAILS
------------------------------------------------

Detected        : {alert_text}
Detection Source: {source}
Date            : {date_text}
Time            : {time_text}

------------------------------------------------
LOCATION
------------------------------------------------

{location_text}

------------------------------------------------
RECOMMENDED ACTION
------------------------------------------------

Please verify the garbage bin / waste area immediately.

If OVERFLOW is detected:
• Check the bin condition.
• Arrange garbage collection if required.
• Prevent further waste accumulation.

If PERSON_THROWING_GARBAGE is detected:
• Verify the activity.
• Take appropriate cleanliness / awareness action.

------------------------------------------------

EcoBin AI
Smart Garbage Overflow Detection System

Automatically generated alert.
"""

        message = EmailMessage()
        message["From"] = sender
        message["To"] = receiver
        message["Subject"] = subject
        message.set_content(body)

        with smtplib.SMTP("smtp.gmail.com", 587, timeout=20) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(sender, password)
            server.send_message(message)

        st.session_state.email_error = None
        return True

    except Exception as e:
        st.session_state.email_error = str(e)
        return False

# ============================================================
# ALERT COOLDOWN
# ============================================================

def can_send_alert(alert_key):
    now = datetime.now(ZoneInfo("Asia/Kolkata"))
    last_time = st.session_state.last_alert_time

    if last_time is None:
        return True

    if st.session_state.last_alert_key != alert_key:
        return True

    return (now - last_time) >= timedelta(
        minutes=ALERT_COOLDOWN_MINUTES
    )

def handle_alert(alerts, source="image"):
    if not alerts:
        return False

    alert_names = sorted(
        set(name for name, confidence, overflow, throwing in alerts)
    )

    alert_key = (source, tuple(alert_names))

    if not can_send_alert(alert_key):
        return False

    if st.session_state.location is None:
        try:
            enable_location()
        except Exception:
            pass

    success = send_email_alert(
        alerts=alerts,
        source=source,
        location_data=st.session_state.location,
        location_name=st.session_state.location_name,
    )

    if success:
        st.session_state.last_alert_time = datetime.now(
            ZoneInfo("Asia/Kolkata")
        )
        st.session_state.last_alert_key = alert_key
        st.success(
            f"📧 EcoBin AI alert sent successfully. "
            f"Next same alert is allowed after {ALERT_COOLDOWN_MINUTES} minutes."
        )
        return True

    st.error("❌ Alert could not be sent.")
    if st.session_state.email_error:
        st.caption("Email error: " + st.session_state.email_error)

    return False

# ============================================================
# DISPLAY ALERT / SAFE BOX
# ============================================================

def display_alert_box(alerts):
    if not alerts:
        return

    names = []
    for name, confidence, overflow, throwing in alerts:
        if name not in names:
            names.append(name)

    text = ", ".join(names)

    has_overflow = any(x[2] for x in alerts)
    has_throwing = any(x[3] for x in alerts)

    if has_overflow:
        title = "🚨 GARBAGE OVERFLOW DETECTED"
        extra = "🔴 Red bounding box indicates an overflowing bin."
    elif has_throwing:
        title = "⚠️ PERSON THROWING GARBAGE DETECTED"
        extra = "🟠 Orange bounding box indicates garbage-throwing activity."
    else:
        title = "⚠️ GARBAGE EVENT DETECTED"
        extra = "Please verify the detected area."

    render_html(
        f"""
        <div class="overflow-box">
            <div class="overflow-title">{title}</div>
            <div class="overflow-text">
                Detected: <strong>{text}</strong>
            </div>
            <div class="overflow-text">{extra}</div>
        </div>
        """
    )

def display_safe_box():
    render_html(
        """
        <div class="safe-box">
            🟢 SAFE — No garbage overflow detected.
        </div>
        """
    )

def display_warning_box():
    render_html(
        """
        <div class="warning-box">
            🟡 PERSON THROWING GARBAGE DETECTED — Please verify the activity.
        </div>
        """
    )

# ============================================================
# HOME PAGE
# ============================================================

if st.session_state.page == "home":

    render_html(
        """
        <div class="home-hero">
            <div class="hero-badge">♻️ AI-POWERED SMART WASTE MONITORING</div>
            <div class="hero-title">♻️ EcoBin AI</div>
            <div class="hero-subtitle">
                AI-Powered Garbage Overflow Detection System
            </div>
        </div>
        """
    )

    left_col, right_col = st.columns([0.40, 0.60], gap="large")

    with left_col:
        render_html(
            """
            <div class="home-card aicw-card">
                <div class="aicw-icon">♻️</div>
                <div class="aicw-title">EcoBin AI</div>
                <div class="aicw-subtitle">
                    Smart Garbage Monitoring
                </div>
                <div class="capstone">
                    🚀 YOLOv8 • Real-Time Detection • Smart Alerts
                </div>
            </div>
            """
        )

        st.write("")

        if st.button("🔍 START PREDICTION", key="home_predict_button"):
            st.session_state.page = "predict"
            st.rerun()

    with right_col:
        render_html(
            """
            <div class="home-card">
                <div class="about-title">♻️ What is EcoBin AI?</div>
                <div class="about-text">
                    EcoBin AI is an AI-based smart waste monitoring system
                    designed to detect garbage-bin overflow automatically.
                    <br><br>
                    The YOLOv8 computer vision model analyses images,
                    camera captures and videos to identify:
                    <br><br>
                    🟢 Normal bin condition<br>
                    🔴 Garbage Overflow<br>
                    🟠 Person Throwing Garbage
                    <br><br>
                    🚨 When an important event is confirmed, the system
                    can send an automatic Gmail alert with the current
                    area/location and Google Maps information.
                </div>
            </div>
            """
        )

    st.write("")
    st.write("")

    render_html(
        """
        <div class="team-heading">👩🏻‍💻 Our Team</div>
        """
    )

    c1, c2, c3, c4 = st.columns(4, gap="medium")

    team = [
        ("👩🏻‍💻", "Y.D.V.Sivani", "AI / ML"),
        ("👩🏻‍💻", "V.L.S.Asritha", "AI / ML"),
        ("👩🏻‍💻", "R.Likhitha", "Development"),
        ("👩🏻‍💻", "S.Poojitha Sri", "Development"),
    ]

    for col, (avatar, name, role) in zip([c1, c2, c3, c4], team):
        with col:
            render_html(
                f"""
                <div class="team-card">
                    <div class="avatar">{avatar}</div>
                    <div class="member-name">{name}</div>
                    <div class="member-role">{role}</div>
                </div>
                """
            )

    st.write("")
    st.write("")

    render_html(
        """
        <div class="guide-card">
            <div style="display:flex;align-items:center;gap:18px;">
                <div class="avatar" style="margin:0;">👨🏻‍🏫</div>
                <div>
                    <div class="member-name" style="font-size:18px;">
                        MD. Abdul Aziz
                    </div>
                    <div class="member-role" style="font-size:13px;">
                        Trainer • Co-Lead – AICW
                    </div>
                </div>
            </div>
        </div>
        """
    )

    render_html(
        """
        <div class="footer">
            ♻️ EcoBin AI • Building Cleaner Communities with AI
        </div>
        """
    )

# ============================================================
# PREDICTION PAGE
# ============================================================

elif st.session_state.page == "predict":

    render_html(
        """
        <div class="detect-title">♻️ EcoBin AI</div>
        <div class="detect-subtitle">
            AI-Powered Garbage Overflow Detection
            • Visual Alerts • Gmail Alerts • Live Location
        </div>
        """
    )

    # --------------------------------------------------------
    # MODEL
    # --------------------------------------------------------

    try:
        model = load_model()
    except Exception as e:
        st.error("❌ best.pt model load avvaledu.")
        st.info("best.pt file app.py same folder lo undali.")
        st.caption(str(e))
        st.stop()

    with st.container(border=True):
        render_html(
            """
            <div class="card-title">🤖 EcoBin AI Vision Model</div>
            """
        )

        st.markdown(
            """
            🟢 **Normal** &nbsp;&nbsp;
            🔴 **Overflow** &nbsp;&nbsp;
            🟠 **Person Throwing Garbage**
            """
        )

        st.caption(
            f"General confidence: {GENERAL_CONFIDENCE:.2f} | "
            f"Overflow threshold: {OVERFLOW_CONFIDENCE:.2f} | "
            f"Video confirmation: {OVERFLOW_CONFIRM_FRAMES} consecutive frames"
        )

    st.write("")

    # --------------------------------------------------------
    # EMAIL STATUS
    # --------------------------------------------------------

    with st.container(border=True):
        st.markdown("### 📧 Gmail Alerts")

        if (
            "EMAIL_SENDER" in st.secrets
            and "EMAIL_PASSWORD" in st.secrets
            and "EMAIL_RECEIVER" in st.secrets
        ):
            st.success("🟢 Gmail is configured.")
        else:
            st.warning("🟡 Gmail is not configured.")
            st.caption(
                "Add EMAIL_SENDER, EMAIL_PASSWORD and EMAIL_RECEIVER "
                "in Streamlit Secrets."
            )

    st.write("")

    # --------------------------------------------------------
    # LIVE LOCATION
    # --------------------------------------------------------

    with st.container(border=True):
        st.markdown("### 📍 Live Detection Location")

        st.write(
            "Enable location to automatically convert GPS coordinates "
            "into a readable area name for the alert."
        )

        if st.button("📍 Enable Live Location", key="location_button"):
            with st.spinner("Getting current location..."):
                enable_location()

        if st.session_state.location:
            latitude = st.session_state.location["latitude"]
            longitude = st.session_state.location["longitude"]
            area_name = st.session_state.location_name

            if area_name:
                st.success(f"📍 Area: {area_name}")
            else:
                st.info("📍 Area name could not be resolved.")

            st.caption(
                f"GPS: {latitude:.6f}, {longitude:.6f}"
            )

            maps_link = (
                "https://www.google.com/maps/search/?api=1&query="
                f"{latitude},{longitude}"
            )

            st.markdown(
                f"[🗺️ Open current location in Google Maps]({maps_link})"
            )

    st.write("")

    # --------------------------------------------------------
    # BACK
    # --------------------------------------------------------

    if st.button("← Back to Home", key="prediction_back_button"):
        st.session_state.page = "home"
        st.rerun()

    st.write("")

    # --------------------------------------------------------
    # INPUT SELECTOR
    # --------------------------------------------------------

    input_type = st.radio(
        "Choose Detection Mode",
        [
            "🖼️ Image",
            "📷 Camera",
            "🎥 Video",
        ],
        horizontal=True,
        key="input_type_selector",
    )

    # ========================================================
    # IMAGE
    # ========================================================

    if input_type == "🖼️ Image":

        input_col, result_col = st.columns(2, gap="large")

        with input_col:
            with st.container(border=True):

                st.markdown("### 📸 Upload Garbage Image")

                uploaded_image = st.file_uploader(
                    "Choose image",
                    type=["jpg", "jpeg", "png"],
                    key="image_upload",
                )

                if uploaded_image:
                    image = Image.open(uploaded_image).convert("RGB")

                    st.image(
                        image,
                        caption="Original Image",
                        use_container_width=True,
                    )

                    if st.button(
                        "🔍 Detect Garbage",
                        key="image_detect_button",
                    ):

                        with st.spinner("🔎 AI is analysing the image..."):
                            result = model.predict(
                                np.array(image),
                                conf=GENERAL_CONFIDENCE,
                                verbose=False,
                            )[0]

                        frame = np.array(image)

                        detections = extract_detections(result)
                        annotated = draw_custom_boxes(frame, detections)
                        alerts = get_alerts(detections)

                        st.session_state.result_image = annotated
                        st.session_state.detections = detections
                        st.session_state.image_alerts = alerts
                        st.session_state.last_alert_key = None

                        if alerts:
                            handle_alert(alerts, "image")

        with result_col:
            with st.container(border=True):

                st.markdown("### 🎯 Detection Result")

                if st.session_state.result_image is None:
                    st.info(
                        "Upload an image and click Detect Garbage."
                    )
                else:
                    st.image(
                        st.session_state.result_image,
                        caption="EcoBin AI Result",
                        use_container_width=True,
                    )

                    alerts = st.session_state.image_alerts

                    if alerts:
                        has_overflow = any(x[2] for x in alerts)
                        has_throwing = any(x[3] for x in alerts)

                        display_alert_box(alerts)

                        if has_overflow:
                            st.error(
                                "🚨 Overflow detected — garbage collection attention required."
                            )

                        if has_throwing:
                            st.warning(
                                "⚠️ Person throwing garbage detected — verify the activity."
                            )
                    else:
                        display_safe_box()

                    detections = st.session_state.detections

                    if detections:
                        st.markdown("### 🔎 Detected Objects")

                        for detection in detections:
                            name = detection["name"]
                            confidence = detection["confidence"]

                            if detection["overflow"]:
                                st.markdown(
                                    f"🔴 **{name}** — {confidence * 100:.1f}%"
                                )
                            elif detection["throwing"]:
                                st.markdown(
                                    f"🟠 **{name}** — {confidence * 100:.1f}%"
                                )
                            else:
                                st.markdown(
                                    f"🟢 **{name}** — {confidence * 100:.1f}%"
                                )

    # ========================================================
    # CAMERA
    # ========================================================

    elif input_type == "📷 Camera":

        with st.container(border=True):

            st.markdown("### 📷 Live Camera Capture")

            camera_image = st.camera_input(
                "Take a photo",
                key="camera_input",
            )

            if camera_image:

                image = Image.open(camera_image).convert("RGB")

                if st.button(
                    "🔍 Analyse Camera Image",
                    key="camera_detect_button",
                ):

                    with st.spinner("Analysing..."):
                        result = model.predict(
                            np.array(image),
                            conf=GENERAL_CONFIDENCE,
                            verbose=False,
                        )[0]

                    frame = np.array(image)

                    detections = extract_detections(result)
                    annotated = draw_custom_boxes(frame, detections)
                    alerts = get_alerts(detections)

                    st.image(
                        annotated,
                        caption="EcoBin AI Camera Result",
                        use_container_width=True,
                    )

                    if alerts:
                        display_alert_box(alerts)
                        handle_alert(alerts, "camera image")
                    else:
                        display_safe_box()

                    if detections:
                        st.markdown("### 🔎 Detected Objects")

                        for detection in detections:
                            name = detection["name"]
                            confidence = detection["confidence"]

                            if detection["overflow"]:
                                st.markdown(
                                    f"🔴 **{name}** — {confidence * 100:.1f}%"
                                )
                            elif detection["throwing"]:
                                st.markdown(
                                    f"🟠 **{name}** — {confidence * 100:.1f}%"
                                )
                            else:
                                st.markdown(
                                    f"🟢 **{name}** — {confidence * 100:.1f}%"
                                )

    # ========================================================
    # VIDEO
    # ========================================================

    elif input_type == "🎥 Video":

        with st.container(border=True):

            st.markdown("### 🎥 Garbage Video Analysis")

            uploaded_video = st.file_uploader(
                "Upload video",
                type=["mp4", "avi", "mov", "mkv"],
                key="video_upload",
            )

            if uploaded_video:

                st.video(uploaded_video)

                if st.button(
                    "🎥 Analyse Entire Video",
                    key="video_detect_button",
                ):

                    with st.spinner(
                        "🎬 Processing video... Please wait."
                    ):

                        input_file = tempfile.NamedTemporaryFile(
                            delete=False,
                            suffix=".mp4",
                        )

                        input_file.write(
                            uploaded_video.getbuffer()
                        )
                        input_file.close()

                        cap = cv2.VideoCapture(input_file.name)

                        fps = cap.get(cv2.CAP_PROP_FPS)
                        if fps <= 0:
                            fps = 20

                        width = int(
                            cap.get(cv2.CAP_PROP_FRAME_WIDTH)
                        )
                        height = int(
                            cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
                        )

                        if width <= 0 or height <= 0:
                            cap.release()
                            os.remove(input_file.name)
                            st.error(
                                "❌ Video dimensions could not be read."
                            )
                            st.stop()

                        output_file = tempfile.NamedTemporaryFile(
                            delete=False,
                            suffix=".mp4",
                        )
                        output_path = output_file.name
                        output_file.close()

                        # mp4v is broadly supported by OpenCV.
                        fourcc = cv2.VideoWriter_fourcc(*"mp4v")

                        writer = cv2.VideoWriter(
                            output_path,
                            fourcc,
                            fps,
                            (width, height),
                        )

                        if not writer.isOpened():
                            cap.release()
                            os.remove(input_file.name)
                            st.error(
                                "❌ Video writer could not be opened."
                            )
                            st.stop()

                        video_alert_names = set()

                        # Overflow confirmation logic
                        consecutive_overflow_frames = 0
                        overflow_confirmed = False

                        # Person throwing can be reported separately.
                        throwing_detected = False

                        frame_count = 0
                        total_frames = int(
                            cap.get(cv2.CAP_PROP_FRAME_COUNT)
                        )

                        progress = st.progress(0)

                        while True:

                            ret, frame = cap.read()

                            if not ret:
                                break

                            frame_count += 1

                            result = model.predict(
                                frame,
                                conf=GENERAL_CONFIDENCE,
                                verbose=False,
                            )[0]

                            detections = extract_detections(result)

                            annotated = draw_custom_boxes(
                                frame,
                                detections,
                            )

                            writer.write(annotated)

                            frame_overflow = any(
                                d["overflow"]
                                for d in detections
                            )

                            frame_throwing = any(
                                d["throwing"]
                                for d in detections
                            )

                            if frame_overflow:
                                consecutive_overflow_frames += 1
                            else:
                                consecutive_overflow_frames = 0

                            if (
                                consecutive_overflow_frames
                                >= OVERFLOW_CONFIRM_FRAMES
                            ):
                                overflow_confirmed = True
                                video_alert_names.add("Overflow")

                            if frame_throwing:
                                throwing_detected = True
                                video_alert_names.add(
                                    "Person_Throwing_Garbage"
                                )

                            if total_frames > 0:
                                progress.progress(
                                    min(
                                        frame_count / total_frames,
                                        1.0,
                                    )
                                )

                        cap.release()
                        writer.release()

                        try:
                            os.remove(input_file.name)
                        except Exception:
                            pass

                    st.success("✅ Video processing completed!")

                    st.video(output_path)

                    final_alerts = []

                    if overflow_confirmed:
                        final_alerts.append(
                            (
                                "Overflow",
                                1.0,
                                True,
                                False,
                            )
                        )

                    if throwing_detected:
                        final_alerts.append(
                            (
                                "Person_Throwing_Garbage",
                                1.0,
                                False,
                                True,
                            )
                        )

                    if final_alerts:

                        display_alert_box(final_alerts)

                        if overflow_confirmed:
                            st.error(
                                f"🚨 Overflow confirmed in at least "
                                f"{OVERFLOW_CONFIRM_FRAMES} consecutive frames."
                            )

                        if throwing_detected:
                            st.warning(
                                "⚠️ Person throwing garbage was detected "
                                "during the video."
                            )

                        # One alert for the whole video.
                        handle_alert(
                            final_alerts,
                            "video",
                        )

                    else:
                        display_safe_box()

    # --------------------------------------------------------
    # FOOTER
    # --------------------------------------------------------

    render_html(
        """
        <div class="footer">
            ♻️ EcoBin AI • AI-Powered Garbage Overflow Detection
        </div>
        """
    )
