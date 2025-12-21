import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime

# ---------------- 1. INITIAL SETTINGS ----------------
st.set_page_config(page_title="GreenBasket", layout="wide")
USER_FILE = "users.json"

if "bg_color" not in st.session_state:
    st.session_state.bg_color = "#e8f5e9"

def get_text_color(hex_color):
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    brightness = (r * 0.299 + g * 0.587 + b * 0.114)
    return "black" if brightness > 128 else "white"

def set_appearance(bg_color):
    text_color = get_text_color(bg_color)
    # Determine a button color that contrasts with the background
    # If the background is light, we use a darker version for the button.
    # If the background is dark, we use a lighter version/white for the button.
    btn_bg = "white" if text_color == "white" else "#1b5e20"
    btn_text = "black" if text_color == "white" else "white"

    st.markdown(f"""
        <style>
        /* MAIN APP & SIDEBAR BACKGROUND */
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stSidebar"] {{
            background-color: {bg_color} !important;
            color: {text_color} !important;
        }}

        /* SIDEBAR TEXT VISIBILITY */
        [data-testid="stSidebar"] *, 
        [data-testid="stSidebar"] p, 
        [data-testid="stSidebar"] span,
        [data-testid="stWidgetLabel"] p,
        [data-testid="stMarkdownContainer"] p {{
            color: {text_color} !important;
        }}

        /* COLOR PICKER OUTLINE FIX */
        div[data-testid="stColorPicker"] > div {{
            border: 3px solid {text_color} !important;
            border-radius: 12px !important;
            padding: 8px !important;
            display: inline-block !important;
            box-sizing: border-box !important;
        }}
        
        div[data-baseweb="color-picker"] {{
            border: none !important;
        }}

        /* --- THEMED BUTTONS FIX --- */
        div.stButton > button {{
            color: {btn_text} !important;
            background-color: {btn_bg} !important;
            border: 2px solid {text_color} !important;
            border-radius: 8px;
            font-weight: bold;
            transition: 0.3s;
        }}
        
        div.stButton > button:hover {{
            opacity: 0.8;
            border: 2px solid {btn_text} !important;
        }}

        /* LOGIN & INPUT BOXES */
        input, textarea, [data-baseweb="input"] {{
            background-color: #ffffff !important;
            color: #000000 !important;
            -webkit-text-fill-color: #000000 !important;
        }}

        /* RADIO SELECTION COLOR */
        div[data-testid="stMarkdownContainer"] div[role="radiogroup"] input[checked] + div {{
            background-color: {btn_bg} !important;
        }}
        </style>
    """, unsafe_allow_html=True)

set_appearance(st.session_state.bg_color)

# ---------------- 2. DATA STORAGE ----------------
if not os.path.exists(USER_FILE):
    with open(USER_FILE, "w") as f:
        json.dump({}, f)

with open(USER_FILE, "r") as f:
    users = json.load(f)

def save_users():
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)

IMPACT_MULTIPLIER = {"Clothing": 2.5, "Electronics": 4.0, "Groceries": 1.2, "Furniture": 3.0}
TRANSPORT_FACTOR = {"Air": 3.0, "Road": 1.5, "Rail": 1.0, "Sea": 0.8}
DISTANCE_FACTOR = {"Local (Same city)": 1.0, "Domestic": 1.3, "International": 1.8}

# ---------------- 3. AUTHENTICATION ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🌱 GreenBasket")
    t1, t2 = st.tabs(["Login", "Sign Up"])
    with t1:
        u_login = st.text_input("Username", key="l_u")
        p_login = st.text_input("Password", type="password", key="l_p")
        if st.button("Login"):
            if u_login in users and users[u_login]["password"] == p_login:
                st.session_state.logged_in = True
                st.session_state.user = u_login
                st.rerun()
            else: st.error("Invalid credentials")
    with t2:
        nu = st.text_input("New Username", key="s_u")
        np = st.text_input("New Password", type="password", key="s_p")
        nh = st.text_input("Home Location", key="s_h")
        if st.button("Create Account"):
            if nu and np:
                users[nu] = {"password": np, "home": nh, "purchases": []}
                save_users()
                st.success("Account created! Go to Login tab.")

# ---------------- 4. MAIN APP ----------------
else:
    user = st.session_state.user
    profile = users[user]
    
    st.sidebar.markdown(f"### 👋 {user}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    page = st.sidebar.radio("Menu", ["Home", "Add Purchase", "Dashboard", "Settings"])

    if page == "Home":
        st.title("🌍 Eco-Shopping Dashboard")
        st.write(f"Welcome back! You are tracking impact for: **{profile.get('home', 'Default')}**")

    elif page == "Add Purchase":
        st.subheader("➕ New Purchase")
        cat = st.selectbox("Category", list(IMPACT_MULTIPLIER.keys()))
        price = st.number_input("Price", min_value=0.0)
        origin = st.selectbox("Origin", list(DISTANCE_FACTOR.keys()))
        trans = st.selectbox("Transport", list(TRANSPORT_FACTOR.keys()))
        
        if st.button("Save Purchase"):
            score = price * IMPACT_MULTIPLIER[cat] * TRANSPORT_FACTOR[trans] * DISTANCE_FACTOR[origin]
            profile["purchases"].append({
                "date": datetime.now().strftime("%Y-%m-%d"),
                "item": cat, "price": price, "impact": round(score, 2)
            })
            save_users()
            st.success(f"Saved! Impact: {score:.2f} kg CO2")

    elif page == "Dashboard":
        st.subheader("📊 Your Statistics")
        if profile["purchases"]:
            df = pd.DataFrame(profile["purchases"])
            st.metric("Total CO2 Impact", f"{df['impact'].sum():.2f} kg")
            st.dataframe(df, use_container_width=True)
            st.bar_chart(df.set_index("date")["impact"])
        else: st.info("No data yet.")

    elif page == "Settings":
        st.subheader("⚙️ App Theme")
        new_bg = st.color_picker("Choose Color", st.session_state.bg_color)
        if st.button("Apply Theme"):
            st.session_state.bg_color = new_bg
            st.rerun()
