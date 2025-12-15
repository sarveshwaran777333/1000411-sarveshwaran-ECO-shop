import streamlit as st
import json
import os
import pandas as pd

st.set_page_config(page_title="GreenBasket", layout="wide")

DATA_FILE = "data.json"

MASCOT_DEFAULT = "image/Lion.png"
MASCOT_HAPPY = "image/Lion_Happy.png"
MASCOT_SAD = "image/Lion_Sad.png"

st.markdown("""
<style>
.big-title {
  font-size: 36px;
  font-weight: 700;
  color: #2e7d32;
}
</style>
""", unsafe_allow_html=True)

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump([], f)

with open(DATA_FILE, "r") as f:
    purchases = json.load(f)

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(purchases, f, indent=4)

PRODUCT_IMPACT = {
    "Electronics": 5.0,
    "Clothing": 2.0,
    "Food": 1.0,
    "Household": 1.5,
    "Transport": 4.0
}

def calculate_impact(price, product_type):
    co2 = price * PRODUCT_IMPACT[product_type]
    if co2 < 50:
        return "Low Impact", "Eco Saver 🌱", "Great eco-friendly choice!", MASCOT_HAPPY
    elif co2 < 150:
        return "Medium Impact", "Low Impact Shopper 🌿", "Try greener options next time.", MASCOT_DEFAULT
    else:
        return "High Impact", "Conscious Consumer 🌍", "Consider sustainable alternatives.", MASCOT_SAD

def show_mascot(path, width=180):
    if os.path.exists(path):
        st.image(path, width=width)
    else:
        st.error(f"Mascot file missing: {path}")

st.sidebar.markdown("## 🌱 GreenBasket")
show_mascot(MASCOT_DEFAULT, width=140)

page = st.sidebar.radio(
    "Navigate",
    ["Home", "Add Purchase", "Dashboard", "Eco Tips"]
)

if page == "Home":
    st.markdown('<div class="big-title">GreenBasket</div>', unsafe_allow_html=True)
    show_mascot(MASCOT_DEFAULT)
    st.write(
        "GreenBasket helps users track purchases, calculate CO₂ impact automatically, "
        "and build eco-friendly shopping habits."
    )

elif page == "Add Purchase":
    st.subheader("🛒 Add a Purchase")

    product_name = st.text_input("Product Name")
    brand = st.text_input("Brand")
    product_type = st.selectbox(
        "Product Category",
        ["Electronics", "Clothing", "Food", "Household", "Transport"]
    )
    price = st.number_input("Price", min_value=0.0, step=1.0)

    if st.button("Add Purchase"):
        if product_name and brand and price > 0:
            impact, badge, suggestion, mascot = calculate_impact(price, product_type)

            purchases.append({
                "product_name": product_name,
                "brand": brand,
                "category": product_type,
                "price": price,
                "impact": impact,
                "co2": round(price * PRODUCT_IMPACT[product_type], 2),
                "badge": badge
            })

            save_data()
            st.success("Purchase added successfully!")
            show_mascot(mascot)
            st.info(suggestion)
        else:
            st.error("Please fill all required fields.")

elif page == "Dashboard":
    st.subheader("📊 Dashboard")
    show_mascot(MASCOT_DEFAULT)

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
    show_mascot(MASCOT_HAPPY)

    tips = [
        "Buy local products to reduce transport emissions.",
        "Choose reusable products instead of single-use plastics.",
        "Repair items instead of replacing them.",
        "Second-hand shopping reduces carbon footprint significantly."
    ]

    for tip in tips:
        st.markdown(f"- {tip}")
