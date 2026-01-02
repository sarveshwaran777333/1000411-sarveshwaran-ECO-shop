import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime
import base64

# --- CONFIG ---
st.set_page_config(page_title="GreenBasket", layout="wide")

USER_FILE = "users.json"
PRODUCT_FILE = "products.json"

# --- GLOBAL CURRENCY LIST ---
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
    "GTQ - Guatemalan Quetzal (Q)", "GYD - Guyanaese Dollar ($)", "HKD - Hong Kong Dollar ($)", "HNL - Honduran Lempira (L)",
    "HRK - Croatian Kuna (kn)", "HTG - Haitian Gourde (G)", "HUF - Hungarian Forint (Ft)", "IDR - Indonesian Rupiah (Rp)",
    "ILS - Israeli New Shekel (₪)", "IMP - Isle of Man Pound (£)", "INR - Indian Rupee (₹)", "IQD - Iraqi Dinar (ع.د)",
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

# --- DATA HANDLING ---
def safe_load_json(file_path, default_data):
    if not os.path.exists(file_path):
        with open(file_path, "w") as f: json.dump(default_data, f)
        return default_data
    try:
        with open(file_path, "r") as f: return json.load(f)
    except: return default_data

if "users" not in st.session_state:
    st.session_state.users = safe_load_json(USER_FILE, {})

users = st.session_state.users
PRODUCTS = safe_load_json(PRODUCT_FILE, {})

def save_users():
    with open(USER_FILE, "w") as f:
        json.dump(st.session_state.users, f, indent=4)

# --- AUDIO HELPER ---
def play_sound(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            md = f"""<audio autoplay="true" style="display:none;"><source src="data:audio/wav;base64,{b64}" type="audio/wav"></audio>"""
            st.markdown(md, unsafe_allow_html=True)

# --- UI HELPERS ---
def get_text_color(bg):
    bg = bg.lstrip("#")
    r, g, b = int(bg[0:2], 16), int(bg[2:4], 16), int(bg[4:6], 16)
    brightness = (r * 299 + g * 587 + b * 114) / 1000
    return "#000000" if brightness > 140 else "#ffffff"

def set_background(bg_color):
    text_color = get_text_color(bg_color)
    st.markdown(f"""<style>.stApp {{ background-color: {bg_color}; color: {text_color}; }}</style>""", unsafe_allow_html=True)

# --- SESSION STATE ---
if "bg_color" not in st.session_state: st.session_state.bg_color = "#1b5e20"
if "logged_in" not in st.session_state: st.session_state.logged_in = False

set_background(st.session_state.bg_color)

# --- APP PAGES ---
if not st.session_state.logged_in:
    st.title("🌱 GreenBasket")
    t1, t2 = st.tabs(["Login", "Sign Up"])
    with t1:
        u = st.text_input("Username", key="login_user")
        p = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            if u in users and users[u]["password"] == p:
                st.session_state.logged_in, st.session_state.user = True, u
                st.rerun()
            else: st.error("Invalid credentials")
    with t2:
        nu = st.text_input("New User", key="reg_user")
        np = st.text_input("New Password", type="password", key="reg_pass")
        if st.button("Register"):
            if nu in users: st.error("Username already exists")
            else:
                users[nu] = {"password": np, "purchases": []}
                save_users(); st.success("Account created! Please Login.")

else:
    user = st.session_state.user
    profile = users[user]
    
    # --- MASCOT LOGIC ---
    path = "image/"
    LION_NORM = f"{path}Lion.png"
    LION_HAP  = f"{path}Lion_Happy.png"
    LION_SAD  = f"{path}Lion_Sad.png"

    # Navigation Setup
    st.sidebar.title(f"Hello, {user}")
    page = st.sidebar.radio("Navigate", ["Home", "Add Purchase", "Dashboard", "Eco Game", "Settings"])
    
    # Define Dynamic Mascot State
    current_lion = LION_NORM
    lion_msg = "Roar! Let's save the earth together."

    # Calculation for Mascot Comment
    total_impact = sum(p["impact"] for p in profile["purchases"]) if profile["purchases"] else 0

    if page == "Home":
        lion_msg = f"Hey {user}, ready to track some green habits?"
    elif page == "Add Purchase":
        lion_msg = "Adding new gear? Let's check how eco-friendly it is!"
    elif page == "Dashboard":
        if total_impact > 100000:
            current_lion = LION_SAD
            lion_msg = f"Oh no! Our total carbon impact is {total_impact:,.0f}. We need to be more careful!"
        elif total_impact > 0:
            current_lion = LION_HAP
            lion_msg = "Your green history looks amazing! Keep it up!"
        else:
            current_lion = LION_NORM
            lion_msg = "Nothing to show yet. Let's add a purchase!"
    elif page == "Eco Game":
        current_lion = LION_HAP
        lion_msg = "Time to run! Ready to set a high score?"

    # Display Mascot in Sidebar with "Comment" look
    with st.sidebar:
        st.image(current_lion, width=150)
        with st.chat_message("assistant", avatar=current_lion):
            st.write(lion_msg)
        st.markdown("---")

    # --- MAIN PAGES ---
    if page == "Home":
        st.title("Welcome to GreenBasket!")
        st.write("Start tracking your eco-friendly choices today.")
        st.info("Tip: Look for the 'Eco-Friendly' brands to keep your Carbon Impact low!")

    elif page == "Add Purchase":
        st.header("Add Purchase")
        
        # CATEGORY SELECTION
        cat = st.selectbox("Category", list(PRODUCTS.keys()))
        
        # PRODUCT SELECTION (Corrected to map items)
        prod = st.selectbox("Product", PRODUCTS[cat]["items"])
        
        # BRAND SELECTION (Corrected to map brands)
        std_brands = PRODUCTS[cat]["brands"]["Standard"]
        eco_brands = PRODUCTS[cat]["brands"]["Eco-Friendly"]
        brand = st.selectbox("Brand Name", std_brands + eco_brands)
        
        currency = st.selectbox("Select Currency", ALL_CURRENCIES, index=62) # Default to INR
        price = st.number_input(f"Price", min_value=0.0)
        
        if st.button("Add to History"):
            # Check if brand is eco to decide impact
            is_eco = brand in eco_brands or cat == "Second-hand"
            impact_val = price * (0.4 if is_eco else 1.2)
            
            profile["purchases"].append({
                "date": datetime.now().strftime("%Y-%m-%d"),
                "product": prod, 
                "brand": brand, 
                "currency": currency,
                "price": price, 
                "impact": impact_val
            })
            save_users()
            st.success(f"Added {brand} {prod} to your history!")
            play_sound(f"{path}coin.wav")
            if is_eco:
                st.balloons()
                st.toast("The Lion is proud of your choice!", icon="🦁")

    elif page == "Dashboard":
        st.header("Your Shopping Insights")
        if profile["purchases"]:
            df = pd.DataFrame(profile["purchases"])
            st.dataframe(df, use_container_width=True)
            st.subheader("Carbon Impact Over Time")
            st.line_chart(df.set_index("date")["impact"])
        else: 
            st.info("No purchases recorded yet.")

    elif page == "Eco Game":
        st.header("Robo Runner Pro")
        try:
            with open("game.html", "r", encoding="utf-8") as f:
                game_html = f.read()
            st.components.v1.html(game_html, height=550)
        except FileNotFoundError:
            st.error("Missing game.html file.")

    elif page == "Settings":
        st.header("Customize App")
        st.session_state.bg_color = st.color_picker("Pick a color", st.session_state.bg_color)
        if st.button("Apply"): 
            st.rerun()

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()
