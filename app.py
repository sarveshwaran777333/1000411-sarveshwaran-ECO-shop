import streamlit as st
import json
import os
import pandas as pd

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="GreenBasket", layout="wide")

USER_FILE = "users.json"
MASCOT_DEFAULT = "image/Lion.png"
MASCOT_LOW = "image/Lion_Happy.png"
MASCOT_HIGH = "image/Lion_Sad.png"
LOW_CO2_LIMIT = 100

# ---------------- BACKGROUND HANDLER ----------------
if "bg_color" not in st.session_state:
    st.session_state.bg_color = "#e8f5e9"

def set_background(color):
    st.markdown(
        f"""
        <style>
        .stApp {{ background-color: {color}; }}
        </style>
        """,
        unsafe_allow_html=True
    )

set_background(st.session_state.bg_color)

# ---------------- DATA INIT ----------------
if not os.path.exists(USER_FILE):
    with open(USER_FILE, "w") as f:
        json.dump({}, f)

with open(USER_FILE, "r") as f:
    users = json.load(f)

def save_users():
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)

# ---------------- CO₂ LOGIC ----------------
PRODUCT_IMPACT = {
    "Electronics": 5.0,
    "Clothing": 2.0,
    "Food": 1.0,
    "Household": 1.5,
    "Transport": 4.0
}

def calculate_multiplier(user_home, product_origin):
    u_home = user_home.lower().strip()
    p_origin = product_origin.lower().strip()
    
    # Logic: Compare user home to product origin
    if u_home == p_origin or p_origin in ["local", "nearby", "home"]:
        return 1.0  # Local
    elif p_origin == "":
        return 1.3  # Default to Regional if unknown
    else:
        return 1.8  # International (Long distance transport)

def total_co2(username):
    user_data = users.get(username, {})
    purchases = user_data.get("purchases", [])
    return sum(p.get("co2", 0) for p in purchases)

def get_mascot(username):
    total = total_co2(username)
    if total == 0: return MASCOT_DEFAULT
    return MASCOT_LOW if total <= LOW_CO2_LIMIT else MASCOT_HIGH

def show_sidebar_mascot(username):
    path = get_mascot(username)
    if os.path.exists(path):
        st.sidebar.image(path, width=160)

# ---------------- AUTH & SESSION ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🌱 GreenBasket")
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    with tab1:
        u_in = st.text_input("Username")
        p_in = st.text_input("Password", type="password")
        if st.button("Login"):
            if u_in in users and users[u_in]["password"] == p_in:
                st.session_state.logged_in = True
                st.session_state.user = u_in
                st.rerun()
            else: st.error("Invalid credentials")
    with tab2:
        n_u = st.text_input("New Username")
        n_p = st.text_input("New Password", type="password")
        n_home = st.text_input("Your Country (e.g., India, UK, USA)")
        if st.button("Sign Up"):
            if n_u and n_p and n_home:
                users[n_u] = {
                    "password": n_p, 
                    "display_name": n_u, 
                    "home_country": n_home,
                    "purchases": []
                }
                save_users()
                st.success("Account created! Please login.")
            else:
                st.warning("Please fill all fields")

# ---------------- MAIN APP ----------------
else:
    user = st.session_state.user
    profile = users[user]
    
    # Sidebar
    st.sidebar.markdown(f"👋 Hello, **{profile.get('display_name', user)}**")
    st.sidebar.caption(f"📍 Home Base: {profile.get('home_country', 'Not set')}")
    show_sidebar_mascot(user)
    
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    page = st.sidebar.radio("Navigate", ["Home", "Add Purchase", "Dashboard", "Settings"])

    if page == "Home":
        st.title("GreenBasket")
        st.write(f"Welcome back! We are comparing all products against your home in **{profile.get('home_country')}**.")

    elif page == "Add Purchase":
        st.subheader("🛒 Add a Purchase")
        col1, col2 = st.columns(2)
        with col1:
            prod = st.text_input("Product Name")
            brand = st.text_input("Brand")
            price = st.number_input("Price", min_value=0.0)
        with col2:
            cat = st.selectbox("Category", list(PRODUCT_IMPACT.keys()))
            prod_origin = st.text_input("Product Origin Country (e.g., USA, China, India)")

        if st.button("Add Purchase"):
            if prod and prod_origin and price > 0:
                user_home = profile.get("home_country", "Unknown")
                
                # Determine multiplier by comparing home vs origin
                mult = calculate_multiplier(user_home, prod_origin)
                co2_val = round(price * PRODUCT_IMPACT[cat] * mult, 2)
                
                profile["purchases"].append({
                    "product": prod, 
                    "brand": brand, 
                    "category": cat, 
                    "origin": prod_origin, 
                    "price": price, 
                    "co2": co2_val,
                    "impact_type": "Local" if mult == 1.0 else "International"
                })
                save_users()
                st.success(f"Added! Since you are in {user_home} and this is from {prod_origin}, it is marked as {('Local' if mult == 1.0 else 'International')}.")
                st.rerun()

    elif page == "Dashboard":
        st.subheader("📊 Impact Dashboard")
        if not profile["purchases"]: st.info("No data yet.")
        else:
            df = pd.DataFrame(profile["purchases"])
            st.metric("Total CO₂ Impact", f"{df['co2'].sum():.2f} kg")
            st.dataframe(df, use_container_width=True)

    elif page == "Settings":
        st.subheader("⚙️ Settings")
        new_name = st.text_input("Display Name", profile.get("display_name"))
        new_country = st.text_input("Home Country", profile.get("home_country"))
        if st.button("Save Changes"):
            profile["display_name"] = new_name
            profile["home_country"] = new_country
            save_users()
            st.success("Settings updated!")

    # Theme
    st.sidebar.markdown("---")
    new_bg = st.sidebar.color_picker("Theme Color", st.session_state.bg_color)
    if st.sidebar.button("Apply"):
        st.session_state.bg_color = new_bg
        st.rerun()
