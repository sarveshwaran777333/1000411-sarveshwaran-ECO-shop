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

# ---------------- DYNAMIC THEME HANDLER ----------------
if "bg_color" not in st.session_state:
    st.session_state.bg_color = "#e8f5e9"

def get_text_color(hex_color):
    """Calculates if text should be black or white based on background brightness."""
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    brightness = (r * 0.299 + g * 0.587 + b * 0.114)
    return "black" if brightness > 128 else "white"

def set_appearance(bg_color):
    text_color = get_text_color(bg_color)
    
    st.markdown(
        f"""
        <style>
        /* Main App Background */
        .stApp {{
            background-color: {bg_color};
            color: {text_color};
        }}
        
        /* All standard text and headers */
        .stApp h1, .stApp h2, .stApp h3, .stApp p, .stApp label, .stApp span, .stApp .stMarkdown {{
            color: {text_color} !important;
        }}

        /* Buttons Styling */
        div.stButton > button {{
            color: {text_color} !important;
            background-color: transparent;
            border: 2px solid {text_color} !important;
        }}
        div.stButton > button:hover {{
            background-color: {text_color};
            color: {bg_color} !important;
        }}

        /* DROPDOWN & INPUT TEXT COLOR (The fix for your screenshot) */
        /* This targets the text inside the selection boxes and input fields */
        div[data-baseweb="select"] > div, 
        div[data-baseweb="input"] > div,
        input {{
            color: {text_color} !important;
            -webkit-text-fill-color: {text_color} !important;
        }}
        
        /* Dropdown Icon color */
        svg[data-testid="stIcon"] {{
            fill: {text_color} !important;
        }}

        /* Sidebar Styling */
        [data-testid="stSidebar"] {{
            background-color: {bg_color};
            border-right: 1px solid {text_color};
        }}
        
        /* Metric Labels */
        [data-testid="stMetricValue"] {{
            color: {text_color} !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

set_appearance(st.session_state.bg_color)

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
    "Electronics": 5.0, "Clothing": 2.0, "Food": 1.0, "Household": 1.5, "Transport": 4.0
}

PRODUCT_LISTS = {
    "Electronics": ["Laptop", "Mobile Phone", "Headphones", "Smart Watch", "Television"],
    "Clothing": ["T-Shirt", "Jeans", "Jacket", "Shoes", "Dress"],
    "Food": ["Vegetables", "Fruits", "Meat", "Dairy", "Snacks"],
    "Household": ["Furniture", "Cleaning Supplies", "Kitchenware", "Decor"],
    "Transport": ["Bicycle", "Electric Scooter", "Car Spare Parts", "Fuel"]
}

def calculate_multiplier(user_home, product_origin):
    u_home = str(user_home).lower().replace(",", "").strip()
    p_origin = str(product_origin).lower().replace(",", "").strip()
    if u_home in p_origin or p_origin in u_home or p_origin in ["local", "home"]:
        return 1.0  
    return 1.8 if p_origin else 1.3

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
                st.toast(f"Welcome back! Use the sidebar for your Dashboard.")
                st.rerun()
            else: st.error("Invalid credentials")
    with tab2:
        n_u = st.text_input("New Username")
        n_p = st.text_input("New Password", type="password")
        n_home = st.text_input("Your City/Country")
        if st.button("Sign Up"):
            if n_u and n_p and n_home:
                users[n_u] = {"password": n_p, "display_name": n_u, "home_country": n_home, "purchases": []}
                save_users()
                st.success("Account created! Please log in.")

# ---------------- MAIN APP ----------------
else:
    user = st.session_state.user
    profile = users[user]
    
    # --- DATA MIGRATION ---
    for p in profile.get("purchases", []):
        if "Price" in p and "Price_INR" not in p:
            p["Price_INR"] = p.pop("Price")
        if "product" in p and "Product" not in p:
            p["Product"] = p.pop("product")
    
    # Sidebar
    st.sidebar.markdown(f"👋 Hello, **{profile.get('display_name', user)}**")
    st.sidebar.caption(f"📍 Home: {profile.get('home_country')}")
    
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

    if page == "Home":
        st.title("GreenBasket")
        st.write(f"Tracking impact for your home in: **{profile.get('home_country')}**.")
        st.info("👈 Use the sidebar to go to your **Dashboard** or **Add a Purchase**.")

    elif page == "Add Purchase":
        st.subheader(f"🛒 Add Purchase ({curr_info['symbol']})")
        col1, col2 = st.columns(2)
        with col1:
            cat = st.selectbox("Category", list(PRODUCT_IMPACT.keys()))
            prod = st.selectbox("Product Name", PRODUCT_LISTS.get(cat, ["Other"]))
            brand = st.text_input("Brand")
        with col2:
            price_input = st.number_input(f"Price ({curr_info['symbol']})", min_value=0.0)
            origin = st.text_input("Origin (City/Country)")

        if st.button("Add to Basket"):
            if prod and origin and price_input > 0:
                price_in_inr = price_input / curr_info["rate"]
                mult = calculate_multiplier(profile.get("home_country", ""), origin)
                co2 = round(price_in_inr * PRODUCT_IMPACT[cat] * mult, 2)
                
                profile["purchases"].append({
                    "Product": prod, "Brand": brand, "Category": cat, 
                    "Origin": origin, "Price_INR": price_in_inr, 
                    "CO2 Impact": co2, "Type": "Local" if mult == 1.0 else "International"
                })
                save_users()
                st.toast("Item Added! View results in Dashboard 📊")
                st.rerun()

    elif page == "Dashboard":
        st.subheader("📊 Your Dashboard")
        if not profile.get("purchases"): 
            st.info("No data yet. Go to 'Add Purchase' to begin.")
        else:
            df = pd.DataFrame(profile["purchases"])
            df[f"Price ({curr_info['symbol']})"] = (df["Price_INR"] * curr_info["rate"]).round(2)
            
            m1, m2 = st.columns(2)
            m1.metric("Total Spending", f"{curr_info['symbol']} {df[f'Price ({curr_info['symbol']})'].sum():.2f}")
            m2.metric("Total CO₂ (kg)", f"{df['CO2 Impact'].sum():.2f}")
            
            st.dataframe(df.drop(columns=["Price_INR"], errors='ignore'), use_container_width=True)

    elif page == "Settings":
        st.subheader("⚙️ Settings")
        st.session_state.bg_color = st.color_picker("Change App Background", st.session_state.bg_color)
        if st.button("Apply Theme"):
            st.rerun()
        
        st.divider()
        if st.button("Clear History"):
            profile["purchases"] = []
            save_users()
            st.rerun()
