import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime
import random

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
        html, body, [data-testid="stAppViewContainer"], .stApp {{
            background-color: {bg_color} !important;
            color: {text_color} !important;
        }}
        input, textarea {{
            color: {text_color} !important;
            -webkit-text-fill-color: {text_color} !important;
            caret-color: {text_color} !important;
        }}
        label, .stMarkdown p, .stMarkdown h1, .stMarkdown h2 {{
            color: {text_color} !important;
        }}
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

# ---------------- SHOPIMPACT LOGIC (ADDED) ----------------
CO2_MULTIPLIER = {
    "Clothing": 1.5,
    "Electronics": 3.0,
    "Groceries": 0.8,
    "Furniture": 2.5,
    "Footwear": 1.8,
    "Second-hand": 0.4
}

GREEN_ALTERNATIVES = {
    "Clothing": ["Organic cotton brands", "Second-hand stores"],
    "Electronics": ["Energy Star devices", "Refurbished electronics"],
    "Groceries": ["Local produce", "Package-free stores"],
    "Furniture": ["Bamboo or recycled wood furniture"],
    "Footwear": ["Vegan leather brands"],
    "Second-hand": ["Reuse & thrift stores"]
}

ECO_TIPS = [
    "Buying second-hand greatly reduces CO₂ 🌍",
    "Local products reduce transport emissions 🚲",
    "Durable products reduce waste ♻️",
    "Repairing items saves resources 🌱"
]

def calculate_co2(price, product_type):
    return round(price * CO2_MULTIPLIER.get(product_type, 1), 2)

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
            else:
                st.error("Invalid credentials")

    with t2:
        n_u = st.text_input("New Username", key="s_user")
        n_p = st.text_input("New Password", type="password", key="s_pass")
        n_h = st.text_input("Home City/Country", key="s_home")
        if st.button("Create Account", key="s_btn"):
            if n_u and n_p and n_h:
                if n_u in users:
                    st.error("Username already exists")
                else:
                    users[n_u] = {
                        "password": n_p,
                        "display_name": n_u,
                        "home_country": n_h,
                        "purchases": []
                    }
                    save_users()
                    st.success("Account created! Go to Login tab.")
            else:
                st.error("Please fill all fields")

# ---------------- MAIN APP ----------------
else:
    user = st.session_state.user
    profile = users[user]

    if "badges" not in st.session_state:
        st.session_state.badges = set()

    st.sidebar.markdown(f"👋 Hello, **{profile.get('display_name', user)}**")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    page = st.sidebar.radio("Navigate", ["Home", "Settings"])

    # ---------------- HOME PAGE ----------------
    if page == "Home":
        st.title("GreenBasket")
        st.write(f"Welcome to your Dashboard, {user}!")

        st.subheader("🛒 Log a Purchase")
        c1, c2, c3 = st.columns(3)
        with c1:
            product_type = st.selectbox("Product Type", list(CO2_MULTIPLIER.keys()))
        with c2:
            brand = st.text_input("Brand")
        with c3:
            price = st.number_input("Price (₹)", min_value=1.0)

        if st.button("Add Purchase"):
            co2 = calculate_co2(price, product_type)
            profile["purchases"].append({
                "date": datetime.now().isoformat(),
                "product": product_type,
                "brand": brand,
                "price": price,
                "co2": co2
            })
            save_users()
            st.success(f"Purchase added! Estimated CO₂ impact: {co2}")
            st.info(random.choice(ECO_TIPS))

        if profile["purchases"]:
            df = pd.DataFrame(profile["purchases"])
            df["date"] = pd.to_datetime(df["date"])
            df["month"] = df["date"].dt.to_period("M").astype(str)

            total_spend = df["price"].sum()
            total_co2 = df["co2"].sum()

            if total_co2 < 100:
                st.session_state.badges.add("🌟 Eco Saver")
            if total_co2 < 200:
                st.session_state.badges.add("🍃 Low Impact Shopper")

            st.subheader("📊 Monthly Impact Dashboard")
            m1, m2 = st.columns(2)
            m1.metric("Total Spend (₹)", round(total_spend, 2))
            m2.metric("Estimated CO₂ Impact", round(total_co2, 2))

            st.bar_chart(df.groupby("month")[["price", "co2"]].sum())

            st.subheader("🏅 Your Eco Badges")
            for badge in st.session_state.badges:
                st.success(badge)

            if st.session_state.badges:
                st.markdown(
                    "<div style='font-size:60px;text-align:center;'>🍃🌍🍃</div>",
                    unsafe_allow_html=True
                )

            st.subheader("🌿 Greener Alternatives")
            for alt in GREEN_ALTERNATIVES.get(product_type, []):
                st.write("•", alt)

    # ---------------- SETTINGS PAGE ----------------
    elif page == "Settings":
        st.subheader("⚙️ Settings")
        st.session_state.bg_color = st.color_picker(
            "App Color", st.session_state.bg_color
        )
        if st.button("Apply Theme"):
            st.rerun()
