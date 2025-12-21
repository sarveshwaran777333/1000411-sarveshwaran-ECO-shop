import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime

# ---------------- 1. PAGE CONFIGURATION ----------------
st.set_page_config(page_title="GreenBasket", layout="wide")

USER_FILE = "users.json"

# ---------------- 2. THEME & CSS HANDLING ----------------
# Initialize session state for background color
if "bg_color" not in st.session_state:
    st.session_state.bg_color = "#e8f5e9"  # Default light green

def get_text_color(hex_color):
    """
    Determines if text should be black or white based on background brightness.
    """
    hex_color = hex_color.lstrip('#')
    try:
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        brightness = (r * 0.299 + g * 0.587 + b * 0.114)
        return "black" if brightness > 128 else "white"
    except:
        return "black"

def set_appearance(bg_color):
    """
    Injects CSS to force colors on all elements, specifically fixing Input fields.
    """
    text_color = get_text_color(bg_color)
    
    # We define the CSS in a Python string to avoid SyntaxErrors
    # input, textarea rule forces the text inside the box to be visible
    css_styles = f"""
    <style>
    /* GLOBAL APP BACKGROUND & TEXT */
    .stApp, [data-testid="stAppViewContainer"] {{
        background-color: {bg_color} !important;
        color: {text_color} !important;
    }}

    /* INPUT FIELDS - FORCE VISIBILITY */
    /* This targets the specific text box where you type */
    input, textarea {{
        color: {text_color} !important;
        -webkit-text-fill-color: {text_color} !important;
        caret-color: {text_color} !important;
    }}
    
    /* This targets the container around the input (the box itself) */
    [data-baseweb="input"] {{
        background-color: rgba(255,255,255,0.15) !important;
        border: 1px solid {text_color} !important;
    }}
    
    /* PLACEHOLDER TEXT (Username/Password hints) */
    ::placeholder {{
        color: {text_color} !important;
        opacity: 0.6 !important;
    }}

    /* TAB LABELS (Login / Signup) */
    button[data-baseweb="tab"] p {{
        color: {text_color} !important;
        font-weight: bold !important;
    }}

    /* BUTTON STYLING */
    div.stButton > button {{
        color: {text_color} !important;
        background-color: transparent !important;
        border: 2px solid {text_color} !important;
        border-radius: 8px;
    }}
    div.stButton > button:hover {{
        background-color: {text_color} !important;
        color: {bg_color} !important;
    }}

    /* DROPDOWNS & SELECTBOXES */
    /* Keep dropdown menu text black for readability against white popups */
    div[role="listbox"] ul li {{
        color: black !important;
    }}
    </style>
    """
    st.markdown(css_styles, unsafe_allow_html=True)

# Apply the theme immediately so Login page is styled
set_appearance(st.session_state.bg_color)

# ---------------- 3. DATA MANAGEMENT ----------------
if not os.path.exists(USER_FILE):
    with open(USER_FILE, "w") as f:
        json.dump({}, f)

with open(USER_FILE, "r") as f:
    users = json.load(f)

def save_users():
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)

# ---------------- 4. CO₂ CALCULATION LOGIC ----------------
IMPACT_MULTIPLIER = {
    "Clothing": 2.5,
    "Electronics": 4.0,
    "Groceries": 1.2,
    "Furniture": 3.0,
    "Second-hand": 0.5
}

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

# ---------------- 5. AUTHENTICATION (Login/Signup) ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🌱 GreenBasket")
    st.write("Welcome! Please login to track your eco-footprint.")
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        u_login = st.text_input("Username", key="login_u")
        p_login = st.text_input("Password", type="password", key="login_p")
        if st.button("Login"):
            if u_login in users and users[u_login]["password"] == p_login:
                st.session_state.logged_in = True
                st.session_state.user = u_login
                st.rerun()
            else:
                st.error("Invalid username or password.")

    with tab2:
        new_u = st.text_input("New Username", key="signup_u")
        new_p = st.text_input("New Password", type="password", key="signup_p")
        new_city = st.text_input("Home City/Country", key="signup_c")
        
        if st.button("Create Account"):
            if new_u and new_p and new_city:
                if new_u in users:
                    st.error("User already exists.")
                else:
                    users[new_u] = {
                        "password": new_p,
                        "home": new_city,
                        "purchases": []
                    }
                    save_users()
                    st.success("Account created! Please switch to the Login tab.")
            else:
                st.warning("Please fill in all fields.")

# ---------------- 6. MAIN APPLICATION ----------------
else:
    user = st.session_state.user
    profile = users[user]
    
    # Sidebar Navigation
    st.sidebar.markdown(f"## 👋 Hello, **{user}**")
    st.sidebar.markdown("---")
    
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    page = st.sidebar.radio("Navigate", ["Home", "Add Purchase", "Dashboard", "Settings"])

    # --- HOME PAGE ---
    if page == "Home":
        st.title("🌍 Conscious Shopping Dashboard")
        st.write(f"Tracking impact for **{profile.get('home', 'Global')}**.")
        st.info("Use the sidebar to add purchases or view your stats.")

    # --- ADD PURCHASE PAGE ---
    elif page == "Add Purchase":
        st.subheader("➕ Add a Purchase")
        
        col1, col2 = st.columns(2)
        with col1:
            product = st.selectbox("Product Type", list(IMPACT_MULTIPLIER.keys()))
            brand = st.text_input("Brand Name")
            price = st.number_input("Price", min_value=0.0, format="%.2f")
        
        with col2:
            origin = st.selectbox("Origin", list(DISTANCE_FACTOR.keys()))
            transport = st.selectbox("Transport Mode", list(TRANSPORT_FACTOR.keys()))

        if st.button("Add to Basket"):
            # Calculate CO2 Impact
            co2_score = (
                price 
                * IMPACT_MULTIPLIER[product] 
                * TRANSPORT_FACTOR[transport] 
                * DISTANCE_FACTOR[origin]
            )
            
            # Save to user profile
            profile["purchases"].append({
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "product": product,
                "brand": brand,
                "price": price,
                "origin": origin,
                "impact": round(co2_score, 2)
            })
            save_users()
            st.success(f"Added! Estimated CO₂ Impact: {co2_score:.2f}")

    # --- DASHBOARD PAGE ---
    elif page == "Dashboard":
        st.subheader("📊 Your Impact Analytics")
        
        if not profile["purchases"]:
            st.info("No purchases recorded yet. Go to 'Add Purchase' to start!")
        else:
            df = pd.DataFrame(profile["purchases"])
            
            # Summary Metrics
            total_spent = df["price"].sum()
            total_co2 = df["impact"].sum()
            
            m1, m2 = st.columns(2)
            m1.metric("Total Spending", f"₹{total_spent:.2f}")
            m2.metric("Total CO₂ Footprint", f"{total_co2:.2f} kg")
            
            st.divider()
            st.write("### Recent Transactions")
            st.dataframe(df, use_container_width=True)

            st.write("### Impact Breakdown")
            st.bar_chart(df, x="product", y="impact")

    # --- SETTINGS PAGE ---
    elif page == "Settings":
        st.subheader("⚙️ App Settings")
        
        st.write("Customize the look of your GreenBasket app.")
        
        # Color Picker
        new_color = st.color_picker("Background Color", st.session_state.bg_color)
        
        if st.button("Apply Theme"):
            st.session_state.bg_color = new_color
            st.rerun()
