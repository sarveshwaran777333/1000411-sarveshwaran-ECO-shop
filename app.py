import streamlit as st
import pandas as pd
from datetime import datetime
import random

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="GreenBasket – ShopImpact", layout="wide")

# ---------------- SESSION STATE ----------------
if "purchases" not in st.session_state:
    st.session_state.purchases = []

if "badges" not in st.session_state:
    st.session_state.badges = set()

# ---------------- DATA LOGIC ----------------
CO2_MULTIPLIER = {
    "Clothing": 1.5,
    "Electronics": 3.0,
    "Groceries": 0.8,
    "Furniture": 2.5,
    "Footwear": 1.8,
    "Second-hand": 0.4
}

GREEN_ALTERNATIVES = {
    "Clothing": ["Organic cotton brands", "Second-hand stores"],
    "Electronics": ["Energy Star devices", "Refurbished electronics"],
    "Groceries": ["Local produce", "Package-free stores"],
    "Furniture": ["Bamboo furniture", "Recycled wood brands"],
    "Footwear": ["Vegan leather brands"],
    "Second-hand": ["Reuse centers", "Thrift stores"]
}

ECO_TIPS = [
    "Buying second-hand reduces carbon footprint 🌍",
    "Local products reduce transport emissions 🚲",
    "Repairing items saves resources ♻️",
    "Durable products reduce waste 🌱"
]

# ---------------- FUNCTIONS ----------------
def calculate_co2(price, product_type):
    return round(price * CO2_MULTIPLIER.get(product_type, 1), 2)

def award_badges(total_co2):
    if total_co2 < 100:
        st.session_state.badges.add("🌟 Eco Saver")
    if total_co2 < 200:
        st.session_state.badges.add("🍃 Low Impact Shopper")

def eco_graphic():
    st.markdown(
        """
        <div style="font-size:70px; text-align:center;">
            🍃🌍🍃
        </div>
        <p style="text-align:center; font-size:18px;">
            Eco-friendly choice detected!
        </p>
        """,
        unsafe_allow_html=True
    )

# ---------------- UI ----------------
st.title("🌱 GreenBasket – ShopImpact Dashboard")
st.write("Track your shopping habits and see your environmental impact in real time.")

# ---------------- INPUT SECTION ----------------
st.subheader("🛒 Log a Purchase")

col1, col2, col3 = st.columns(3)
with col1:
    product_type = st.selectbox("Product Type", list(CO2_MULTIPLIER.keys()))
with col2:
    brand = st.text_input("Brand")
with col3:
    price = st.number_input("Price (₹)", min_value=1.0)

if st.button("Add Purchase"):
    co2 = calculate_co2(price, product_type)
    st.session_state.purchases.append({
        "date": datetime.now(),
        "product": product_type,
        "brand": brand,
        "price": price,
        "co2": co2
    })
    st.success(f"Purchase added! Estimated CO₂ impact: {co2}")
    st.info(random.choice(ECO_TIPS))

# ---------------- DASHBOARD ----------------
if st.session_state.purchases:
    df = pd.DataFrame(st.session_state.purchases)
    df["month"] = df["date"].dt.to_period("M").astype(str)

    total_spend = df["price"].sum()
    total_co2 = df["co2"].sum()

    award_badges(total_co2)

    st.subheader("📊 Monthly Impact Dashboard")
    c1, c2 = st.columns(2)
    c1.metric("Total Spend (₹)", round(total_spend, 2))
    c2.metric("Estimated CO₂ Impact", round(total_co2, 2))

    monthly = df.groupby("month")[["price", "co2"]].sum()
    st.bar_chart(monthly)

    # ---------------- BADGES ----------------
    st.subheader("🏅 Your Eco Badges")
    for badge in st.session_state.badges:
        st.success(badge)

    if st.session_state.badges:
        eco_graphic()

    # ---------------- SUGGESTIONS ----------------
    st.subheader("🌿 Greener Alternatives")
    for alt in GREEN_ALTERNATIVES.get(product_type, []):
        st.write("•", alt)

else:
    st.info("No purchases logged yet. Start by adding one above!")

st.markdown("---")
st.caption("GreenBasket © ShopImpact | Designed for Social Good")
