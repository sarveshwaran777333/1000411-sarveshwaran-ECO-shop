import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime
import base64
import random
import plotly.graph_objects as go

st.set_page_config(page_title="GreenBasket", layout="wide")

USER_FILE = "users.json"
PRODUCT_FILE = "products.json"

ALL_CURRENCIES = [
    "AED - UAE Dirham (د.إ)", "AFN - Afghan Afghani (؋)", "ALL - Albanian Lek (L)", "AMD - Armenian Dram (֏)",
    "ANG - NL Antillean Guilder (ƒ)", "AOA - Angolan Kwanza (Kz)", "ARS - Argentine Peso ($)", "AUD - Australian Dollar (A$)",
    "AWG - Aruban Florin (ƒ)", "AZN - Azerbaijani Manat (₼)", "BAM - Bosnia-Herzegovina Mark (KM)", "BBD - Barbadian Dollar ($)",
    "BDT - Bangladeshi Taka (৳)", "BGN - Bulgarian Lev (лв)", "BHD - Bahraini Dinar (.د.ب)", "BIF - Burundian Franc (FBu)",
    "BMD - Bermudian Dollar ($)", "BND - Brunei Dollar ($)", "BOB - Bolivian Boliviano (Bs.)", "BRL - Brazilian Real (R$)",
    "BSD - Bahamian Dollar ($)", "BTN - Bhutanese Ngultrum (Nu.)", "BWP - Botswanan Pula (P)", "BYN - Belarusian Ruble (Br)",
    "BZD - Belize Dollar ($)", "CAD - Canadian Dollar (C$)", "CDF - Congolese Franc (FC)", "CHF - Swiss Franc (CHf)",
    "CLP - Chilean Peso ($)", "CNY - Chinese Yuan (¥)", "COP - Colombian Peso ($)", "CRC - Costa Rican Colón (₡)",
    "CUP - Cuban Peso ($)", "CVE - Cape Verdean Escudo ($)", "CZK - Czech Koruna (Kč)", "DJF - Djiboutian Franc (Fdj)",
    "DKK - Danish Krone (kr)", "DOP - Dominican Peso ($)", "DZD - Algerian Dinar (د.ج)", "EGP - Egyptian Pound (E£)",
    "ERN - Eritrean Nakfa (Nfk)", "ETB - Ethiopian Birr (Br)", "EUR - Euro (€)", "FJD - Fijian Dollar ($)",
    "FKP - Falkland Islands Pound (£)", "GBP - British Pound (£)", "GEL - Georgian Lari (₾)", "GGP - Guernsey Pound (£)",
    "GHS - Ghanaian Cedi (₵)", "GIP - Gibraltar Pound (£)", "GMD - Gambian Dalasi (D)", "GNF - Guinean Franc (FG)",
    "GTQ - Guatemalan Apollon (Q)", "GYD - Guyanaese Dollar ($)", "HKD - Hong Kong Dollar ($)", "HNL - Honduran Lempira (L)",
    "HRK - Croatian Kuna (kn)", "HTG - Haitian Gourde (G)", "HUF - Hungarian Forint (Ft)", "IDR - Indonesian Rupiah (Rp)",
    "ILS - Israeli New Shkel (₪)", "IMP - Isle of Man Pound (£)", "INR - Indian Rupee (₹)", "IQD - Iraqi Dinar (ع.د)",
    "IRR - Iranian Rial (﷼)", "ISK - Icelandic Króna (kr)", "JEP - Jersey Pound (£)", "JMD - Jamaican Dollar ($)",
    "JOD - Jordanian Dinar (د.ا)", "JPY - Japanese Yen (¥)", "KES - Kenyan Shilling (KSh)", "KGS - Kyrgystani Som (с)",
    "KHR - Cambodian Riel (៛)", "KMF - Comorian Franc (CF)", "KPW - North Korean Won (₩)", "KRW - South Korean Won (₩)",
    "KWD - Kuwaiti Dinar (د.ك)", "KYD - Cayman Islands Dollar ($)", "KZT - Kazakhstani Tenge (₸)", "LAK - Laotian Kip (₭)",
    "LBP - Lebanese Pound (L£)", "LKR - Sri Lankan Rupee (Rs)", "LRD - Liberian Dollar ($)", "LSL - Lesotho Loti (L)",
    "LYD - Libyan Dinar (ل.د)", "MAD - Moroccan Dirham (د.م.)", "MDL - Moldovan Leu (L)", "MGA - Malagasy Ariary (Ar)",
    "MKD - Macedonian Denar (ден)", "MMK - Myanmar Kyat (K)", "MNT - Mongolian Tugrik (₮)", "MOP - Macanese Pataca (P)",
    "MRU - Mauritanian Ouguiya (UM)", "MUR - Mauritian Rupee (₨)", "MVR - Maldivian Rufiyaa (Rf)", "MWK - Malawian Kwacha (MK)",
    "MXN - Mexican Peso ($)", "MYR - Malaysian Ringgit (RM)", "MZN - Mozambican Metical (MT)", "NAD - Namibian Dollar ($)",
    "NGN - Nigerian Naira (₦)", "NIO - Nicaraguan Córdoba (C$)", "NOK - Norwegian Krone (kr)", "NPR - Nepalese Rupee (₨)",
    "NZD - New Zealand Dollar ($)", "OMR - Oman Rial (ر.ع.)", "PAB - Panamanian Balboa (B/.)", "PEN - Peruvian Sol (S/.)",
    "PGK - Papua New Guinean Kina (K)", "PHP - Philippine Peso (₱)", "PKR - Pakistani Rupee (₨)", "PLN - Polish Zloty (zł)",
    "PYG - Paraguayan Guarani (₲)", "QAR - Qatari Rial (ر.ق)", "RON - Romanian Leu (lei)", "RSD - Serbian Dinar (дин.)",
    "RUB - Russian Ruble (₽)", "RWF - Rwandan Franc (FRw)", "SAR - Saudi Riyal (ر.س)", "SBD - Solomon Islands Dollar ($)",
    "SCR - Seychellois Rupee (₨)", "SDG - Sudanese Pound (ج.س.)", "SEK - Swedish Krone (kr)", "SGD - Singapore Dollar ($)",
    "SHP - Saint Helena Pound (£)", "SLL - Sierra Leonean Leone (Le)", "SOS - Somali Shilling (Sh)", "SRD - Surinamese Dollar ($)",
    "SSP - South Sudanese Pound (£)", "STN - São Tomé & Príncipe Dobra (Db)", "SVC - Salvadoran Colón ($)", "SYP - Syrian Pound (£)",
    "SZL - Swazi Lilangeni (L)", "THB - Thai Baht (฿)", "TJS - Tajikistani Somoni (ЅМ)", "TMT - Turkmenistani Manat (T)",
    "TND - Tunisian Dinar (د.ت)", "TOP - Tongan Paʻanga (T$)", "TRY - Turkish Lira (₺)", "TTD - Trinidad & Tobago Dollar ($)",
    "TWD - New Taiwan Dollar (NT$)", "TZS - Tanzanian Shilling (TSh)", "UAH - Ukrainian Hryvnia (₴)", "UGX - Ugandan Shilling (USh)",
    "USD - US Dollar ($)", "UYU - Uruguay Peso ($)", "UZS - Uzbekistani Som (so'm)", "VES - Venezuelan Bolívar (Bs.S.)",
    "VND - Vietnamese Dong (₫)", "VUV - Vanuatu Vatu (VT)", "WST - Samoan Tala (WS$)", "XAF - Central African CFA Franc (FCFA)",
    "XCD - East Caribbean Dollar ($)", "XOF - West African CFA Franc (CFA)", "XPF - CFP Franc (₣)", "YER - Yemeni Rial (﷼)",
    "ZAR - South African Rand (R)", "ZMW - Zambian Kwacha (ZK)", "ZWL - Zimbabwean Dollar ($)"
]

