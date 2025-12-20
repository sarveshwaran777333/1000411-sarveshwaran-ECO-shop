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

def total_co2(user):
    return sum(p["co2"] for p in users[user]["purchases"])

def get_mascot(user):
    total = total_co2(user)
    if total == 0:
        return MASCOT_DEFAULT
    elif total <= LOW_CO2_LIMIT:
        return MASCOT_LOW
    else:
        return MASCOT_HIGH

def show_sidebar_mascot(user):
    path = get_mascot(user)
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
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if username in users and users[username]["password"] == password:
                st.session_state.logged_in = True
                st.session_state.user = username
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
                    "location": "Local",
                    "purchases": []
                }
                save_users()
                st.success("Account created. Please login.")

# ---------------- MAIN APP ----------------
else:
    user = st.session_state.user
    profile = users[user]
    if "display_name" not in profile:
        profile["display_name"] = user
    if "location" not in profile:
        profile["location"] = "Local"
    if "purchases" not in profile:
        profile["purchases"] = []

save_users()


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
        st.write(
            "Track your shopping habits, understand carbon footprints, "
            "and make environmentally conscious choices."
        )

    # ---------- ADD PURCHASE ----------
    elif page == "Add Purchase":
        st.subheader("🛒 Add a Purchase")

        product = st.text_input("Product Name")
        brand = st.text_input("Brand")
        category = st.selectbox("Category", PRODUCT_IMPACT.keys())
        price = st.number_input("Price", min_value=0.0, step=1.0)

        if st.button("Add Purchase"):
            if product and brand and price > 0:
                base = PRODUCT_IMPACT[category]
                location_factor = LOCATION_MULTIPLIER[profile["location"]]
                co2 = round(price * base * location_factor, 2)

                users[user]["purchases"].append({
                    "product": product,
                    "brand": brand,
                    "category": category,
                    "price": price,
                    "co2": co2
                })

                save_users()
                st.success("Purchase added successfully")
                st.rerun()
            else:
                st.error("Please fill all fields")

    # ---------- DASHBOARD ----------
    elif page == "Dashboard":
        st.subheader("📊 Dashboard")

        if not profile["purchases"]:
            st.info("No purchases yet.")
        else:
            df = pd.DataFrame(profile["purchases"])

            col1, col2 = st.columns(2)
            col1.metric("Total Spend", f"{df['price'].sum():.2f}")
            col2.metric("Total CO₂ Impact (kg)", f"{df['co2'].sum():.2f}")

            st.dataframe(df, use_container_width=True)

    # ---------- ECO TIPS ----------
    elif page == "Eco Tips":
        st.subheader("🌍 Eco Tips")
        tips = [
            "Buy local products to reduce transport emissions.",
            "Avoid single-use plastics.",
            "Repair instead of replacing items.",
            "Choose second-hand goods."
        ]
        for tip in tips:
            st.markdown(f"- {tip}")

    # ---------- SETTINGS ----------
    elif page == "Settings":
        st.subheader("⚙️ Settings")

        display_name = st.text_input(
            "Display Name",
            value=profile["display_name"]
        )

        location = st.selectbox(
            "Your Location",
            LOCATION_MULTIPLIER.keys(),
            index=list(LOCATION_MULTIPLIER.keys()).index(profile["location"])
        )

        if st.button("Save Profile Settings"):
            profile["display_name"] = display_name
            profile["location"] = location
            save_users()
            st.success("Profile updated")

st.markdown("### 🎨 Change background")
st.markdown(
    """
    <style>
    /* Strong black outline for color picker */
    input[type=color] {
        border: 3px solid black !important;
        border-radius: 8px !important;
        box-shadow: 0 0 0 2px black inset;
        height: 50px !important;
        width: 50px !important;
        cursor: pointer;
        margin-bottom: 10px;
    }

    /* Black outline when focused */
    input[type=color]:focus {
        outline: 2px solid black !important;
    }

    /* Apply Background button styling */
    .apply-bg-btn button {
        margin-top: 10px;
        padding: 10px 20px;
        background-color: #111;
        color: white;
        border-radius: 8px;
        border: 2px solid black;
        cursor: pointer;
        font-weight: bold;
    }

    .apply-bg-btn button:hover {
        background-color: #222;
    }
    </style>
    """,
    unsafe_allow_html=True
)

new_color = st.color_picker(
    "Pick a background colour",
    st.session_state.bg_color
)

st.markdown('<div class="apply-bg-btn">', unsafe_allow_html=True)
if st.button("Apply Background Color"):
    st.session_state.bg_color = new_color
    set_background(st.session_state.bg_color)
st.markdown('</div>', unsafe_allow_html=True)
