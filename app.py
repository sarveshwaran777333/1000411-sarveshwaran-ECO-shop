import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="GreenBasket", layout="wide")

USER_FILE = "users.json"

# ---------------- THEME ----------------
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
        html, body, .stApp {{
            background-color: {bg_color} !important;
            color: {text_color} !important;
        }}

        input {{
            background-color: rgba(255,255,255,0.85) !important;
            color: {text_color} !important;
        }}

        /* -------- BUTTON FIX -------- */
        .stButton > button {{
            color: white !important;
            background-color: #1b5e20 !important;
            border-radius: 8px;
            border: none;
            font-weight: 600;
        }}

        .stButton > button:hover {{
            background-color: #2e7d32 !important;
            color: white !important;
        }}
        /* --------------------------- */

        </style>
        """,
        unsafe_allow_html=True
    )

# ---------------- DATA ----------------
if not os.path.exists(USER_FILE):
    with open(USER_FILE, "w") as f:
        json.dump({}, f)

with open(USER_FILE, "r") as f:
    users = json.load(f)

def save_users():
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)

# ---------------- CO₂ LOGIC ----------------
IMPACT_MULTIPLIER = {
    "Clothing": 2.5,
    "Electronics": 4.0,
    "Groceries": 1.2,
    "Furniture": 3.0,
    "Second-hand": 0.5
}

# --------- ADDED (NO EXISTING CODE REMOVED) ---------
TRANSPORT_FACTOR = {
    "Air": 3.0,
    "Road": 1.5,
    "Rail": 1.0,
    "Sea": 0.8
}

DISTANCE_FACTOR = {
    "Local (Same city)": 1.0,
    "Domestic": 1.3,
    "International": 1.8
}
# ---------------------------------------------------

# ---------------- AUTH ----------------
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
        nh = st.text_input("Home City/Country")
        if st.button("Create Account"):
            users[nu] = {
                "password": np,
                "home": nh,
                "purchases": []
            }
            save_users()
            st.success("Account created")

# ---------------- MAIN APP ----------------
else:
    user = st.session_state.user
    profile = users[user]

    st.sidebar.markdown(f"👋 **{user}**")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    page = st.sidebar.radio(
        "Navigate",
        ["Home", "Add Purchase", "Dashboard", "Badges", "Settings"]
    )

    # -------- HOME --------
    if page == "Home":
        st.title("🌍 Conscious Shopping Dashboard")
        st.write("Track purchases and reduce your environmental impact.")

    # -------- ADD PURCHASE --------
    elif page == "Add Purchase":
        st.subheader("➕ Add a Purchase")

        product = st.selectbox("Product Type", list(IMPACT_MULTIPLIER.keys()))
        brand = st.text_input("Brand")
        price = st.number_input("Price", min_value=0.0)

        # --------- ADDED INPUTS ---------
        origin = st.selectbox(
            "Product Origin",
            ["Local (Same city)", "Domestic", "International"]
        )

        transport = st.selectbox(
            "Mode of Transport",
            list(TRANSPORT_FACTOR.keys())
        )
        # --------------------------------

        if st.button("Add Purchase"):
            impact = (
                price
                * IMPACT_MULTIPLIER[product]
                * TRANSPORT_FACTOR[transport]
                * DISTANCE_FACTOR[origin]
            )

            profile["purchases"].append({
                "date": datetime.now().strftime("%Y-%m-%d"),
                "product": product,
                "brand": brand,
                "price": price,
                "origin": origin,
                "transport": transport,
                "impact": impact
            })
            save_users()
            st.success(f"Added! Estimated CO₂ impact: {impact:.2f}")

        st.warning("""
⚠️ CO₂ Calculation Note

Actual carbon footprints depend on:
• Manufacturing location
• Distance travelled
• Mode of transport

This app uses a simplified estimation model
to create environmental awareness.
""")

    # -------- DASHBOARD --------
    elif page == "Dashboard":
        st.subheader("📊 Monthly Impact Dashboard")

        if profile["purchases"]:
            df = pd.DataFrame(profile["purchases"])
            df["date"] = pd.to_datetime(df["date"])
            monthly = df.groupby(df["date"].dt.month).sum(numeric_only=True)

            st.metric("Total Spend", f"₹{df['price'].sum():.2f}")
            st.metric("Total CO₂ Impact", f"{df['impact'].sum():.2f}")

            st.bar_chart(monthly[["price", "impact"]])
        else:
            st.info("No purchases yet.")

    # -------- BADGES --------
    elif page == "Badges":
        st.subheader("🏆 Your Eco Mascot")

        total_impact = sum(p["impact"] for p in profile["purchases"])

        if total_impact < 500:
            st.success("🌟 Eco Saver Badge Earned!")
            st.image("image/Lion_Happy.png", width=250)
        elif total_impact < 1000:
            st.info("👍 Conscious Shopper")
            st.image("image/Lion.png", width=250)
        else:
            st.warning("⚠️ High Impact Shopper")
            st.image("image/Lion_Sad.png", width=250)

    # -------- SETTINGS --------
    elif page == "Settings":
        st.subheader("⚙️ Settings")
        st.session_state.bg_color = st.color_picker(
            "App Theme Color",
            st.session_state.bg_color
        )
        if st.button("Apply Theme"):
            st.rerun()
