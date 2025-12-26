import string
import secrets
import streamlit as st
from datetime import datetime
import qrcode
from io import BytesIO

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
    img = qr.make_image(fill_color="#22c55e", back_color="white")
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
st.session_state.setdefault("show_qr", False)

# ================== STYLE ==================
st.markdown("""
<style>
.password-box {
    background: #020617;
    border-radius: 16px;
    padding: 16px;
    color: #38bdf8;
    font-size: 20px;
    font-weight: 600;
    word-break: break-all;
    border: 1px solid #1e293b;
    margin-bottom:12px;
}
</style>
""", unsafe_allow_html=True)

left, center, right = st.columns([1.2, 2, 2])

# ================== LEFT ==================
with left:
    st.subheader("⚙️ Settings")
    use_upper = st.checkbox("Uppercase", True)
    use_lower = st.checkbox("Lowercase", True)
    use_digit = st.checkbox("Numbers", True)
    use_symbols = st.checkbox("Symbols", False)
    exclude_similar = st.checkbox("Exclude similar")
    length = st.slider("Length", 4, 64, 16)
    num_passwords = st.number_input(
        "Number of passwords to generate",
        min_value=1, max_value=20, value=1, step=1
    )

# ================== CENTER ==================
with center:
    st.subheader("🔑 Generated Password")

    # ✅ أيقونة الكوبي المدمجة
    st.code(st.session_state.password or "Click Generate")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔁 Generate", use_container_width=True):
            for _ in range(num_passwords):
                generate_and_store_password(
                    length, use_upper, use_lower,
                    use_digit, use_symbols, exclude_similar
                )
            st.rerun()

    with col2:
        if st.button("🔳 Show / Hide QR", use_container_width=True):
            st.session_state.show_qr = not st.session_state.show_qr

    if st.session_state.password:
        score = password_strength(st.session_state.password)
        color = "#ef4444" if score <= 2 else "#facc15" if score == 3 else "#22c55e"

        st.markdown(f"**Strength:** {strength_label(score)}")
        st.markdown(f"""
        <div style="background:#334155;border-radius:8px;height:10px;">
            <div style="width:{score*20}%;background:{color};height:100%;border-radius:8px;"></div>
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.show_qr:
            st.image(generate_qr_image(st.session_state.password), width=120)

    # ================== TEST ==================
    st.subheader("🧪 Test Any Password")
    test_pwd = st.text_input("Enter password", type="password")
    if test_pwd:
        test_score = password_strength(test_pwd)
        test_color = "#ef4444" if test_score <= 2 else "#facc15" if test_score == 3 else "#22c55e"
        st.markdown(f"**Strength:** {strength_label(test_score)}")
        st.markdown(f"""
        <div style="background:#334155;border-radius:8px;height:10px;">
            <div style="width:{test_score*20}%;background:{test_color};height:100%;border-radius:8px;"></div>
        </div>
        """, unsafe_allow_html=True)

# ================== RIGHT ==================
with right:
    st.subheader("📜 History")

    if st.button("🗑️ Clear History"):
        st.session_state.password_history.clear()
        st.rerun()

    history = st.session_state.password_history
    show_all = st.session_state.show_all_history

    if history:
        latest = history[-1]
        st.code(latest["password"])
        st.caption(latest["time"])

        if st.button("🔳 QR Latest"):
            st.image(generate_qr_image(latest["password"]), width=70)

        rest = history[:-1]
        if rest and show_all:
            for item in reversed(rest):
                st.code(item["password"])
                st.caption(item["time"])
                st.image(generate_qr_image(item["password"]), width=60)

        if rest:
            if st.button("⬇️ Show More" if not show_all else "⬆️ Show Less"):
                st.session_state.show_all_history = not show_all
                st.rerun()
