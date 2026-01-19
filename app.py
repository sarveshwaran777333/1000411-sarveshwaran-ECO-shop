import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime
import base64
import random
import time

# ---------------- CONFIG ----------------
st.set_page_config(page_title="GreenBasket", layout="wide", page_icon="🌱")

USER_FILE = "users.json"
PRODUCT_FILE = "products.json"

TRANSPORT_FACTORS = {
    "✈️ Air Freight": 0.500,
    "🚛 Road": 0.105,
    "🚆 Rail": 0.028,
    "🚢 Sea Freight": 0.015
}

COUNTRY_DISTANCES = {
    "Local (Within Country)": 150,
    "USA": 12000,
    "China": 8000,
    "India": 9000,
    "Germany": 1000,
    "Brazil": 10000,
    "UK": 1500,
    "Australia": 15000
}

ALL_CURRENCIES = ["USD - US Dollar ($)", "EUR - Euro (€)", "GBP - British Pound (£)", "INR - Indian Rupee (₹)"]

ECO_TIPS = [
    "Choosing slower shipping reduces CO₂ emissions.",
    "Buying local products reduces transport emissions.",
    "Minimal packaging reduces carbon footprint."
]

# ---------------- HELPERS ----------------
def safe_load_json(file_path, default_data):
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            json.dump(default_data, f)
        return default_data
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except:
        return default_data

def save_users():
    with open(USER_FILE, "w") as f:
        json.dump(st.session_state.users, f, indent=4)

def set_background(color):
    st.markdown(f"""
        <style>
        .stApp {{ background-color: {color}; }}
        .stMarkdown, h1, h2, h3, p, .stMetric, span {{ color: white !important; }}
        </style>
    """, unsafe_allow_html=True)

def format_price(amount):
    rates = {"USD": 1, "EUR": 0.92, "GBP": 0.79, "INR": 83}
    code = st.session_state.currency.split(" - ")[0]
    symbol = st.session_state.currency.split("(")[-1].replace(")", "")
    return f"{symbol}{amount * rates.get(code, 1):,.2f}"

def run_turtle_animation(badge_name):
    st.write(f"### 🎨 Drawing {badge_name}...")
    progress_bar = st.progress(0)
    for i in range(100):
        time.sleep(0.01)
        progress_bar.progress(i + 1)
    st.success(f"🍀 Finished drawing your **{badge_name}** badge!")
    st.balloons()

# ---------------- SESSION STATE ----------------
if "users" not in st.session_state:
    st.session_state.users = safe_load_json(USER_FILE, {})
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "bg_color" not in st.session_state:
    st.session_state.bg_color = "#1b5e20"
if "currency" not in st.session_state:
    st.session_state.currency = "USD - US Dollar ($)"

set_background(st.session_state.bg_color)

PRODUCTS = safe_load_json(PRODUCT_FILE, {
    "Electronics": {"items": ["Smartphone"], "brands": {"Standard": ["Generic"], "Eco-Friendly": ["Fairphone"]}},
    "Groceries": {"items": ["Coffee"], "brands": {"Standard": ["BigBrand"], "Eco-Friendly": ["Local Organic"]}}
})

# ---------------- AUTH ----------------
if not st.session_state.logged_in:
    st.title("🌱 GreenBasket")
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    with tab1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Login"):
            if u in st.session_state.users and st.session_state.users[u]["password"] == p:
                st.session_state.logged_in = True
                st.session_state.user = u
                st.rerun()
    with tab2:
        nu = st.text_input("New Username")
        np = st.text_input("New Password", type="password")
        if st.button("Register"):
            if nu and nu not in st.session_state.users:
                st.session_state.users[nu] = {"password": np, "purchases": [], "badges": []}
                save_users()
                st.success("Account created!")

# ---------------- MAIN APP ----------------
else:
    user = st.session_state.user
    profile = st.session_state.users[user]

    st.sidebar.title("🌿 ShopImpact")
    page = st.sidebar.radio("Menu", ["Home", "Add Purchase", "Dashboard", "Settings"])

    if page == "Home":
        st.title(f"Welcome, {user} 👋")
        st.info(f"💡 Eco-Tip: {random.choice(ECO_TIPS)}")
        st.subheader("🏅 Your Ethical Badges")
        user_badges = profile.get("badges", [])
        if user_badges:
            cols = st.columns(len(user_badges))
            for idx, badge in enumerate(user_badges):
                cols[idx].info(f"🏆 {badge}")
        else:
            st.write("No badges earned yet.")

    elif page == "Add Purchase":
        st.header("🛒 Log New Purchase")
        col1, col2 = st.columns(2)
        
        # --- CRITICAL FIX: Initialize variables outside the logic blocks ---
        eco_brands = []
        
        with col1:
            cat = st.selectbox("Category", list(PRODUCTS.keys()))
            prod_list = PRODUCTS[cat].get("items", [])
            prod = st.selectbox("Product", prod_list)
            
            # Fetch brands
            brands_data = PRODUCTS[cat].get("brands", {})
            eco_brands = brands_data.get("Eco-Friendly", [])
            standard_brands = brands_data.get("Standard", [])
            
            # Show warning ONLY if eco alternatives exist
            if eco_brands:
                st.warning(f"🌱 High Impact Alert! Consider these Eco-Friendly alternatives: {', '.join(eco_brands)}")
            
            all_brands = standard_brands + eco_brands
            brand = st.selectbox("Brand", all_brands)
            price = st.number_input("Price (USD)", min_value=0.0, format="%.2f")

        with col2:
            origin = st.selectbox("Origin", list(COUNTRY_DISTANCES.keys()))
            mode = st.selectbox("Transport Mode", list(TRANSPORT_FACTORS.keys()))
            
            if st.button("Add to Basket"):
                is_eco = brand in eco_brands
                impact = (price * (0.4 if is_eco else 1.2)) + (COUNTRY_DISTANCES[origin] * TRANSPORT_FACTORS[mode])
                
                profile["purchases"].append({
                    "product": prod, "brand": brand, "price": price, 
                    "impact": round(impact, 2), "date": str(datetime.now())
                })
                
                if is_eco and "Eco Saver" not in profile.get("badges", []):
                    profile.setdefault("badges", []).append("Eco Saver")
                    run_turtle_animation("Eco Saver")
                
                save_users()
                st.success(f"Added! Carbon Footprint: {impact:.2f} kg CO₂")

    elif page == "Dashboard":
        st.header("📊 Monthly Impact Dashboard")
        if profile.get("purchases"):
            df = pd.DataFrame(profile["purchases"])
            df['date'] = pd.to_datetime(df['date'])
            df['Month'] = df['date'].dt.strftime('%b %Y')
            
            recent_impact = df['impact'].sum()
            recent_spend = df['price'].sum()
            
            c1, c2 = st.columns(2)
            c1.metric("Total CO₂ Impact", f"{recent_impact:.2f} kg")
            c2.metric("Total Spend", format_price(recent_spend))
            
            st.write("### Impact Trend")
            st.line_chart(df.set_index("date")["impact"])
        else:
            st.info("No data logged yet.")

    elif page == "Settings":
        st.header("⚙️ Settings")
        new_color = st.color_picker("Change Theme", st.session_state.bg_color)
        if st.button("Save Settings"):
            st.session_state.bg_color = new_color
            st.rerun()
        if st.button("Logout", type="primary"):
            st.session_state.logged_in = False
            st.rerun()