ECO_TIPS = [
    "Choosing slower shipping reduces CO₂ emissions.", "Ground shipping emits less carbon than air delivery.",
    "Consolidating items into one order saves fuel.", "Buying local products reduces transport emissions.",
    "Lightweight products generate less shipping CO₂.", "Smaller packages lower delivery emissions.",
    "Minimal packaging reduces carbon footprint.", "Recyclable packaging cuts lifecycle emissions.",
    "Reusable packaging saves production energy.", "Avoiding express shipping lowers emissions.",
    "Fewer returns mean less transport pollution.", "Checking size guides helps prevent returns.",
    "Buying durable products avoids replacement emissions.", "High-quality items last longer and save CO₂.",
    "Refurbished products reduce manufacturing emissions.", "Second-hand purchases save embedded carbon.",
    "Repairable products extend useful life.", "Buying once is better than buying twice.",
    "Digital products avoid shipping emissions.", "Flat-pack designs reduce transport space.",
    "Local warehouses shorten delivery distance.", "Bulk orders reduce delivery trips.",
    "Subscription refills cut packaging waste.", "Compact product designs ship more efficiently.",
    "Avoiding impulse buys lowers total emissions.", "Mindful shopping reduces demand-related CO₂.",
    "Eco-certified brands track carbon impact.", "Transparent supply chains reduce hidden emissions.",
    "Renewable-powered warehouses cut CO₂ output.", "Electric delivery vehicles emit less carbon.",
    "Bike couriers reduce last-mile emissions.", "Pickup points lower failed delivery trips.",
    "Locker pickups save fuel and time.", "Daytime delivery improves route efficiency.",
    "Carbon-aware routing reduces fuel use.", "Reusable mailers cut repeat emissions.",
    "Paper padding beats plastic fillers.", "Plastic-free packaging lowers pollution.",
    "Returnable packaging supports reuse.", "Product size affects delivery emissions.",
    "Dense packing reduces transport trips.", "Sea freight emits less CO₂ than air freight.",
    "Cross-border shipping increases emissions.", "Regional sourcing lowers transport distance.",
    "Carbon-neutral shipping supports climate projects.", "Verified offsets ensure real impact.",
    "Visible CO₂ labels encourage greener choices.", "Comparing options empowers low-carbon decisions.",
    "Small checkout choices reduce emissions.", "Every purchase has a carbon footprint."
]

