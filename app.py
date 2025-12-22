import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime
import turtle
import random

# ---------------- 1. PAGE CONFIG ----------------
st.set_page_config(page_title="GreenBasket", layout="wide")
USER_FILE = "users.json"

MASCOT_DEFAULT = "image/Lion.png"
MASCOT_LOW = "image/Lion_Happy.png"
MASCOT_HIGH = "image/Lion_Sad.png"

# ---------------- 2. THEME LOGIC ----------------
if "bg_color" not in st.session_state:
    st.session_state.bg_color = "#e8f5e9"

def get_text_color(hex_color):
    hex_color = hex_color.lstrip('#')
    try:
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        brightness = (r * 0.299 + g * 0.587 + b * 0.114)
        return "black" if brightness > 128 else "white"
    except:
        return "black"

def set_appearance(bg_color):
    text_color = get_text_color(bg_color)
    st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg_color}; color: {text_color}; }}
    </style>
    """, unsafe_allow_html=True)

set_appearance(st.session_state.bg_color)

# ---------------- 3. DATA PERSISTENCE ----------------
if not os.path.exists(USER_FILE):
    with open(USER_FILE, "w") as f:
        json.dump({}, f)

with open(USER_FILE, "r") as f:
    users = json.load(f)

def save_users():
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)

# ---------------- 4. SHOP IMPACT LOGIC ----------------
IMPACT_MULTIPLIER = {
    "Clothing": 2.5,
    "Electronics": 4.0,
    "Groceries": 1.2,
    "Furniture": 3.0,
    "Second-hand": 0.5
}

GREEN_ALTERNATIVES = {
    "Clothing": ["Organic cotton", "Second-hand clothing"],
    "Electronics": ["Refurbished devices", "Energy-star rated products"],
    "Groceries": ["Local produce", "Plastic-free packaging"],
    "Furniture": ["Bamboo furniture", "Upcycled wood"],
    "Second-hand": ["Thrift stores", "Community swaps"]
}

ECO_TIPS = [
    "Buying second-hand reduces carbon emissions by up to 80%",
    "Local products reduce transport pollution",
    "Minimal packaging helps the environment",
    "Repairing products saves natural resources"
]

# ---------------- 5. TURTLE GRAPHIC ----------------
def draw_eco_leaf():
    t = turtle.Turtle()
    t.speed(5)
    t.color("green")
    t.begin_fill()
    t.circle(50)
    t.end_fill()
    turtle.done()

# ---------------- 6. AUTHENTICATION ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🌱 GreenBasket")
    t1, t2 = st.tabs(["Login", "Sign Up"])

    with t1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Login"):
            if u in users and users[u]["password"] == p:
                st.session_state.logged_in = True
                st.session_state.user = u
                st.rerun()
            else:
                st.error("Invalid credentials")

    with t2:
        nu = st.text_input("New Username")
        np = st.text_input("New Password", type="password")
        if st.button("Create Account"):
            users[nu] = {"password": np, "purchases": []}
            save_users()
            st.success("Account created. Please login.")

# ---------------- 7. MAIN APP ----------------
else:
    user = st.session_state.user
    profile = users[user]

    st.sidebar.markdown(f"👋 **{user}**")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    page = st.sidebar.radio("Navigate", ["Home", "Add Purchase", "Dashboard", "Badges", "Settings"])

    if page == "Home":
        st.title("🌍 Conscious Shopping Dashboard")
        st.write("Track purchases, see your CO₂ footprint, and earn eco rewards.")

    elif page == "Add Purchase":
        st.subheader("➕ Add a Purchase")

        p_type = st.selectbox("Product Type", list(IMPACT_MULTIPLIER.keys()))
        brand = st.text_input("Brand")
        price = st.number_input("Price (₹)", min_value=0.0, step=10.0)

        if st.button("Add Purchase"):
            impact = price * IMPACT_MULTIPLIER[p_type]
            profile["purchases"].append({
                "date": datetime.now(),
                "product_type": p_type,
                "brand": brand,
                "price": price,
                "impact": impact
            })
            save_users()
            st.success(f"Purchase added! CO₂ Impact: {impact:.2f}")
            st.info(random.choice(ECO_TIPS))

            st.subheader("🌱 Greener Alternatives")
            for alt in GREEN_ALTERNATIVES[p_type]:
                st.write("•", alt)

    elif page == "Dashboard":
        st.subheader("📊 Monthly Impact Dashboard")
        if profile["purchases"]:
            df = pd.DataFrame(profile["purchases"])
            df["Month"] = pd.to_datetime(df["date"]).dt.to_period("M")

            monthly = df.groupby("Month")[["price", "impact"]].sum()

            st.metric("Total CO₂ Impact", f"{df['impact'].sum():.2f}")
            st.dataframe(monthly)
            st.bar_chart(monthly["impact"])
        else:
            st.info("No purchases yet.")

    elif page == "Badges":
        st.subheader("🏆 Eco Badges")
        total = sum(p["impact"] for p in profile["purchases"])

        if total < 500:
            st.success("🏆 Eco Saver")
            if st.button("See Eco Reward"):
                draw_eco_leaf()
        elif total < 1000:
            st.info("🌿 Conscious Shopper")
        else:
            st.warning("⚠️ High Impact – Try greener choices")

    elif page == "Settings":
        st.subheader("⚙️ Settings")
        st.session_state.bg_color = st.color_picker("Theme Color", st.session_state.bg_color)
        if st.button("Apply"):
            st.rerun()
