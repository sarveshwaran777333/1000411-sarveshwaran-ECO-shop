import streamlit as st
import json
import os
from datetime import datetime, date

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="ShopImpact – Conscious Shopping Dashboard",
    layout="centered"
)

DATA_FILE = "purchases.json"
MASCOT_PATH = os.path.join("image", "Lion.png")

# ---------------- DATA SETUP ----------------
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump([], f)

def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ---------------- LOGIC ----------------
def calculate_impact(price):
    if price < 500:
        return "Low Impact", 1, "Eco Saver"
    elif price < 2000:
        return "Medium Impact", 2, "Low Impact Shopper"
    else:
        return "High Impact", 5, "Conscious Consumer"

eco_tips = [
    "Buying local reduces transport emissions.",
    "Second-hand shopping saves resources.",
    "Reusable items reduce plastic waste.",
    "Energy-efficient products save CO₂ long-term."
]

suggestions = {
    "Low Impact": "Excellent choice! Keep going.",
    "Medium Impact": "Consider greener alternatives.",
    "High Impact": "Try sustainable or second-hand options."
}

# ---------------- HEADER ----------------
col1, col2 = st.columns([3,1])
with col1:
    st.title("🌿 ShopImpact")
    st.caption("Conscious Shopping Dashboard")
with col2:
    if os.path.exists(MASCOT_PATH):
        st.image(MASCOT_PATH, width=130)

# ---------------- NAVIGATION ----------------
page = st.radio(
    "Navigate",
    ["Home", "Add Purchase", "Dashboard", "Eco Tips"],
    horizontal=True
)

# ---------------- HOME ----------------
if page == "Home":
    st.subheader("Welcome 👋")
    st.write(
        "ShopImpact helps you track purchases, understand CO₂ impact, "
        "and build sustainable habits in a fun, guilt-free way."
    )
    st.success("Start by adding your first purchase!")

# ---------------- ADD PURCHASE ----------------
elif page == "Add Purchase":
    st.subheader("🛒 Add a Purchase")

    product = st.text_input("Product Name")
    brand = st.text_input("Brand Name")
    price = st.number_input("Price", min_value=0.0, step=1.0)

    currency = st.selectbox(
        "Currency Used",
        ["₹ INR", "$ USD", "€ EUR", "£ GBP", "¥ JPY"]
    )

    purchase_date = st.date_input("Purchase Date", date.today())

    if st.button("Add Purchase"):
        if product == "" or brand == "" or price == 0:
            st.error("Please fill all required fields.")
        else:
            impact, multiplier, badge = calculate_impact(price)
            co2 = price * multiplier

            data = load_data()
            data.append({
                "product": product,
                "brand": brand,
                "price": price,
                "currency": currency.split()[0],
                "impact": impact,
                "co2": round(co2, 2),
                "badge": badge,
                "date": str(purchase_date),
                "suggestion": suggestions[impact]
            })
            save_data(data)

            st.success("Purchase saved successfully!")
            st.info("Eco Tip: " + eco_tips[len(data) % len(eco_tips)])

    st.subheader("📋 Purchase History")
    data = load_data()
    if data:
        st.table(data)
    else:
        st.info("No purchases recorded yet.")

# ---------------- DASHBOARD ----------------
elif page == "Dashboard":
    st.subheader("📊 Monthly Summary")

    data = load_data()
    if not data:
        st.info("No data to display yet.")
    else:
        total_spend = sum(p["price"] for p in data)
        total_co2 = sum(p["co2"] for p in data)
        eco_count = sum(1 for p in data if p["impact"] == "Low Impact")

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Spend", f"{total_spend:.2f}")
        col2.metric("Total CO₂ (kg)", f"{total_co2:.2f}")
        col3.metric("Eco Purchases", eco_count)

# ---------------- ECO TIPS ----------------
elif page == "Eco Tips":
    st.subheader("💡 Eco Tips & Suggestions")

    data = load_data()
    if not data:
        st.info("Add purchases to get personalized tips.")
    else:
        for p in data:
            st.write(f"• **{p['product']}** → {p['suggestion']}")

# ---------------- FOOTER ----------------
st.markdown("---")
st.caption("Built with Python & Streamlit • Social Good Project")
