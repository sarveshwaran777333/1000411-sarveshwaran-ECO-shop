import streamlit as st
import json
import os
from datetime import date

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="GreenBasket – Conscious Shopping Dashboard",
    layout="centered"
)

DATA_FILE = "purchases.json"
MASCOT_PATH = os.path.join("image", "Lion.png")

# ---------------- DATA FILE ----------------
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

suggestions = {
    "Low Impact": "Excellent choice! Keep it up.",
    "Medium Impact": "Consider greener alternatives.",
    "High Impact": "Try sustainable or second-hand options."
}

eco_tips = [
    "Buying local products reduces transport emissions.",
    "Second-hand shopping saves resources.",
    "Reusable items help cut plastic waste.",
    "Energy-efficient products save CO₂."
]

# ---------------- ANIMATED MASCOT ----------------
st.markdown(
    """
    <style>
    .mascot {
        position: fixed;
        bottom: 25px;
        right: 25px;
        animation: float 3s ease-in-out infinite;
        z-index: 999;
    }

    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-15px); }
        100% { transform: translateY(0px); }
    }
    </style>
    """,
    unsafe_allow_html=True
)

if os.path.exists(MASCOT_PATH):
    with open(MASCOT_PATH, "rb") as img:
        import base64
        encoded = base64.b64encode(img.read()).decode()

    st.markdown(
        f"""
        <div class="mascot">
            <img src="data:image/png;base64,{encoded}" width="120">
        </div>
        """,
        unsafe_allow_html=True
    )

# ---------------- HEADER ----------------
st.title("🌱 GreenBasket")
st.caption("Conscious Shopping Dashboard")

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
        "GreenBasket helps you track purchases, understand their environmental impact, "
        "and build sustainable shopping habits in a fun and friendly way."
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

            st.success("Purchase added successfully!")
            st.info("Eco Tip: " + eco_tips[len(data) % len(eco_tips)])

    st.subheader("📋 Purchase History")
    data = load_data()
    if data:
        st.dataframe(data, use_container_width=True)
    else:
        st.info("No purchases recorded yet.")

# ---------------- DASHBOARD ----------------
elif page == "Dashboard":
    st.subheader("📊 Monthly Summary")

    data = load_data()
    if not data:
        st.info("No data available yet.")
    else:
        total_spend = sum(p["price"] for p in data)
        total_co2 = sum(p["co2"] for p in data)
        eco_count = sum(1 for p in data if p["impact"] == "Low Impact")

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Spend", f"{total_spend:.2f}")
        col2.metric("Total CO₂ (kg)", f"{total_co2:.2f}")
        col3.metric("Eco-Friendly Purchases", eco_count)

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
st.caption("GreenBasket • Built with Python & Streamlit • Social Good Project")
