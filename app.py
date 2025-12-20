import streamlit as st
import json
import os
import pandas as pd

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="GreenBasket", layout="wide")

USER_FILE = "users.json"

# Ensure these files exist in your "image" folder
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
        .stApp {{
            background-color: {color};
        }}
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

LOCATION_MULTIPLIER = {
    "Local": 1.0,
    "Regional": 1.3,
    "International": 1.8
}

def total_co2(username):
    # Safely calculate total CO2 from the user's purchase list
    user_data = users.get(username, {})
    purchases = user_data.get("purchases", [])
    return sum(p.get("co2", 0) for p in purchases)

def get_mascot(username):
    total = total_co2(username)
    if total == 0:
        return MASCOT_DEFAULT
    elif total <= LOW_CO2_LIMIT:
        return MASCOT_LOW
    else:
        return MASCOT_HIGH

def show_sidebar_mascot(username):
    path = get_mascot(username)
    if os.path.exists(path):
        st.sidebar.image(path, width=160)

# ---------------- SESSION ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ---------------- AUTH ----------------
if not st.session_state.logged_in:
    st.title("🌱 GreenBasket")
    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        username_input = st.text_input("Username")
        password_input = st.text_input("Password", type="password")
        if st.button("Login"):
            if username_input in users and users[username_input]["password"] == password_input:
                st.session_state.logged_in = True
                st.session_state.user = username_input
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:
        new_user = st.text_input("New Username")
        new_pass = st.text_input("New Password", type="password")
        if st.button("Sign Up"):
            if new_user in users:
                st.error("Username already exists")
            elif new_user and new_pass:
                users[new_user] = {
                    "password": new_pass,
                    "display_name": new_user,
                    "purchases": []
                }
                save_users()
                st.success("Account created. Please login.")

# ---------------- MAIN APP ----------------
else:
    user = st.session_state.user
    profile = users[user]
    
    # Ensure necessary keys exist
    if "display_name" not in profile: profile["display_name"] = user
    if "purchases" not in profile: profile["purchases"] = []

    # Sidebar UI
    st.sidebar.markdown(f"👋 Hello, **{profile['display_name']}**")
    show_sidebar_mascot(user)

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    page = st.sidebar.radio(
        "Navigate",
        ["Home", "Add Purchase", "Dashboard", "Eco Tips", "Settings"]
    )

    # ---------- HOME ----------
    if page == "Home":
        st.title("GreenBasket")
        st.write("Track your shopping habits, understand carbon footprints, and make environmentally conscious choices.")
        st.info("Navigate to 'Add Purchase' to start tracking your items.")

    # ---------- ADD PURCHASE ----------
    elif page == "Add Purchase":
        st.subheader("🛒 Add a Purchase")
        
        col1, col2 = st.columns(2)
        with col1:
            product_name = st.text_input("Product Name")
            brand = st.text_input("Brand")
            price = st.number_input("Price", min_value=0.0, step=1.0)
            
        with col2:
            category = st.selectbox("Category", list(PRODUCT_IMPACT.keys()))
            source_loc = st.selectbox("Product Source (Location)", list(LOCATION_MULTIPLIER.keys()))

        if st.button("Add Purchase"):
            if product_name and brand and price > 0:
                # Calculation logic
                base_impact = PRODUCT_IMPACT[category]
                multiplier = LOCATION_MULTIPLIER[source_loc]
                co2_score = round(price * base_impact * multiplier, 2)

                # Append to user history
                new_item = {
                    "product": product_name,
                    "brand": brand,
                    "category": category,
                    "location": source_loc,
                    "price": price,
                    "co2": co2_score
                }
                profile["purchases"].append(new_item)
                save_users()
                
                st.success(f"Added {product_name}! Estimated CO₂: {co2_score} kg")
                st.rerun()
            else:
                st.error("Please fill in all fields.")

    # ---------- DASHBOARD ----------
    elif page == "Dashboard":
        st.subheader("📊 Your Environmental Dashboard")
        if not profile["purchases"]:
            st.info("Your basket is empty. Add purchases to see your impact.")
        else:
            df = pd.DataFrame(profile["purchases"])
            
            # Key Metrics
            m1, m2 = st.columns(2)
            m1.metric("Total Spending", f"${df['price'].sum():.2f}")
            m2.metric("Total CO₂ (kg)", f"{df['co2'].sum():.2f}")
            
            # Data Table
            st.write("### Purchase History")
            st.dataframe(df[["product", "brand", "category", "location", "price", "co2"]], use_container_width=True)

    # ---------- ECO TIPS ----------
    elif page == "Eco Tips":
        st.subheader("🌍 Eco-Friendly Tips")
        tips = [
            "**Buy Local:** Items sourced locally have a lower transport footprint.",
            "**Check Categories:** Electronics usually have the highest manufacturing impact.",
            "**Quality over Quantity:** Buying long-lasting items reduces waste over time.",
            "**Eco-Labels:** Look for certified organic or fair-trade brands."
        ]
        for tip in tips:
            st.markdown(f"- {tip}")

    # ---------- SETTINGS ----------
    elif page == "Settings":
        st.subheader("⚙️ User Settings")
        new_display = st.text_input("Change Display Name", value=profile["display_name"])
        
        if st.button("Update Profile"):
            profile["display_name"] = new_display
            save_users()
            st.success("Profile updated!")

# ---------------- APPEARANCE (SIDEBAR BOTTOM) ----------------
st.sidebar.markdown("---")
st.sidebar.markdown("### 🎨 Appearance")
new_bg = st.sidebar.color_picker("Choose Background Color", st.session_state.bg_color)

if st.sidebar.button("Apply Theme"):
    st.session_state.bg_color = new_bg
    st.rerun()
