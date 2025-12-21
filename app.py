import streamlit as st
import json
import os
import pandas as pd

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="GreenBasket", layout="wide")

USER_FILE = "users.json"

# ---------------- THEME & COLOR LOGIC ----------------
if "bg_color" not in st.session_state:
    st.session_state.bg_color = "#e8f5e9"

def get_text_color(hex_color):
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    brightness = (r * 0.299 + g * 0.587 + b * 0.114)
    return "black" if brightness > 128 else "white"

def set_appearance(bg_color):
    text_color = get_text_color(bg_color)
    
    st.markdown(
        f"""
        <style>
        /* 1. UNIVERSAL FORCE - THIS TARGETS EVERY ELEMENT */
        * {{
            color: {text_color} !important;
        }}

        /* 2. APP BACKGROUND */
        .stApp, [data-testid="stAppViewContainer"] {{
            background-color: {bg_color} !important;
        }}
        
        /* 3. INPUT BOX TEXT (TYPING FIX) */
        /* Targets the text typed, the placeholder, and the internal containers */
        input, textarea, [data-baseweb="input"] input {{
            color: {text_color} !important;
            -webkit-text-fill-color: {text_color} !important;
        }}

        /* Targets the faint placeholder text specifically */
        input::placeholder {{
            color: {text_color} !important;
            opacity: 0.7 !important;
        }}

        /* 4. BUTTONS */
        div.stButton > button {{
            color: {text_color} !important;
            background-color: transparent !important;
            border: 2px solid {text_color} !important;
            width: 100%;
        }}
        div.stButton > button:hover {{
            background-color: {text_color} !important;
            color: {bg_color} !important;
        }}

        /* 5. TABS (Login / Sign Up) */
        [data-baseweb="tab-list"] button {{
            border-bottom: 2px solid {text_color}44 !important;
        }}
        
        /* 6. DROPDOWN LIST TEXT (When you click a list) */
        /* We keep these black because the list background is usually white/pop-up style */
        div[role="listbox"] ul li {{
            color: black !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

set_appearance(st.session_state.bg_color)

# ---------------- DATA STORAGE ----------------
if not os.path.exists(USER_FILE):
    with open(USER_FILE, "w") as f:
        json.dump({}, f)

with open(USER_FILE, "r") as f:
    users = json.load(f)

def save_users():
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)

# ---------------- AUTH PAGE ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🌱 GreenBasket")
    t1, t2 = st.tabs(["Login", "Sign Up"])
    with t1:
        u_in = st.text_input("Username", key="l_user")
        p_in = st.text_input("Password", type="password", key="l_pass")
        if st.button("Login", key="l_btn"):
            if u_in in users and users[u_in]["password"] == p_in:
                st.session_state.logged_in = True
                st.session_state.user = u_in
                st.rerun()
            else: st.error("Invalid credentials")
    with t2:
        n_u = st.text_input("New Username", key="s_user")
        n_p = st.text_input("New Password", type="password", key="s_pass")
        n_h = st.text_input("Home City/Country", key="s_home")
        if st.button("Create Account", key="s_btn"):
            if n_u and n_p and n_h:
                users[n_u] = {"password": n_p, "display_name": n_u, "home_country": n_h, "purchases": []}
                save_users()
                st.success("Account created! Go to Login tab.")

# ---------------- MAIN APP ----------------
else:
    user = st.session_state.user
    profile = users[user]
    
    st.sidebar.markdown(f"👋 Hello, **{profile.get('display_name', user)}**")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    page = st.sidebar.radio("Navigate", ["Home", "Dashboard", "Settings"])

    if page == "Home":
        st.title("GreenBasket")
        st.write(f"Welcome back to your Eco-tracker!")

    elif page == "Dashboard":
        st.subheader("📊 Your Dashboard")
        if not profile.get("purchases"):
            st.info("No purchases recorded yet.")
        else:
            df = pd.DataFrame(profile["purchases"])
            st.dataframe(df, use_container_width=True)

    elif page == "Settings":
        st.subheader("⚙️ Settings")
        st.session_state.bg_color = st.color_picker("App Color", st.session_state.bg_color)
        if st.button("Apply Theme"):
            st.rerun()
