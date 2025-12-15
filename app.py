import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

st.set_page_config(page_title="GreenBasket", layout="wide")

DATA_FILE = "data.json"
MASCOT_PATH = "image/lion.png"

st.markdown("""
<style>
@keyframes float {
  0% { transform: translateY(0px); }
  50% { transform: translateY(-10px); }
  100% { transform: translateY(0px); }
}
.mascot {
  animation: float 3s ease-in-out infinite;
  text-align: center;
}
.big-title {
  font-size: 36px;
  font-weight: 700;
  color: #2e7d32;
}
.section-box {
  background: #ffffff;
  padding: 20px;
  border-radius: 12px;
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
        return "Low Impact", "Eco Saver 🌱", "Great choice! Very eco-friendly."
    elif co2 < 150:
        return "Medium Impact", "Low Impact Shopper 🌿", "Try greener alternatives next time."
    else:
        return "High Impact", "Conscious Consumer 🌍", "Consider sustainable or second-hand options."

st.sidebar.markdown("## 🌱 GreenBasket")

if os.path.exists(MASCOT_PATH):
    st.sidebar.markdown(
        f"""
        <div class="mascot">
            <img src="{MASCOT_PATH}" width="160">
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.sidebar.warning("Mascot image not found")

page = st.sidebar.radio(
    "Navigate",
    ["Home", "Add Purchase", "Dashboard", "Eco Tips"]
)

if page == "Home":
    st.markdown('<div class="big-title">GreenBasket</div>', unsafe_allow_html=True)
    st.write(
        "GreenBasket helps you track purchases, understand their CO₂ impact, "
        "and encourages eco-friendly shopping habits in a fun, visual way."
    )

elif page == "Add Purchase":
    st.subheader("🛒 Add a Purchase")

    with st.container():
        product = st.selectbox(
            "Product Type",
            ["Electronics", "Clothing", "Food", "Household", "Transport"]
        )
        brand = st.text_input("Brand")
        price = st.number_input("Price", min_value=0.0, step=1.0)

        currency = st.selectbox(
            "Currency",
            ["₹ INR", "$ USD", "€ EUR", "£ GBP", "¥ JPY"]
        )

        date = st.date_input("Purchase Date")
        time = st.time_input("Purchase Time")

        if st.button("Add Purchase"):
            if brand and price > 0:
                impact, badge, suggestion = calculate_impact(price, product)
                entry = {
                    "product": product,
                    "brand": brand,
                    "price": price,
                    "currency": currency.split()[0],
                    "impact": impact,
                    "co2": round(price * PRODUCT_IMPACT[product], 2),
                    "badge": badge,
                    "date": f"{date} {time}",
                    "suggestion": suggestion
                }
                purchases.append(entry)
                save_data()
                st.success("Purchase added successfully!")
            else:
                st.error("Please fill all required fields.")

elif page == "Dashboard":
    st.subheader("📊 Dashboard")

    if not purchases:
        st.info("No purchases yet.")
    else:
        df = pd.DataFrame(purchases)

        total_spend = df["price"].sum()
        total_co2 = df["co2"].sum()

        col1, col2 = st.columns(2)
        col1.metric("Total Spend", f"{total_spend:.2f}")
        col2.metric("Total CO₂ Impact (kg)", f"{total_co2:.2f}")

        st.subheader("📋 Purchase History")

        st.dataframe(
            df.rename(columns={
                "product": "Product",
                "brand": "Brand",
                "price": "Price",
                "currency": "Currency",
                "impact": "Impact",
                "co2": "CO₂ (kg)",
                "badge": "Badge",
                "date": "Date",
                "suggestion": "Suggestion"
            }),
            use_container_width=True
        )

elif page == "Eco Tips":
    st.subheader("🌍 Eco Tips")

    tips = [
        "Buy local products to reduce transport emissions.",
        "Choose reusable items instead of single-use plastics.",
        "Repair before replacing electronics.",
        "Second-hand shopping significantly reduces carbon footprint."
    ]

    for tip in tips:
        st.markdown(f"- {tip}")
