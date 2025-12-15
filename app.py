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

def total_co2(user):
    purchases = users[user]["purchases"]
    return sum(p["co2"] for p in purchases) if purchases else 0

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
        st.sidebar.image(path, width=150)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username_input" not in st.session_state:
    st.session_state.username_input = ""

if "password_input" not in st.session_state:
    st.session_state.password_input = ""

if not st.session_state.logged_in:
    st.title("🌱 GreenBasket")

    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        username = st.text_input(
            "Username",
            value=st.session_state.username_input
        )
        password = st.text_input(
            "Password",
            type="password",
            value=st.session_state.password_input
        )

        st.session_state.username_input = username
        st.session_state.password_input = password

        if st.button("Login"):
            if username in users and users[username]["password"] == password:
                st.session_state.logged_in = True
                st.session_state.user = username
                st.rerun()
            else:
                st.error("Invalid username or password")

    with tab2:
        new_user = st.text_input(
            "New Username",
            value=st.session_state.username_input
        )
        new_pass = st.text_input(
            "New Password",
            type="password",
            value=st.session_state.password_input
        )

        st.session_state.username_input = new_user
        st.session_state.password_input = new_pass

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
    show_sidebar_mascot(user)

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    page = st.sidebar.radio(
        "Navigate",
        ["Home", "Add Purchase", "Dashboard", "Eco Tips"]
    )

    if page == "Home":
        st.title("GreenBasket")
        st.write(
            "GreenBasket helps users track shopping habits and "
            "understand their carbon footprint."
        )

    elif page == "Add Purchase":
        st.subheader("🛒 Add a Purchase")

        product = st.text_input("Product Name")
        brand = st.text_input("Brand")
        category = st.selectbox(
            "Category",
            list(PRODUCT_IMPACT.keys())
        )
        price = st.number_input("Price", min_value=0.0, step=1.0)

        if st.button("Add Purchase"):
            if product and brand and price > 0:
                co2 = round(price * PRODUCT_IMPACT[category], 2)

                users[user]["purchases"].append({
                    "product_name": product,
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
