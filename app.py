import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime
import random

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="GreenBasket", layout="wide")

USER_FILE = "users.json"
PRODUCT_FILE = "products.json"
ECO_FILE = "eco_alternatives.json"

# ---------------- SESSION STATE ----------------
if "bg_color" not in st.session_state:
    st.session_state.bg_color = "#dff5e1"

# ---------------- BACKGROUND STYLE ----------------
def set_background(color):
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: {color};
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

set_background(st.session_state.bg_color)

# ---------------- LOAD FILES ----------------
for file in [PRODUCT_FILE, ECO_FILE]:
    if not os.path.exists(file):
        st.error(f"{file} not found")
        st.stop()

with open(PRODUCT_FILE, "r") as f:
    PRODUCTS = json.load(f)

with open(ECO_FILE, "r") as f:
    ECO_ALTS = json.load(f)

# ---------------- USER DATA ----------------
if not os.path.exists(USER_FILE):
    with open(USER_FILE, "w") as f:
        json.dump({}, f)

with open(USER_FILE, "r") as f:
    users = json.load(f)

def save_users():
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)

# ---------------- IMPACT LOGIC ----------------
IMPACT_MULTIPLIER = {
    "Clothing": 2.5,
    "Electronics": 4.0,
    "Groceries": 1.2,
    "Furniture": 3.0,
    "Second-hand": 0.5
}

ECO_TIPS = [
    "Repairing products reduces waste",
    "Second-hand shopping saves resources",
    "Local products reduce transport emissions",
    "Minimal packaging helps the planet"
]

# ---------------- AUTH ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🌱 GreenBasket")

    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Login"):
            if u in users and users[u]["password"] == p:
                st.session_state.logged_in = True
                st.session_state.user = u
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:
        nu = st.text_input("New Username")
        np = st.text_input("New Password", type="password")
        if st.button("Create Account"):
            users[nu] = {"password": np, "purchases": []}
            save_users()
            st.success("Account created. Please login.")

# ---------------- MAIN APP ----------------
else:
    user = st.session_state.user
    profile = users[user]

    # ---------- SIDEBAR ----------
    st.sidebar.markdown(f"👤 **{user}**")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    st.sidebar.markdown("### 🎨 Background Theme")
    new_color = st.sidebar.color_picker(
        "Choose background color",
        st.session_state.bg_color
    )

    if st.sidebar.button("Apply Background"):
        st.session_state.bg_color = new_color
        st.rerun()

    page = st.sidebar.radio("Navigate", ["Home", "Add Purchase", "Dashboard"])

    # ---------- HOME ----------
    if page == "Home":
        st.title("🌍 Conscious Shopping Dashboard")
        st.write("Track purchases and understand environmental impact.")

    # ---------- ADD PURCHASE ----------
    elif page == "Add Purchase":
        st.subheader("➕ Add a Purchase")

        p_type = st.selectbox("Product Category", list(PRODUCTS.keys()))
        p_name = st.selectbox("Product Name", PRODUCTS[p_type])
        brand = st.text_input("Brand")
        price = st.number_input("Price (₹)", min_value=0.0)

        if st.button("Add Purchase"):
            impact = price * IMPACT_MULTIPLIER[p_type]

            profile["purchases"].append({
                "date": datetime.now().strftime("%Y-%m-%d"),
                "category": p_type,
                "product": p_name,
                "brand": brand,
                "price": price,
                "impact": impact
            })

            save_users()

            st.success(f"{p_name} added successfully")
            st.info(random.choice(ECO_TIPS))

            # 🌱 ECO RECOMMENDATIONS
            st.subheader("🌱 Eco-Friendly Alternatives")
            for alt in ECO_ALTS.get(p_type, []):
                st.write("•", alt)

    # ---------- DASHBOARD ----------
    elif page == "Dashboard":
        st.subheader("📊 Impact Summary")

        if profile["purchases"]:
            df = pd.DataFrame(profile["purchases"])

            c1, c2 = st.columns(2)
            c1.metric("🌍 Total CO₂ Impact", f"{df['impact'].sum():.2f}")
            c2.metric("💰 Total Spend", f"₹ {df['price'].sum():.2f}")

            st.bar_chart(df.set_index("date")["impact"])
            st.dataframe(df)

        else:
            st.info("No purchases recorded yet.")
