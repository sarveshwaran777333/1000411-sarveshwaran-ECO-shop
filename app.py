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
    # Clean the strings: remove commas, lowercase them, and strip spaces
    u_home = user_home.lower().replace(",", "").strip()
    p_origin = product_origin.lower().replace(",", "").strip()
    
    # Check if the product origin contains the home location or common local keywords
    if u_home in p_origin or p_origin in u_home or p_origin in ["local", "nearby", "home"]:
        return 1.0  # Local
    elif p_origin == "":
        return 1.3  # Regional/Default
    else:
        return 1.8  # International

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
        n_home = st.text_input("Your City/Country (e.g., Madurai, India)")
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

# ---------------- MAIN APP ----------------
else:
    user = st.session_state.user
    profile = users[user]
    
    st.sidebar.markdown(f"👋 Hello, **{profile.get('display_name', user)}**")
    st.sidebar.caption(f"📍 Home: {profile.get('home_country', 'Not set')}")
    show_sidebar_mascot(user)
    
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    page = st.sidebar.radio("Navigate", ["Home", "Add Purchase", "Dashboard", "Settings"])

    if page == "Home":
        st.title("GreenBasket")
        st.write(f"We are analyzing your shopping footprint based on your location in **{profile.get('home_country')}**.")

    elif page == "Add Purchase":
        st.subheader("🛒 Add a Purchase")
        col1, col2 = st.columns(2)
        with col1:
            prod_name = st.text_input("Product Name")
            brand_name = st.text_input("Brand")
            price_val = st.number_input("Price", min_value=0.0)
        with col2:
            cat_name = st.selectbox("Category", list(PRODUCT_IMPACT.keys()))
            origin_name = st.text_input("Where is it from? (e.g., Madurai, China, USA)")

        if st.button("Add Purchase"):
            if prod_name and origin_name and price_val > 0:
                user_home = profile.get("home_country", "Unknown")
                mult = calculate_multiplier(user_home, origin_name)
                co2_score = round(price_val * PRODUCT_IMPACT[cat_name] * mult, 2)
                
                # Using consistent keys to avoid "None" columns
                profile["purchases"].append({
                    "Product": prod_name, 
                    "Brand": brand_name, 
                    "Category": cat_name, 
                    "Origin": origin_name, 
                    "Price": price_val, 
                    "CO2 Impact": co2_score,
                    "Type": "Local" if mult == 1.0 else "International"
                })
                save_users()
                st.success("Purchase added successfully!")
                st.rerun()

    elif page == "Dashboard":
        st.subheader("📊 Your Carbon Footprint")
        if not profile.get("purchases"): 
            st.info("No data yet. Go to 'Add Purchase' to start.")
        else:
            df = pd.DataFrame(profile["purchases"])
            # Only show the relevant columns
            display_cols = ["Product", "Brand", "Category", "Origin", "Price", "CO2 Impact", "Type"]
            # Filter to only existing columns in the dataframe
            actual_cols = [c for c in display_cols if c in df.columns]
            
            m1, m2 = st.columns(2)
            m1.metric("Total Spending", f"${df['Price'].sum() if 'Price' in df.columns else 0:.2f}")
            m2.metric("Total CO2 (kg)", f"{df['CO2 Impact'].sum() if 'CO2 Impact' in df.columns else 0:.2f}")
            
            st.dataframe(df[actual_cols], use_container_width=True)

    elif page == "Settings":
        st.subheader("⚙️ Settings")
        u_name = st.text_input("Display Name", profile.get("display_name"))
        u_home = st.text_input("Home Location", profile.get("home_country"))
        
        if st.button("Update Profile"):
            profile["display_name"] = u_name
            profile["home_country"] = u_home
            save_users()
            st.success("Updated!")
            
        st.divider()
        st.error("Danger Zone")
        if st.button("Clear All Purchase History"):
            profile["purchases"] = []
            save_users()
            st.success("History cleared! Your table will be clean now.")
            st.rerun()

    # Theme
    st.sidebar.markdown("---")
    st.session_state.bg_color = st.sidebar.color_picker("Theme", st.session_state.bg_color)
    if st.sidebar.button("Apply Theme"):
        st.rerun()
