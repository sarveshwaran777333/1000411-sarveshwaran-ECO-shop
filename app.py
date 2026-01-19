import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime
import random
import time

# ---------------- CONFIG ----------------
st.set_page_config(page_title="GreenBasket", layout="wide", page_icon="🌱")

USER_FILE = "users.json"
PRODUCT_FILE = "products.json"

TRANSPORT_FACTORS = {"✈️ Air Freight": 0.500, "🚛 Road": 0.105, "🚆 Rail": 0.028, "🚢 Sea Freight": 0.015}
COUNTRY_DISTANCES = {"Local (Within Country)": 150, "USA": 12000, "China": 8000, "India": 9000, "Germany": 1000, "UK": 1500}
ECO_TIPS = ["Choosing slower shipping reduces CO₂.", "Buying local reduces transport emissions."]

# ---------------- HELPERS ----------------
def safe_load_json(file_path, default_data):
    if not os.path.exists(file_path):
        with open(file_path, "w") as f: json.dump(default_data, f)
        return default_data
    try:
        with open(file_path, "r") as f: return json.load(f)
    except: return default_data

def save_users():
    with open(USER_FILE, "w") as f:
        json.dump(st.session_state.users, f, indent=4)

def set_background(color):
    st.markdown(f"""<style>.stApp {{ background-color: {color}; }} .stMarkdown, h1, h2, h3, p, span, label {{ color: white !important; }}</style>""", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
if "users" not in st.session_state: st.session_state.users = safe_load_json(USER_FILE, {})
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "bg_color" not in st.session_state: st.session_state.bg_color = "#1b5e20"

set_background(st.session_state.bg_color)

PRODUCTS = safe_load_json(PRODUCT_FILE, {
    "Electronics": {"items": ["Smartphone"], "brands": {"Standard": ["Generic"], "Eco-Friendly": ["Fairphone"]}},
    "Groceries": {"items": ["Coffee"], "brands": {"Standard": ["BigBrand"], "Eco-Friendly": ["Local Organic"]}}
})

# ---------------- AUTH ----------------
if not st.session_state.logged_in:
    st.title("🌱 GreenBasket")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Login"):
        if u in st.session_state.users and st.session_state.users[u]["password"] == p:
            st.session_state.logged_in = True
            st.session_state.user = u
            st.rerun()
    if st.button("Register"):
        if u and u not in st.session_state.users:
            st.session_state.users[u] = {"password": p, "purchases": [], "badges": []}
            save_users()
            st.success("Registered!")

# ---------------- MAIN APP ----------------
else:
    user = st.session_state.user
    profile = st.session_state.users[user]

    page = st.sidebar.radio("Menu", ["Home", "Add Purchase", "Eco Game", "Settings"])

    if page == "Home":
        st.title(f"Welcome, {user} 👋")
        # Calculate total clovers safely
        total_clovers = sum(p.get("clovers_earned", 0) for p in profile.get("purchases", []))
        st.metric("🍀 Your Green Clovers", total_clovers)

    elif page == "Add Purchase":
        st.header("🛒 Log New Purchase")
        cat = st.selectbox("Category", list(PRODUCTS.keys()))
        eco_brands = PRODUCTS[cat].get("brands", {}).get("Eco-Friendly", [])
        
        if eco_brands:
            st.warning(f"🌱 Eco Alternatives: {', '.join(eco_brands)}")
        
        brand = st.selectbox("Brand", PRODUCTS[cat]["brands"]["Standard"] + eco_brands)
        price = st.number_input("Price", min_value=0.0)
        
        if st.button("Add to Basket"):
            is_eco = brand in eco_brands
            # Earn 10 clovers for eco brands, 1 for standard
            earned = 10 if is_eco else 1 
            
            profile["purchases"].append({
                "product": brand, 
                "price": price, 
                "clovers_earned": earned,
                "date": str(datetime.now())
            })
            save_users()
            st.success(f"Added! You earned {earned} 🍀 Clovers!")

    # ---------- ECO GAME: ROBO RUNNER ----------
    elif page == "Eco Game":
        st.header("🤖 Robo Runner")
        
        # Calculate clovers from purchase history
        total_clovers = sum(p.get("clovers_earned", 0) for p in profile.get("purchases", []))
        
        st.write(f"### 🍀 Total Clovers Available: {total_clovers}")
        
        if total_clovers == 0:
            st.warning("You need Clovers to fuel your Robo! Go shop for Eco-friendly items.")
        else:
            st.write("Your Robo uses Clovers to clean the planet. Click 'Run' to start!")
            
            if st.button("🚀 Start Cleaning Run"):
                st.write("Robo is running...")
                bar = st.progress(0)
                
                # Simple game animation
                for i in range(100):
                    time.sleep(0.02)
                    bar.progress(i + 1)
                
                st.success(f"Run Complete! Robo cleaned up {total_clovers * 2}kg of virtual CO₂!")
                st.balloons()

    elif page == "Settings":
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()
            
