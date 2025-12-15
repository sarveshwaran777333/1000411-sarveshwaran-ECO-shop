import streamlit as st
import json
import os
from datetime import date

st.set_page_config(
    page_title="GreenBasket",
    layout="wide"
)

DATA_FILE = "data.json"

# ----------------- JSON STORAGE -----------------
def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

purchases = load_data()

# ----------------- CO2 LOGIC -----------------
def calculate_impact(price):
    if price >= 30000:
        return "High Impact", price * 5, "Conscious Consumer", "Try sustainable or second-hand options."
    elif price >= 10000:
        return "Medium Impact", price * 2, "Aware Shopper", "Look for eco-certified brands."
    else:
        return "Low Impact", price * 1, "Eco Saver", "Great choice! Keep it up."

# ----------------- SIDEBAR -----------------
st.sidebar.title("🌱 GreenBasket")
page = st.sidebar.radio(
    "Navigate",
    ["Home", "Add Purchase", "Dashboard", "Eco Tips"]
)

# Mascot logic
total_co2 = sum(p["co2"] for p in purchases) if purchases else 0
mascot = "image/lion_happy.gif" if total_co2 < 500 else "image/lion_sad.gif"

st.sidebar.image(mascot, width=180)
st.sidebar.caption("Your Eco Buddy")

# ----------------- HOME -----------------
if page == "Home":
    st.title("🌿 GreenBasket – Conscious Shopping Dashboard")
    st.write("""
    Track your purchases, understand environmental impact,  
    and build better shopping habits 🌍
    """)

# ----------------- ADD PURCHASE -----------------
elif page == "Add Purchase":
    st.title("➕ Add Purchase")

    col1, col2 = st.columns(2)

    with col1:
        product = st.text_input("Product Name")
        brand = st.text_input("Brand")
        price = st.number_input("Price", min_value=0.0, step=1.0)
        currency = st.selectbox("Currency Used", ["₹ INR", "$ USD", "€ EUR", "£ GBP", "¥ JPY"])

    with col2:
        purchase_date = st.date_input("Purchase Date", date.today())

    if st.button("Add Purchase"):
        if product and brand and price > 0:
            impact, co2, badge, suggestion = calculate_impact(price)

            entry = {
                "product": product,
                "brand": brand,
                "price": price,
                "currency": currency,
                "impact": impact,
                "co2": round(co2, 2),
                "badge": badge,
                "date": str(purchase_date),
                "suggestion": suggestion
            }

            purchases.append(entry)
            save_data(purchases)
            st.success("Purchase added successfully!")

        else:
            st.error("Please fill all fields correctly.")

# ----------------- DASHBOARD -----------------
elif page == "Dashboard":
    st.title("📊 Purchase History")

    if purchases:
        st.dataframe(
            purchases,
            use_container_width=True,
            height=400
        )

        total_spend = sum(p["price"] for p in purchases)
        total_eco = sum(1 for p in purchases if p["impact"] == "Low Impact")

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Spend", f"{total_spend:.2f}")
        col2.metric("Total CO₂", f"{total_co2:.2f} kg")
        col3.metric("Eco Purchases", total_eco)

    else:
        st.info("No purchases recorded yet.")

# ----------------- ECO TIPS -----------------
elif page == "Eco Tips":
    st.title("💡 Eco Tips")

    tips = [
        "Choose reusable products over disposable ones.",
        "Buy local to reduce transport emissions.",
        "Repair instead of replacing electronics.",
        "Support eco-certified brands."
    ]

    for tip in tips:
        st.success(tip)