def safe_load_json(file_path, default_data):
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            json.dump(default_data, f)
        return default_data
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except:
        return default_data

def save_users():
    with open(USER_FILE, "w") as f:
        json.dump(st.session_state.users, f, indent=4)

def get_base64(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

def set_background(bg_color):
    st.markdown(f'<style>.stApp {{ background-color: {bg_color}; }}</style>', unsafe_allow_html=True)

if "users" not in st.session_state:
    st.session_state.users = safe_load_json(USER_FILE, {})
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "bg_color" not in st.session_state:
    st.session_state.bg_color = "#1b5e20"

users = st.session_state.users
PRODUCTS = safe_load_json(PRODUCT_FILE, {})
set_background(st.session_state.bg_color)

if not st.session_state.logged_in:
    st.title("🌱 GreenBasket")
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    with tab1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Login"):
            if u in users and users[u]["password"] == p:
                st.session_state.logged_in, st.session_state.user = True, u
                st.rerun()
    with tab2:
        nu = st.text_input("New Username")
        np = st.text_input("New Password", type="password")
        if st.button("Register"):
            if nu not in users:
                users[nu] = {"password": np, "purchases": []}
                save_users()
                st.success("Registered!")

else:
    username = st.session_state.user
    profile = users.get(username, {"purchases":[]})
    path = "image/"
    
    total_impact = sum(p["impact"] for p in profile["purchases"])
    if total_impact > 100000:
        current_lion = f"{path}Lion_Sad.png"
        lion_msg = "Oh no! Our impact is getting too high!"
    elif total_impact > 0:
        current_lion = f"{path}Lion_Happy.png"
        lion_msg = "Great job keeping it green!"
    else:
        current_lion = f"{path}Lion.png"
        lion_msg = "Ready to start your eco-journey?"

    st.sidebar.image(current_lion if os.path.exists(current_lion) else [], width=150)
    st.sidebar.write(f"**{lion_msg}**")
    page = st.sidebar.radio("Menu", ["Home", "Add Purchase", "Dashboard", "Eco Game", "Settings"])

    if page == "Home":
        st.title(f"Welcome, {username}!")
        eco_count = sum(1 for p in profile["purchases"] if p["impact"] < (p["price"] * 1.0))
        c1, c2 = st.columns(2)
        c1.metric("Eco Choices", eco_count)
        c2.metric("Total Carbon", f"{total_impact:,.0f}")
        st.subheader("🕒 Recent Activity")
        for p in profile["purchases"][-3:][::-1]:
            st.write(f"✅ {p['product']} ({p['brand']})")

    elif page == "Add Purchase":
        st.header("Log Purchase")
        cat = st.selectbox("Category", list(PRODUCTS.keys()))
        prod = st.selectbox("Product", PRODUCTS[cat]["items"])
        brand = st.selectbox("Brand", PRODUCTS[cat]["brands"]["Standard"] + PRODUCTS[cat]["brands"]["Eco-Friendly"])
        price = st.number_input("Price", min_value=0.0)
        if st.button("Add"):
            is_eco = brand in PRODUCTS[cat]["brands"]["Eco-Friendly"]
            impact = price * (0.4 if is_eco else 1.2)
            profile["purchases"].append({"product": prod, "brand": brand, "price": price, "impact": impact, "date": str(datetime.now())})
            save_users()
            st.rerun()

    elif page == "Eco Game":
        st.header("Robo Runner")
        robo_data = get_base64(f"{path}ROBO.png")
        if not robo_data:
            st.error("Missing 'image/ROBO.png'!")
        else:
            try:
                with open("game.html", "r", encoding="utf-8") as f:
                    game_code = f.read().replace("PUT_YOUR_BASE64_IMAGE_HERE", robo_data)
                    st.components.v1.html(game_code, height=550)
            except Exception as e:
                st.error(f"Error loading game: {e}")

    elif page == "Settings":
        st.session_state.bg_color = st.color_picker("Theme Color", st.session_state.bg_color)
        if st.button("Save"): st.rerun()

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()
