import streamlit as st
import json
import os
import pandas as pd

st.set_page_config(page_title="GreenBasket", layout="wide")

DATA_FILE = "data.json"

MASCOT_DEFAULT = "image/Lion.png"
MASCOT_LOW = "image/Lion_Happy.png"
MASCOT_HIGH = "image/Lion_Sad.png"

LOW_CO2_LIMIT = 100  # threshold

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

def get_mascot(total_co2):
    if total_co2 == 0:
        return MASCOT_DEFAULT
    elif total_co2 <= LOW_CO2_LIMIT:
        return MASCOT_LOW
    else:
        return MASCOT_HIGH

def show_mascot(path, width=180):
    if os.path.exists(path):
        st.image(path, width=width)

st.sidebar.markdown("## 🌱 GreenBasket")
show_mascot(MASCOT_DEFAULT, 140)

page = st.sidebar.radio(
    "Navigate",
    ["Home", "Add Purchase", "Dashboard", "Eco Tips"]
)

if page == "Home":
    st.title("GreenBasket")
    show_mascot(MASCOT_DEFAULT)
    st.write("Track your purchases and understand your carbon footprint.")

elif page == "Add Purchase":
    st.subheader("🛒 Add a Purchase")

    product_name = st.text_input("Product Name")
    brand = st.text_input("Brand")
    category = st.selectbox(
        "Product Category",
        ["Electronics", "Clothing", "Food", "Household", "Transport"]
    )
    price = st.number_input("Price", min_value=0.0, step=1.0)

    if st.button("Add Purchase"):
        if product_name and brand and price > 0:
            co2 = round(price * PRODUCT_IMPACT[category], 2)

            purchases.append({
                "product_name": product_name,
                "brand": brand,
                "category": category,
                "price": price,
                "co2": co2
            })

            save_data()
            st.success("Purchase added successfully!")

            show_mascot(get_mascot(co2))
        else:
            st.error("Please fill all fields.")

elif page == "Dashboard":
    st.subheader("📊 Dashboard")

    if not purchases:
        show_mascot(MASCOT_DEFAULT)
        st.info("No purchases recorded yet.")
    else:
        df = pd.DataFrame(purchases)
        total_co2 = df["co2"].sum()

        show_mascot(get_mascot(total_co2))

        col1, col2 = st.columns(2)
        col1.metric("Total Spend", f"{df['price'].sum():.2f}")
        col2.metric("Total CO₂ Impact (kg)", f"{total_co2:.2f}")

        st.dataframe(df, use_container_width=True)

elif page == "Eco Tips":
    st.subheader("🌍 Eco Tips")
    show_mascot(MASCOT_LOW)
    st.markdown("- Buy local products")
    st.markdown("- Choose reusable items")
    st.markdown("- Repair instead of replace")
