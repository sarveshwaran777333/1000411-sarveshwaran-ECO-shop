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
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    brightness = (r * 0.299 + g * 0.587 + b * 0.114)
    return "black" if brightness > 128 else "white"

def set_appearance(bg_color):
    text_color = get_text_color(bg_color)
    
    st.markdown(
        f"""
        <style>
        /* 1. GLOBAL APP & TEXT OVERRIDE */
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{
            background-color: {bg_color} !important;
        }}
        
        /* Force color on every text element including inputs */
        * {{
            color: {text_color} ;
        }}

        h1, h2, h3, p, label, span, .stMarkdown {{
            color: {text_color} !important;
        }}

        /* 2. THE ULTIMATE INPUT FIX (Forces text you type) */
        input {{
            color: {text_color} !important;
            -webkit-text-fill-color: {text_color} !important;
        }}

        /* Target Streamlit's internal input container */
        [data-baseweb="input"] {{
            background-color: rgba(255,255,255,0.05) !important;
            border: 1px solid {text_color}55 !important;
        }}

        /* Target the typing area specifically */
        [data-baseweb="input"] input {{
            color: {text_color} !important;
            -webkit-text-fill-color: {text_color} !important;
        }}

        /* 3. TABS FIX (Login/Signup) */
        button[data-baseweb="tab"] p {{
            color: {text_color} !important;
        }}
        
        /* 4. BUTTONS */
        div.stButton > button {{
            color: {text_color} !important;
            background-color: transparent !important;
            border: 2px solid {text_color} !important;
        }}
        div.stButton > button:hover {{
            background-color: {text_color} !important;
            color: {bg_color} !important;
        }}

        /* 5. SIDEBAR */
        [data-testid="stSidebar"], [data-testid="stSidebarNav"] {{
            background-color: {bg_color} !important;
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

# ---------------- PRODUCT LOGIC ----------------
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

# ---------------- AUTH PAGE ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🌱 GreenBasket")
    t1, t2 = st.tabs(["Login", "Sign Up"])
    with t1:
        u_in = st.text_input("Username", key="l_user")
        p_in = st.text_input("Password", type="password", key="l_pass")
        if st.button("Login", key="l_btn"):
            if u_in in users and users[u_in]["password"] == p_in:
                st.session_state.logged_in = True
                st.session_state.user = u_in
                st.rerun()
            else: st.error("Invalid credentials")
    with t2:
        n_u = st.text_input("New Username", key="s_user")
        n_p = st.text_input("New Password", type="password", key="s_pass")
        n_h = st.text_input("Home City/Country", key="s_home")
        if st.button("Create Account", key="s_btn"):
            if n_u and n_p and n_h:
                users[n_u] = {"password": n_p, "display_name": n_u, "home_country": n_h, "purchases": []}
                save_users()
                st.success("Account created! Go to Login tab.")

# ---------------- MAIN APP ----------------
else:
    user = st.session_state.user
    profile = users[user]
    
    # Clean data columns
    for p in profile.get("purchases", []):
        if "product_name" in p: p["Product"] = p.pop("product_name")
        if "price" in p: p["Price_INR"] = p.pop("price")

    # Sidebar
    st.sidebar.markdown(f"👋 Hello, **{profile.get('display_name', user)}**")
    st.sidebar.markdown("---")
    st.session_state.currency = st.sidebar.selectbox("Currency", list(CURRENCY_MAP.keys()))
    curr_info = CURRENCY_MAP[st.session_state.currency]

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    page = st.sidebar.radio("Navigate", ["Home", "Add Purchase", "Dashboard", "Settings"])

    if page == "Home":
        st.title("GreenBasket")
        st.write(f"Eco-tracker for **{profile.get('home_country')}**.")
        # Navigation guide as requested earlier
        st.info("👈 Use the sidebar to find your **Dashboard** or **Add Purchase**.")

    elif page == "Add Purchase":
        st.subheader("🛒 Add Item")
        c1, c2 = st.columns(2)
        with c1:
            cat = st.selectbox("Category", list(PRODUCT_IMPACT.keys()))
            prod = st.selectbox("Product", PRODUCT_LISTS[cat])
            brand = st.text_input("Brand")
        with c2:
            price_val = st.number_input("Price", min_value=0.0)
            origin_val = st.text_input("Origin (City/Country)")
        
        if st.button("Add to Basket"):
            if prod and origin_val and price_val > 0:
                p_inr = price_val / curr_info["rate"]
                m = calculate_multiplier(profile["home_country"], origin_val)
                score = round(p_inr * PRODUCT_IMPACT[cat] * m, 2)
                profile["purchases"].append({
                    "Product": prod, "Brand": brand, "Category": cat, 
                    "Origin": origin_val, "Price_INR": p_inr, 
                    "CO2 Impact": score, "Type": "Local" if m == 1.0 else "International"
                })
                save_users(); st.toast("Added! Check Dashboard 📊"); st.rerun()

    elif page == "Dashboard":
        st.subheader("📊 Dashboard")
        if not profile["purchases"]: st.info("No data.")
        else:
            df = pd.DataFrame(profile["purchases"])
            df[f"Price ({curr_info['symbol']})"] = (df["Price_INR"] * curr_info["rate"]).round(2)
            st.dataframe(df[["Product", "Brand", "Category", "Origin", f"Price ({curr_info['symbol']})", "CO2 Impact", "Type"]], use_container_width=True)

    elif page == "Settings":
        st.subheader("⚙️ Settings")
        st.session_state.bg_color = st.color_picker("App Color", st.session_state.bg_color)
        if st.button("Apply"): st.rerun()
