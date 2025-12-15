import streamlit as st
import json
import os
import pandas as pd

st.set_page_config(page_title="GreenBasket", layout="wide")

USER_FILE = "users.json"

MASCOT_DEFAULT = "image/Lion.png"
MASCOT_LOW = "image/Lion_Happy.png"
MASCOT_HIGH = "image/Lion_Sad.png"

LOW_CO2_LIMIT = 100

st.markdown("""
<style>
.mascot {
    text-align: center;
    margin-bottom: 15px;
}
</style>
""", unsafe_allow_html=True)

if not os.path.exists(USER_FILE):
    with open(USER_FILE, "w") as f:
        json.dump({}, f)

with open(USER_FILE, "r") as f:
    users = json.load(f)

def save_users():
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)

PRODUCT_IMPACT = {
    "Electronics": 5.0,
    "Clothing": 2.0,
    "Food": 1.0,
    "Household": 1.5,
    "Transport": 4.0
}

def get_total_co2():
    purchases = users[st.session_state.user]["purchases"]
    return sum(p["co2"] for p in purchases) if purchases else 0

def get_mascot():
    total = get_total_co2()
    if total == 0:
        return MASCOT_DEFAULT
    elif total <= LOW_CO2_LIMIT:
        return MASCOT_LOW
    else:
        return MASCOT_HIGH

def show_sidebar_mascot():
    path = get_mascot()
    if os.path.exists(path):
        st.sidebar.markdown(
            f"""
            <div class="mascot">
                <img src="{path}" width="150">
            </div>
            """,
            unsafe_allow_html=True
        )

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

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
                st.experimental_rerun()
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
                    "purchases": []
                }
                save_users()
                st.success("Account created. Please login.")
            else:
                st.error("All fields required")

else:
    user = st.session_state.user
    st.sidebar.markdown(f"👤 {user}")
    show_sidebar_mascot()

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.experimental_rerun()

    page = st.sidebar.radio(
        "Navigate",
        ["Home", "Add Purchase", "Dashboard", "Eco Tips"]
    )

    if page == "Home":
        st.title("GreenBasket")
        st.write(
            "Track your shopping habits and understand your carbon footprint."
        )

    elif page == "Add Purchase":
        st.subheader("🛒 Add a Purchase")

        name = st.text_input("Product Name")
        brand = st.text_input("Brand")
        category = st.selectbox(
            "Product Category",
            list(PRODUCT_IMPACT.keys())
        )
        price = st.number_input("Price", min_value=0.0, step=1.0)

        if st.button("Add Purchase"):
            if name and brand and price > 0:
                co2 = round(price * PRODUCT_IMPACT[category], 2)

                users[user]["purchases"].append({
                    "product_name": name,
                    "brand": brand,
                    "category": category,
                    "price": price,
                    "co2": co2
                })

                save_users()
                st.success("Purchase added successfully")
                st.experimental_rerun()
            else:
                st.error("Fill all fields")

    elif page == "Dashboard":
        st.subheader("📊 Dashboard")

        purchases = users[user]["purchases"]

        if not purchases:
            st.info("No purchases recorded yet.")
        else:
            df = pd.DataFrame(purchases)

            col1, col2 = st.columns(2)
            col1.metric("Total Spend", f"{df['price'].sum():.2f}")
            col2.metric("Total CO₂ Impact (kg)", f"{df['co2'].sum():.2f}")

            st.dataframe(df, use_container_width=True)

    elif page == "Eco Tips":
        st.subheader("🌍 Eco Tips")

        tips = [
            "Buy local products",
            "Avoid single-use plastics",
            "Repair instead of replacing",
            "Choose second-hand items"
        ]

        for tip in tips:
            st.markdown(f"- {tip}")
