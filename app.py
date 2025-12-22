import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime

# ---------------- 1. PAGE CONFIG ----------------
st.set_page_config(page_title="GreenBasket", layout="wide")
USER_FILE = "users.json"

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
    
    if text_color == "white":
        btn_bg, btn_text = "#ffffff", "#000000"
    else:
        btn_bg, btn_text = "#1b5e20", "#ffffff"

    st.markdown(f"""
        <style>
        /* Main Background */
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stSidebar"] {{
            background-color: {bg_color} !important;
            color: {text_color} !important;
        }}

        /* FIX: Tab Visibility (Login / Sign Up text) */
        /* This forces both active and inactive tabs to show the text color */
        button[data-baseweb="tab"] p {{
            color: {text_color} !important;
            font-weight: bold !important;
        }}
        
        /* Ensure the hover state doesn't hide the text */
        button[data-baseweb="tab"]:hover p {{
            color: {text_color} !important;
        }}

        /* FIX: Color Picker Outline */
        div[data-testid="stColorPicker"] > div:first-child {{
            border: 3px solid {text_color} !important;
            border-radius: 10px !important;
            padding: 8px !important;
        }}

        /* FIX: Button Text Visibility */
        div.stButton > button {{
            background-color: {btn_bg} !important;
            border: 2px solid {text_color} !important;
            border-radius: 8px !important;
        }}
        div.stButton > button p {{
            color: {btn_text} !important;
            font-weight: bold !important;
        }}

        /* FIX: Label Visibility (Username/Password) */
        [data-testid="stWidgetLabel"] p {{
            color: {text_color} !important;
            font-weight: bold !important;
        }}

        /* Input Box Styling */
        input {{
            background-color: rgba(255,255,255,0.9) !important;
            color: #000000 !important;
        }}
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
    "Clothing": 2.5, "Electronics": 4.0, "Groceries": 1.2, 
    "Furniture": 3.0, "Second-hand": 0.5
}

PRODUCTS_BY_TYPE = {
    "Clothing": ["T-Shirt", "Jeans", "Jacket", "Shoes"],
    "Electronics": ["Mobile Phone", "Laptop", "Headphones", "Tablet"],
    "Groceries": ["Rice", "Vegetables", "Fruits", "Snacks"],
    "Furniture": ["Chair", "Table", "Sofa", "Bed"],
    "Second-hand": ["Used Clothes", "Used Books", "Refurbished Phone"]
}

# ---------------- 5. AUTHENTICATION ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🌱 GreenBasket")
    t1, t2 = st.tabs(["Login", "Sign Up"])

    with t1:
        u = st.text_input("Username", key="login_user")
        p = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            if u in users and users[u]["password"] == p:
                st.session_state.logged_in = True
                st.session_state.user = u
                st.rerun()
            else:
                st.error("Invalid credentials")

    with t2:
        nu = st.text_input("New Username", key="reg_user")
        np = st.text_input("New Password", type="password", key="reg_pass")
        nh = st.text_input("Home City/Country", key="reg_home")
        if st.button("Create Account"):
            if nu and np:
                users[nu] = {"password": np, "home": nh, "purchases": []}
                save_users()
                st.success("Account created. Go to Login.")

# ---------------- 6. MAIN APP ----------------
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
        st.write(f"Welcome, **{user}**! Track your environmental impact below.")

    elif page == "Add Purchase":
        st.subheader("➕ Add a Purchase")
        p_type = st.selectbox("Product Type", list(IMPACT_MULTIPLIER.keys()))
        p_name = st.selectbox("Product Name", PRODUCTS_BY_TYPE.get(p_type, []))
        brand = st.text_input("Brand")
        price = st.number_input("Price (₹)", min_value=0.0, step=1.0)

        if st.button("Add Purchase"):
            impact = price * IMPACT_MULTIPLIER[p_type]
            profile["purchases"].append({
                "date": datetime.now().strftime("%Y-%m-%d"),
                "product_type": p_type, "product_name": p_name,
                "brand": brand, "price": price, "impact": impact
            })
            save_users()
            st.success(f"Added {p_name}! CO₂ impact: {impact:.2f}")

    elif page == "Dashboard":
        st.subheader("📊 Monthly Impact Dashboard")
        if profile["purchases"]:
            df = pd.DataFrame(profile["purchases"])
            st.metric("Total CO₂ Impact", f"{df['impact'].sum():.2f}")
            st.bar_chart(df.set_index("date")["impact"])
        else:
            st.info("No purchases added yet.")

    elif page == "Badges":
        st.subheader("🏆 Your Eco Badges")
        total_impact = sum(p["impact"] for p in profile["purchases"])
        if total_impact < 500:
            st.success("🌟 Eco Saver (Mascot: 🐢)")
        elif total_impact < 1000:
            st.info("🌿 Conscious Shopper (Mascot: 🌿)")
        else:
            st.warning("🔥 High Impact (Try greener choices!)")

    elif page == "Settings":
        st.subheader("⚙️ Settings")
        st.session_state.bg_color = st.color_picker("App Theme Color", st.session_state.bg_color)
        if st.button("Apply Theme"):
            st.rerun()
