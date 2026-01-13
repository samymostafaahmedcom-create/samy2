import string
import secrets
import streamlit as st
from datetime import datetime
from io import BytesIO
import qrcode

# ================== FUNCTIONS ==================
def generate_password(length, chars):
    return "".join(secrets.choice(chars) for _ in range(length))

def password_strength(password):
    score = 0
    if len(password) >= 12: score += 1
    if any(c.islower() for c in password): score += 1
    if any(c.isupper() for c in password): score += 1
    if any(c.isdigit() for c in password): score += 1
    if any(c in "!@#$%^&*_" for c in password): score += 1
    return score

def strength_label(score):
    return ["Very Weak", "Weak", "Medium", "Strong", "Very Strong"][max(score - 1, 0)]

def generate_qr_image(data):
    qr = qrcode.QRCode(version=1, box_size=5, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#000000", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf

def generate_and_store_password(length, use_upper, use_lower, use_digit, use_symbols, exclude_similar):
    chars = ""
    if use_upper: chars += string.ascii_uppercase
    if use_lower: chars += string.ascii_lowercase
    if use_digit: chars += string.digits
    if use_symbols: chars += "!@#$%^&*_-"

    if exclude_similar:
        chars = "".join(c for c in chars if c not in "0Ool1I")

    if not chars:
        st.warning("Select at least one character set.")
        return

    pwd = generate_password(length, chars)
    st.session_state.password = pwd
    st.session_state.password_history.append({
        "password": pwd,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

# ================== PAGE CONFIG ==================
st.set_page_config("Password Generator", "🔐", layout="wide")

# ================== SESSION ==================
st.session_state.setdefault("password", "")
st.session_state.setdefault("password_history", [])
st.session_state.setdefault("show_all_history", False)
st.session_state.setdefault("show_all_history_qr", False)
st.session_state.setdefault("show_qr", False)
st.session_state.setdefault("main_color", "#2563eb")

# ================== COLOR PICKER ==================
st.session_state.main_color = st.color_picker(
    "🎨 Choose main color",
    value=st.session_state.main_color
)

# ================== STYLE ==================
def set_style():
    main_color = st.session_state.main_color
    st.markdown(f"""
    <style>
    .stApp {{
        background-color: #ffffff;
        color: #0f172a;
        font-family: 'Inter', sans-serif;
    }}
    pre, code {{
        background-color: #f8fafc !important;
        color: {main_color} !important;
        border-radius: 12px !important;
        border: 1px solid #e2e8f0 !important;
        font-size: 16px !important;
        padding: 14px !important;
    }}
    </style>
    """, unsafe_allow_html=True)

set_style()

# ================== LAYOUT ==================
left, center, history_col, test_col = st.columns([1.2, 2, 2, 2])

# ================== LEFT ==================
with left:
    st.subheader("⚙️ Settings")
    use_upper = st.checkbox("Uppercase", True)
    use_lower = st.checkbox("Lowercase", True)
    use_digit = st.checkbox("Numbers", True)
    use_symbols = st.checkbox("Symbols", False)
    exclude_similar = st.checkbox("Exclude similar")
    length = st.slider("Length", 4, 64, 16)
    num_passwords = st.number_input("Number of passwords", 1, 100, 1)

# ================== CENTER ==================
with center:
    st.subheader("🔑 Generated Password")
    st.code(st.session_state.password or "Click Generate")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔁 Generate"):
            for _ in range(num_passwords):
                generate_and_store_password(
                    length, use_upper, use_lower,
                    use_digit, use_symbols, exclude_similar
                )

    with c2:
        if st.button("🔳 Show / Hide QR"):
            st.session_state.show_qr = not st.session_state.show_qr

    if st.session_state.password:
        score = password_strength(st.session_state.password)
        color = "#ef4444" if score <= 2 else "#facc15" if score == 3 else "#22c55e"

        st.markdown(f"**Strength:** {strength_label(score)}")
        st.markdown(f"""
        <div style="background:#e5e7eb;border-radius:8px;height:10px;">
            <div style="width:{score*20}%;background:{color};height:100%;border-radius:8px;"></div>
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.show_qr:
            st.image(generate_qr_image(st.session_state.password), width=120)

# ================== HISTORY ==================
with history_col:
    st.subheader("📜 History")

    if st.button("🗑️ Clear History"):
        st.session_state.password_history.clear()

    if st.button("👁️ Show All QR" if not st.session_state.show_all_history_qr else "🙈 Hide All QR"):
        st.session_state.show_all_history_qr = not st.session_state.show_all_history_qr

    history = st.session_state.password_history
    latest = history[-1:]  
    rest = history[:-1]

    for item in reversed(latest):
        st.code(item["password"])
        st.caption(item["time"])
        if st.session_state.show_all_history_qr:
            st.image(generate_qr_image(item["password"]), width=80)

    if rest and st.session_state.show_all_history:
        for item in reversed(rest):
            st.code(item["password"])
            st.caption(item["time"])
            if st.session_state.show_all_history_qr:
                st.image(generate_qr_image(item["password"]), width=80)

    if rest:
        if st.button("⬇️ Show More" if not st.session_state.show_all_history else "⬆️ Show Less"):
            st.session_state.show_all_history = not st.session_state.show_all_history

# ================== TEST COLUMN ==================
with test_col:
    st.subheader("🧪 Test Any Password")

    test_pwd = st.text_input("Enter password", type="password")
    if test_pwd:
        test_score = password_strength(test_pwd)
        test_color = "#ef4444" if test_score <= 2 else "#facc15" if test_score == 3 else "#22c55e"

        st.markdown(f"**Strength:** {strength_label(test_score)}")
        st.markdown(f"""
        <div style="background:#e5e7eb;border-radius:8px;height:10px;">
            <div style="width:{test_score*20}%;background:{test_color};height:100%;border-radius:8px;"></div>
        </div>
        """, unsafe_allow_html=True)
