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
        return "Low Impact", "Eco Saver 🌱", "Great eco-friendly choice!"
    elif co2 < 150:
        return "Medium Impact", "Low Impact Shopper 🌿", "Try greener options next time."
    else:
        return "High Impact", "Conscious Consumer 🌍", "Consider sustainable alternatives."

def show_mascot(width=160):
    if os.path.exists(MASCOT_PATH):
        st.markdown(
            f"""
            <div class="mascot" style="text-align:center; margin-bottom: 20px;">
                <img src="{MASCOT_PATH}" width="{width}">
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.warning("Mascot image not found")

# Sidebar
st.sidebar.markdown("## 🌱 GreenBasket")
show_mascot(width=120)  # smaller version in sidebar

page = st.sidebar.radio(
    "Navigate",
    ["Home", "Add Purchase", "Dashboard", "Eco Tips"]
)

# Pages
if page == "Home":
    st.markdown('<div class="big-title">GreenBasket</div>', unsafe_allow_html=True)
    show_mascot()
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
    currency = st.selectbox(
        "Currency Used",
        ["₹ INR", "$ USD", "€ EUR", "£ GBP", "¥ JPY"]
    )
    purchase_date = st.date_input("Purchase Date")
    purchase_time = st.time_input("Purchase Time")

    if st.button("Add Purchase"):
        if product_name and brand and price > 0:
            impact, badge, suggestion = calculate_impact(price, product_type)
            entry = {
                "product_name": product_name,
                "brand": brand,
                "category": product_type,
                "price": price,
                "currency": currency.split()[0],
                "impact": impact,
                "co2": round(price * PRODUCT_IMPACT[product_type], 2),
                "badge": badge,
                "date": f"{purchase_date} {purchase_time}",
                "suggestion": suggestion
            }
            purchases.append(entry)
            save_data()
            st.success("Purchase added successfully!")
        else:
            st.error("Please fill all required fields.")

elif page == "Dashboard":
    st.subheader("📊 Dashboard")
    show_mascot()
    if not purchases:
        st.info("No purchases recorded yet.")
    else:
        df = pd.DataFrame(purchases)
        col1, col2 = st.columns(2)
        col1.metric("Total Spend", f"{df['price'].sum():.2f}")
        col2.metric("Total CO₂ Impact (kg)", f"{df['co2'].sum():.2f}")

        st.subheader("📋 Purchase History")
        st.dataframe(
            df.rename(columns={
                "product_name": "Product Name",
                "brand": "Brand",
                "category": "Category",
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
        "Choose reusable products instead of single-use plastics.",
        "Repair items instead of replacing them.",
        "Second-hand shopping reduces carbon footprint significantly."
    ]
    for tip in tips:
        st.markdown(f"- {tip}")
