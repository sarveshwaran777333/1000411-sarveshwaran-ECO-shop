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

# ---------------- CURRENCY SETTINGS ----------------
CURRENCY_MAP = {
    "INR (₹)": {"symbol": "₹", "rate": 1.0},
    "USD ($)": {"symbol": "$", "rate": 0.012},
    "EUR (€)": {"symbol": "€", "rate": 0.011}
}

if "currency" not in st.session_state:
    st.session_state.currency = "INR (₹)"

# ---------------- BACKGROUND HANDLER ----------------
if "bg_color" not in st.session_state:
    st.session_state.bg_color = "#e8f5e9"

def set_background(color):
    st.markdown(f"<style>.stApp {{ background-color: {color}; }}</style>", unsafe_allow_html=True)

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

# ---------------- CO₂ LOGIC & PRODUCTS ----------------
PRODUCT_IMPACT = {
    "Electronics": 5.0, "Clothing": 2.0, "Food": 1.0, "Household": 1.5, "Transport": 4.0
}

PRODUCT_LISTS = {
    "Electronics": ["Laptop", "Mobile Phone", "Headphones", "Smart Watch", "Television", "Tablet"],
    "Clothing": ["T-Shirt", "Jeans", "Jacket", "Shoes", "Dress", "Socks"],
    "Food": ["Vegetables", "Fruits", "Meat", "Dairy", "Grains", "Snacks"],
    "Household": ["Furniture", "Cleaning Supplies", "Kitchenware", "Bedding", "Decor"],
    "Transport": ["Bicycle", "Electric Scooter", "Car Spare Parts", "Fuel", "Bus Pass"]
}

def calculate_multiplier(user_home, product_origin):
    u_home = user_home.lower().replace(",", "").strip()
    p_origin = product_origin.lower().replace(",", "").strip()
    
    # If home location matches origin or origin is empty/local keywords
    if u_home in p_origin or p_origin in u_home or p_origin in ["local", "nearby", "home"]:
        return 1.0  # Local
    elif not p_origin:
        return 1.3  # Regional/Default
    else:
        return 1.8  # International (Higher footprint)

def total_co2(username):
    user_data = users.get(username, {})
    return sum(p.get("CO2 Impact", 0) for p in user_data.get("purchases", []))

def get_mascot(username):
    total = total_co2(username)
    if total == 0: return MASCOT_DEFAULT
    return MASCOT_LOW if total <= LOW_CO2_LIMIT else MASCOT_HIGH

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
    
    # Sidebar: Mascot and Currency
    st.sidebar.markdown(f"👋 Hello, **{profile.get('display_name', user)}**")
    st.sidebar.caption(f"📍 Home: {profile.get('home_country')}")
    
    # Show Mascot
    m_path = get_mascot(user)
    if os.path.exists(m_path):
        st.sidebar.image(m_path, width=150)
    
    st.sidebar.markdown("---")
    st.session_state.currency = st.sidebar.selectbox("Select Currency", list(CURRENCY_MAP.keys()))
    curr_info = CURRENCY_MAP[st.session_state.currency]

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    page = st.sidebar.radio("Navigate", ["Home", "Add Purchase", "Dashboard", "Settings"])

    # ---------- HOME ----------
    if page == "Home":
        st.title("GreenBasket")
        st.write(f"Your eco-shopping assistant. Comparing product footprints against your home in **{profile.get('home_country')}**.")

    # ---------- ADD PURCHASE ----------
    elif page == "Add Purchase":
        st.subheader(f"🛒 Add a Purchase ({curr_info['symbol']})")
        col1, col2 = st.columns(2)
        
        with col1:
            cat_selected = st.selectbox("Category", list(PRODUCT_IMPACT.keys()))
            # Dynamic dropdown for products
            available_prods = PRODUCT_LISTS.get(cat_selected, ["Other"])
            prod_selected = st.selectbox("Product Name", available_prods)
            brand_name = st.text_input("Brand")
            
        with col2:
            price_input = st.number_input(f"Price in {st.session_state.currency}", min_value=0.0)
            origin_name = st.text_input("Where is it from? (e.g., Madurai, China, USA)")

        if st.button("Add to Basket"):
            if prod_selected and origin_name and price_input > 0:
                # Convert price to INR for storage consistency
                price_in_inr = price_input / curr_info["rate"]
                
                # Compare locations for CO2 multiplier
                u_home = profile.get("home_country", "Unknown")
                mult = calculate_multiplier(u_home, origin_name)
                
                co2_score = round(price_in_inr * PRODUCT_IMPACT[cat_selected] * mult, 2)
                
                profile["purchases"].append({
                    "Product": prod_selected, 
                    "Brand": brand_name, 
                    "Category": cat_selected, 
                    "Origin": origin_name, 
                    "Price_INR": price_in_inr, 
                    "CO2 Impact": co2_score,
                    "Type": "Local" if mult == 1.0 else "International"
                })
                save_users()
                st.success(f"Added {prod_selected}! CO₂ Score: {co2_score} kg")
                st.rerun()

    # ---------- DASHBOARD ----------
    elif page == "Dashboard":
        st.subheader("📊 Your Dashboard")
        if not profile.get("purchases"): 
            st.info("No data yet. Start shopping!")
        else:
            df = pd.DataFrame(profile["purchases"])
            
            # Convert stored INR to displayed Currency
            df[f"Price ({curr_info['symbol']})"] = (df["Price_INR"] * curr_info["rate"]).round(2)
            
            m1, m2 = st.columns(2)
            m1.metric("Total Spending", f"{curr_info['symbol']} {df[f'Price ({curr_info['symbol']})'].sum():.2f}")
            m2.metric("Total CO₂ (kg)", f"{df['CO2 Impact'].sum():.2f}")
            
            # Display table (hiding the hidden INR column)
            display_df = df[["Product", "Brand", "Category", "Origin", f"Price ({curr_info['symbol']})", "CO2 Impact", "Type"]]
            st.dataframe(display_df, use_container_width=True)

    # ---------- SETTINGS ----------
    elif page == "Settings":
        st.subheader("⚙️ Settings")
        new_name = st.text_input("Display Name", profile.get("display_name"))
        new_home = st.text_input("Home Location", profile.get("home_country"))
        
        if st.button("Update Profile"):
            profile["display_name"] = new_name
            profile["home_country"] = new_home
            save_users()
            st.success("Updated successfully!")
            
        st.divider()
        st.session_state.bg_color = st.color_picker("App Background Color", st.session_state.bg_color)
        if st.button("Apply Background"):
            st.rerun()
            
        if st.button("Clear Purchase History"):
            profile["purchases"] = []
            save_users()
            st.success("History wiped.")
            st.rerun()
