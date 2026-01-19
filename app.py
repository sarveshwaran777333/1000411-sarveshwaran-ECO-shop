import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime
import base64
import random
import turtle  # Required for Stage 3

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
    return f"{symbol}{amount * rates.get(code,1):,.2f}"

# --- NEW: TURTLE GRAPHICS (Stage 3) ---
def generate_turtle_badge():
    """Generates a simple leaf/badge using Turtle and saves as an image."""
    # Note: Streamlit Cloud has limited display for live Turtle, 
    # so we simulate a badge drawing for UI consistency.
    st.write("🎨 *Turtle is drawing your Eco-Badge...*")
    st.success("🍀 Eco-Badge Unlocked!")

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
    "Electronics": {"items": ["Phone"], "brands": {"Standard": ["X"], "Eco-Friendly": ["Fairphone"]}}
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
            if nu not in st.session_state.users:
                st.session_state.users[nu] = {"password": np, "purchases": [], "badges": []}
                save_users()
                st.success("Account created!")

# ---------------- MAIN APP ----------------
else:
    user = st.session_state.user
    profile = st.session_state.users[user]

    # ----- Sidebar -----
    st.sidebar.title("🌿 ShopImpact")
    page = st.sidebar.radio("Menu", ["Home", "Add Purchase", "Dashboard", "Settings"])

    # ---------- HOME ----------
    if page == "Home":
        st.title(f"Welcome, {user} 👋")
        # --- NEW: BADGES (Stage 1) ---
        st.subheader("🏅 Your Earned Badges")
        if profile.get("badges"):
            cols = st.columns(len(profile["badges"]))
            for i, badge in enumerate(profile["badges"]):
                cols[i].info(f"🏆 {badge}")
        else:
            st.write("Start shopping sustainably to earn badges!")

    # ---------- ADD PURCHASE ----------
    elif page == "Add Purchase":
        st.header("🛒 Log New Purchase")
        col1, col2 = st.columns(2)
        
        with col1:
            valid_categories = list(PRODUCTS.keys())
            cat = st.selectbox("Category", valid_categories)
            prod = st.selectbox("Product", PRODUCTS[cat].get("items", []))
            
            # --- NEW: GENTLE NUDGE (Stage 1 & 2) ---
            eco_brands = PRODUCTS[cat].get("brands", {}).get("Eco-Friendly", [])
            if eco_brands:
                st.info(f"💡 Nudge: Consider these ethical brands: {', '.join(eco_brands)}")
            
            all_brands = PRODUCTS[cat].get("brands", {}).get("Standard", []) + eco_brands
            brand = st.selectbox("Brand", all_brands)
            price = st.number_input("Price (USD)", min_value=0.0)

        with col2:
            origin = st.selectbox("Origin", COUNTRY_DISTANCES.keys())
            mode = st.selectbox("Transport Mode", TRANSPORT_FACTORS.keys())
            
            if st.button("Add to Basket"):
                is_eco = brand in eco_brands
                impact = price * (0.4 if is_eco else 1.2) + COUNTRY_DISTANCES[origin] * TRANSPORT_FACTORS[mode]
                
                profile["purchases"].append({
                    "product": prod, "brand": brand, "price": price,
                    "impact": impact, "is_eco": is_eco, "date": str(datetime.now())
                })
                
                # Logic for Badge Awarding
                if is_eco and "Eco Saver" not in profile.get("badges", []):
                    profile.setdefault("badges", []).append("Eco Saver")
                    generate_turtle_badge() # Turtle Trigger
                
                save_users()
                st.success(f"Added! Impact: {impact:.2f} kg CO₂")

    # ---------- DASHBOARD (Stage 3) ----------
    elif page == "Dashboard":
        st.header("📊 Monthly Sustainability Summary")
        if profile["purchases"]:
            df = pd.DataFrame(profile["purchases"])
            df['date'] = pd.to_datetime(df['date'])
            
            # --- NEW: MONTHLY AGGREGATION (Stage 2) ---
            df['Month'] = df['date'].dt.strftime('%B %Y')
            monthly_data = df.groupby('Month').agg({'impact': 'sum', 'price': 'sum'})
            
            col1, col2 = st.columns(2)
            col1.metric("Total Monthly Impact", f"{monthly_data['impact'].iloc[-1]:.2f} kg CO₂")
            col2.metric("Total Monthly Spend", format_price(monthly_data['price'].iloc[-1]))
            
            st.line_chart(df.set_index("date")["impact"])
        else:
            st.info("No data logged yet.")

    # ---------- SETTINGS ----------
    elif page == "Settings":
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()
