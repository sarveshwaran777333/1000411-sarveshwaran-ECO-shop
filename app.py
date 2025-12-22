import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import random

# ---------------- 1. PAGE CONFIG ----------------
st.set_page_config(page_title="GreenBasket", layout="wide")

USER_FILE = "users.json"
PRODUCT_FILE = "products.json"
ECO_FILE = "eco_alternatives.json"

# ---------------- 2. THEME LOGIC ----------------
if "bg_color" not in st.session_state:
    st.session_state.bg_color = "#e8f5e9"

def get_text_color(bg):
    bg = bg.lstrip("#")
    r, g, b = int(bg[0:2], 16), int(bg[2:4], 16), int(bg[4:6], 16)
    brightness = (r * 299 + g * 587 + b * 114) / 1000
    return "#000000" if brightness > 140 else "#ffffff"

def set_background(bg_color):
    text_color = get_text_color(bg_color)
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: {bg_color};
            color: {text_color};
        }}

        [data-testid="stSidebar"] {{
            background-color: {bg_color};
        }}

        [data-testid="stSidebar"] * {{
            color: {text_color} !important;
            font-weight: bold;
        }}

        h1, h2, h3, h4, h5, h6, p, label {{
            color: {text_color} !important;
        }}

        button[data-baseweb="tab"] p {{
            color: {text_color} !important;
        }}

        div.stButton > button {{
            border: 2px solid {text_color};
            color: {text_color};
            background-color: transparent;
            border-radius: 8px;
        }}

        input {{
            background-color: white !important;
            color: black !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

set_background(st.session_state.bg_color)

# ---------------- 3. FILE SETUP ----------------
if not os.path.exists(USER_FILE):
    with open(USER_FILE, "w") as f:
        json.dump({}, f)

if not os.path.exists(PRODUCT_FILE):
    st.error("Products file not found! Create products.json.")
    st.stop()

if not os.path.exists(ECO_FILE):
    st.error("Eco alternatives file not found! Create eco_alternatives.json.")
    st.stop()

with open(USER_FILE) as f:
    users = json.load(f)

with open(PRODUCT_FILE) as f:
    PRODUCTS = json.load(f)

with open(ECO_FILE) as f:
    ECO_ALTS = json.load(f)

def save_users():
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)

# ---------------- 4. IMPACT MULTIPLIER ----------------
IMPACT_MULTIPLIER = {
    "Clothing": 2.5,
    "Electronics": 4.0,
    "Groceries": 1.2,
    "Furniture": 3.0,
    "Second-hand": 0.5
}

ECO_TIPS = [
    "Buying second-hand reduces carbon emissions by up to 80%",
    "Local products reduce transport pollution",
    "Minimal packaging helps the environment",
    "Repairing products saves natural resources"
]

# ---------------- 5. GRAPHIC ----------------
def draw_eco_leaf():
    fig, ax = plt.subplots()
    t = np.linspace(0, 2*np.pi, 200)
    r = 1 + 0.3 * np.sin(3 * t)
    ax.fill(r*np.cos(t), r*np.sin(t), color="green")
    ax.axis("off")
    ax.set_aspect("equal")
    st.pyplot(fig)

# ---------------- 6. AUTH ----------------
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
            st.success("Account created")

# ---------------- 7. MAIN APP ----------------
else:
    user = st.session_state.user
    profile = users[user]

    st.sidebar.markdown(f"👋 {user}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    page = st.sidebar.radio("Navigate", ["Home", "Add Purchase", "Dashboard", "Badges", "Settings"])

    if page == "Home":
        st.title("🌍 Conscious Shopping Dashboard")
        st.write("Track spending and environmental impact.")

    elif page == "Add Purchase":
        st.subheader("➕ Add Purchase")

        p_type = st.selectbox("Product Type", list(PRODUCTS.keys()))
        p_name = st.selectbox("Product Name", PRODUCTS[p_type])
        brand = st.text_input("Brand")
        price = st.number_input("Price (₹)", min_value=0.0, step=10.0)

        if st.button("Add Purchase"):
            impact = price * IMPACT_MULTIPLIER.get(p_type, 1)
            profile["purchases"].append({
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "type": p_type,
                "product": p_name,
                "brand": brand,
                "price": price,
                "impact": impact
            })
            save_users()

            st.success(f"{p_name} added")
            st.metric("CO₂ Impact", f"{impact:.2f}")
            st.info(random.choice(ECO_TIPS))

            if p_name in ECO_ALTS:
                st.subheader("🌱 Eco-friendly Alternatives")
                for alt in ECO_ALTS[p_name]:
                    st.write("•", alt)

    elif page == "Dashboard":
        st.subheader("📊 Dashboard")

        if profile["purchases"]:
            df = pd.DataFrame(profile["purchases"])
            total_co2 = df["impact"].sum()
            total_money = df["price"].sum()

            col1, col2 = st.columns(2)
            col1.metric("Total CO₂ Released", f"{total_co2:.2f}")
            col2.metric("Total Money Spent (₹)", f"{total_money:.2f}")

            df["date"] = pd.to_datetime(df["date"])
            st.bar_chart(df.set_index("date")["impact"])
            st.dataframe(df)
        else:
            st.info("No purchases yet")

    elif page == "Badges":
        st.subheader("🏆 Eco Badges")
        total = sum(p["impact"] for p in profile["purchases"])
        if total < 500:
            st.success("Eco Saver")
            if st.button("View Reward"):
                draw_eco_leaf()
        elif total < 1000:
            st.info("Conscious Shopper")
        else:
            st.warning("High Impact User")

    elif page == "Settings":
        st.subheader("⚙️ Theme Settings")
        st.session_state.bg_color = st.color_picker("Choose Background Color", st.session_state.bg_color)
        if st.button("Apply Theme"):
            st.rerun()
