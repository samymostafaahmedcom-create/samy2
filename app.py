import string
import secrets
import streamlit as st
from datetime import datetime
from io import BytesIO
import qrcode

# ================== PAGE CONFIG ==================
st.set_page_config(
    page_title="Secure Password Generator",
    page_icon="🔐",
    layout="wide"
)

# ================== THEME ==================
PRIMARY = "#0F172A"
SUCCESS = "#22C55E"
DANGER = "#DC2626"
WARNING = "#F97316"
INFO = "#EAB308"
BG = "#F8FAFC"
CARD = "#FFFFFF"
BORDER = "#E5E7EB"
MUTED = "#64748B"

# ================== SESSION ==================
st.session_state.setdefault("password", "")
st.session_state.setdefault("history", [])
st.session_state.setdefault("copied", False)
st.session_state.setdefault("show_all_history", False)
st.session_state.setdefault("show_qr", False)

# ================== FUNCTIONS ==================
def generate_password(length, chars):
    return "".join(secrets.choice(chars) for _ in range(length))

def strength(password):
    score = 0
    score += len(password) >= 12
    score += any(c.islower() for c in password)
    score += any(c.isupper() for c in password)
    score += any(c.isdigit() for c in password)
    score += any(c in "!@#$%^&*_" for c in password)
    return score

def strength_label(score):
    labels = ["Very Weak", "Weak", "Medium", "Strong", "Very Strong"]
    return labels[min(score, len(labels) - 1)]

def strength_color(score):
    if score <= 1:
        return DANGER
    elif score == 2:
        return WARNING
    elif score == 3:
        return INFO
    else:
        return SUCCESS

def generate_qr(data):
    qr = qrcode.QRCode(box_size=4, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf

# ================== STYLE ==================
st.markdown(f"""
<style>
.stApp {{
    background: {BG};
    font-family: Inter, sans-serif;
}}
.card {{
    background: {CARD};
    border: 1px solid {BORDER};
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 16px;
}}
.title {{
    font-size: 20px;
    font-weight: 600;
}}
.muted {{
    color: {MUTED};
    font-size: 14px;
}}
.password-box {{
    background: {PRIMARY};
    color: white;
    padding: 16px;
    border-radius: 14px;
    font-size: 22px;
    font-weight: 600;
    text-align: center;
}}
.strength-bar {{
    height: 8px;
    background: {BORDER};
    border-radius: 10px;
    overflow: hidden;
    margin-top: 4px;
}}
.strength-fill {{
    height: 100%;
}}
</style>
""", unsafe_allow_html=True)

# ================== HEADER ==================
st.markdown("## 🔐 Secure Password Generator")
st.markdown("<div class='muted'>Premium password generation experience</div>", unsafe_allow_html=True)
st.divider()

# ================== LAYOUT ==================
settings, generate, result, history = st.columns([1.2, 1.4, 2, 2])

# ================== SETTINGS ==================
with settings:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='title'>Settings</div>", unsafe_allow_html=True)

    upper = st.checkbox("Uppercase (A-Z)", True)
    lower = st.checkbox("Lowercase (a-z)", True)
    digits = st.checkbox("Numbers (0-9)", True)
    symbols = st.checkbox("Symbols", True)
    exclude = st.checkbox("Eliminate similarities (O,0,l,I)")

    length = st.slider("Password length", 8, 64, 16)
    batch = st.slider("Number of passwords", 1, 10, 1)

    st.markdown("</div>", unsafe_allow_html=True)

# ================== GENERATE ==================
with generate:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='title'>Generate</div>", unsafe_allow_html=True)

    if st.button("Generate Password(s)", use_container_width=True):
        chars = ""
        if upper: chars += string.ascii_uppercase
        if lower: chars += string.ascii_lowercase
        if digits: chars += string.digits
        if symbols: chars += "!@#$%^&*_"

        if exclude:
            chars = "".join(c for c in chars if c not in "0Ool1I")

        if not chars:
            st.warning("Please select at least one character type")
        else:
            for _ in range(batch):
                pwd = generate_password(length, chars)
                st.session_state.password = pwd
                st.session_state.history.insert(0, {
                    "pwd": pwd,
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
            st.session_state.show_qr = False

    st.markdown("</div>", unsafe_allow_html=True)

# ================== RESULT ==================
with result:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='title'>Result</div>", unsafe_allow_html=True)

    if st.session_state.password:
        pwd = st.session_state.password
        score = strength(pwd)
        width = min(score, 5) * 20
        color = strength_color(score)

        st.markdown(f"<div class='password-box'>{pwd}</div>", unsafe_allow_html=True)

        if st.button("Copy Password"):
            st.session_state.copied = True

        if st.session_state.copied:
            st.code(pwd)
            st.success("Copied ✓")
            st.session_state.copied = False

        st.markdown(f"**Strength:** {strength_label(score)}")
        st.markdown(f"""
        <div class="strength-bar">
            <div class="strength-fill" style="width:{width}%; background:{color};"></div>
        </div>
        """, unsafe_allow_html=True)

        st.session_state.show_qr = st.checkbox("Show QR", value=st.session_state.show_qr)
        if st.session_state.show_qr:
            st.image(generate_qr(pwd), width=120)

    st.markdown("</div>", unsafe_allow_html=True)

# ================== HISTORY ==================
with history:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown(f"<div class='title'>History ({len(st.session_state.history)})</div>", unsafe_allow_html=True)

    search = st.text_input("Search", placeholder="password or date")

    history_list = st.session_state.history
    if search:
        history_list = [
            h for h in history_list
            if search.lower() in h["pwd"].lower()
            or search.lower() in h["time"].lower()
        ]

    show_all = st.session_state.show_all_history
    visible = history_list if show_all else history_list[:3]

    for i, item in enumerate(visible):
        masked = item["pwd"][:4] + "••••" + item["pwd"][-2:]
        col1, col2, col3 = st.columns([3, 1, 1])

        with col1:
            st.code(masked)
            st.caption(item["time"])

        with col2:
            if st.button("Copy", key=f"copy_{i}"):
                st.code(item["pwd"])
                st.success("Copied ✓")

        with col3:
            if st.checkbox("QR", key=f"qr_{i}"):
                st.image(generate_qr(item["pwd"]), width=100)

    if len(history_list) > 3:
        if st.button("Show less ▲" if show_all else "Show more ▼", use_container_width=True):
            st.session_state.show_all_history = not show_all

    if st.button("Clear History", use_container_width=True):
        st.session_state.history.clear()

    st.markdown("</div>", unsafe_allow_html=True)

# ================== TEST ==================
st.divider()
st.markdown("### 🧪 Test Password Strength")

show = st.toggle("Show password")
test = st.text_input("Enter password", type="text" if show else "password")

if test:
    score = strength(test)
    width = min(score, 5) * 20
    color = strength_color(score)

    st.markdown(f"**Strength:** {strength_label(score)}")
    st.markdown(f"""
    <div class="strength-bar">
        <div class="strength-fill" style="width:{width}%; background:{color};"></div>
    </div>
    """, unsafe_allow_html=True)
