import streamlit as st
import streamlit.components.v1 as components
import json
import os
import pandas as pd
from datetime import datetime
import random

# ---------------- CONFIG ----------------
st.set_page_config(page_title="GreenBasket", layout="wide", page_icon="🌱")

USER_FILE = "users.json"
PRODUCT_FILE = "products.json"

TRANSPORT_FACTORS = {
    "✈️ Air Freight": 0.500,
    "🚛 Road": 0.105,
    "🚆 Rail": 0.028,
    "🚢 Sea Freight": 0.015
}

COUNTRY_DISTANCES = {
    "Local (Within Country)": 150,
    "India": 0,
    "Pakistan": 700,
    "Bangladesh": 500,
    "Sri Lanka": 900,
    "Nepal": 800,
    "Bhutan": 900,
    "China": 4500,
    "Japan": 6500,
    "South Korea": 5500,
    "North Korea": 5200,
    "Thailand": 3000,
    "Malaysia": 3500,
    "Singapore": 3600,
    "Indonesia": 4500,
    "Philippines": 5000,
    "Vietnam": 3200,
    "Cambodia": 3300,
    "Laos": 3200,
    "Myanmar": 1600,
    "Afghanistan": 1200,
    "Iran": 2500,
    "Iraq": 3200,
    "Israel": 4200,
    "Jordan": 4300,
    "Saudi Arabia": 4000,
    "UAE": 2600,
    "Qatar": 2700,
    "Kuwait": 2800,
    "Oman": 2800,
    "Turkey": 5000,
    "Kazakhstan": 4500,
    "Uzbekistan": 3000,
    "Turkmenistan": 2800,
    "Kyrgyzstan": 3800,
    "Tajikistan": 3200,
    "Mongolia": 5000,
    "UK": 6800,
    "Ireland": 7000,
    "Germany": 6500,
    "France": 6700,
    "Italy": 6000,
    "Spain": 7200,
    "Portugal": 7500,
    "Netherlands": 6600,
    "Belgium": 6600,
    "Switzerland": 6400,
    "Austria": 6200,
    "Poland": 6300,
    "Czech Republic": 6200,
    "Slovakia": 6100,
    "Hungary": 6000,
    "Romania": 5600,
    "Bulgaria": 5500,
    "Greece": 5200,
    "Sweden": 7200,
    "Norway": 7400,
    "Finland": 7600,
    "Denmark": 7000,
    "Russia": 5000,
    "Ukraine": 5500,
    "Belarus": 6000,
    "Lithuania": 6500,
    "Latvia": 6600,
    "Estonia": 6800,
    "Serbia": 5800,
    "Croatia": 5900,
    "Slovenia": 6000,
    "Bosnia and Herzegovina": 5900,
    "North Macedonia": 5800,
    "Albania": 5700,
    "Montenegro": 5800,
    "Iceland": 9000,
    "Egypt": 4500,
    "South Africa": 8000,
    "Nigeria": 7000,
    "Kenya": 5000,
    "Ethiopia": 4800,
    "Somalia": 4000,
    "Tanzania": 5500,
    "Uganda": 5200,
    "Rwanda": 5400,
    "Burundi": 5500,
    "Ghana": 7200,
    "Senegal": 7800,
    "Morocco": 7200,
    "Algeria": 6500,
    "Tunisia": 6200,
    "Libya": 6000,
    "Sudan": 4500,
    "South Sudan": 4800,
    "Zambia": 6500,
    "Zimbabwe": 6700,
    "Botswana": 7200,
    "Namibia": 7500,
    "Angola": 7500,
    "Mozambique": 6500,
    "Madagascar": 6000,
    "USA": 13000,
    "Canada": 13500,
    "Mexico": 14000,
    "Brazil": 14500,
    "Argentina": 15000,
    "Chile": 16000,
    "Peru": 15500,
    "Colombia": 14500,
    "Venezuela": 14500,
    "Bolivia": 15500,
    "Paraguay": 15000,
    "Uruguay": 15500,
    "Ecuador": 15000,
    "Panama": 14500,
    "Costa Rica": 14000,
    "Cuba": 13500,
    "Jamaica": 13800,
    "Dominican Republic": 13800,
    "Haiti": 13800,
    "Australia": 10500,
    "New Zealand": 12000,
    "Papua New Guinea": 5500,
    "Fiji": 9000,
    "Solomon Islands": 7000,
    "Samoa": 9500,
    "Tonga": 9700,
    "Vanuatu": 8500
}

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
    "ERN - Eritrea Nakfa (Nfk)", "ETB - Ethiopian Birr (Br)", "EUR - Euro (€)", "FJD - Fijian Dollar ($)",
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

# ---------------- HELPERS ----------------
def safe_load_json(file_path, default_data):
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(default_data, f, indent=4)
        return default_data
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if data else default_data
    except Exception:
        return default_data

def save_users():
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.users, f, indent=4)

def set_background(color):
    st.markdown(f"""
        <style>
        .stApp {{ background-color: {color}; }}
        .stMarkdown, h1, h2, h3, p, .stMetric, span, label, div {{ color: white !important; }}
        </style>
    """, unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
if "users" not in st.session_state:
    st.session_state.users = safe_load_json(USER_FILE, {})
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "bg_color" not in st.session_state:
    st.session_state.bg_color = "#1b5e20"

set_background(st.session_state.bg_color)
PRODUCTS = safe_load_json(PRODUCT_FILE, {})

# ---------------- AUTH ----------------
if not st.session_state.logged_in:
    st.title("🌱 GreenBasket")
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    with tab1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Login"):
            if u in st.session_state.users and st.session_state.users[u]["password"] == p:
                st.session_state.logged_in = True
                st.session_state.user = u
                st.rerun()
            else: st.error("Invalid credentials")
    with tab2:
        nu = st.text_input("New Username")
        np = st.text_input("New Password", type="password")
        if st.button("Register"):
            if nu and nu not in st.session_state.users:
                st.session_state.users[nu] = {"password": np, "purchases": []}
                save_users()
                st.success("Account created!")

# ---------------- MAIN APP ----------------
else:
    user = st.session_state.user
    profile = st.session_state.users[user]

    # ----- MASCOT LOGIC -----
    total_impact = sum(p.get("impact", 0) for p in profile.get("purchases", []))
    if not profile.get("purchases"):
        lion_img = "image/Lion.png"
    elif total_impact > 800:
        lion_img = "image/Lion_Sad.png"
    else:
        lion_img = "image/Lion_Happy.png"

    if os.path.exists(lion_img):
        st.sidebar.image(lion_img, width=150)
    else:
        st.sidebar.warning("🦁 Mascot Image Missing")

    page = st.sidebar.radio("Menu", ["Home", "Add Purchase", "Dashboard", "Eco Game", "Settings"])

    # ---------- HOME ----------
    if page == "Home":
        st.title(f"Welcome, {user} 👋")
        st.info(f"💡 {random.choice(ECO_TIPS)}")
        clovers = sum(p.get("clovers_earned", 0) for p in profile.get("purchases", []))
        st.metric("Total Clovers", f"🍀 {clovers}")
    elif page == "Add Purchase":
        st.header("🛒 Log New Purchase")
        
        # 1. Get all category names from the JSON
        categories = list(PRODUCTS.keys())
        cat = st.selectbox("Category", categories)
        
        # 2. Extract product and brand data safely
        cat_data = PRODUCTS.get(cat, {})
        items = cat_data.get("items", [])
        brands_info = cat_data.get("brands", {})
        
        # 3. Handle the inconsistent keys in your JSON ("Standard", "Eco-Friendly", and "EcoFriendly")
        std_brands = brands_info.get("Standard", [])
        eco_brands = brands_info.get("Eco-Friendly", []) + brands_info.get("EcoFriendly", [])
        
        all_brands_list = std_brands + eco_brands
        
        # UI Columns
        col1, col2 = st.columns(2)
        with col1:
            prod = st.selectbox("Product", items)
            brand = st.selectbox("Brand", all_brands_list)
            price = st.number_input("Price", min_value=0.0, step=1.0)

        with col2:
            origin = st.selectbox("Origin", list(COUNTRY_DISTANCES.keys()))
            mode = st.selectbox("Transport Mode", list(TRANSPORT_FACTORS.keys()))
            
            # Identify if the selected brand is eco-friendly for impact calculation
            is_eco = brand in eco_brands
            
            # Show a recommendation only if a standard brand is picked and eco alternatives exist
            if brand in std_brands and eco_brands:
                st.warning(f"🌱 Eco-Tip: Consider switching to **{random.choice(eco_brands)}**!")

            if st.button("Add to Basket"):
                dist = COUNTRY_DISTANCES[origin]
                impact_calc = price * (0.4 if is_eco else 1.2) + (dist * TRANSPORT_FACTORS[mode])
                earned_clovers = 15 if is_eco and origin == "Local (Within Country)" else (10 if is_eco else 5)
                
                # Append to user history
                profile["purchases"].append({
                    "product": prod, 
                    "brand": brand, 
                    "price": price, 
                    "impact": round(impact_calc, 2), 
                    "clovers_earned": earned_clovers, 
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
                
                save_users()
                st.success(f"Successfully added! +{earned_clovers} 🍀")
                st.rerun()
    # ---------- DASHBOARD ----------
    elif page == "Dashboard":
        st.header("📊 Sustainability Insights")
        history = profile.get("purchases", [])
        if history:
            df = pd.DataFrame(history)
            st.metric("Total CO₂ Footprint", f"{total_impact:.2f} kg")
            st.line_chart(df.set_index("date")["impact"])
            st.dataframe(df)
        else:
            st.info("No purchase history found.")

    # ---------- ECO GAME ----------
    elif page == "Eco Game":
        st.header("🤖 Robo Runner")
        clovers = sum(p.get("clovers_earned", 0) for p in profile.get("purchases", []))
        st.subheader(f"🍀 Total Clovers: {clovers}")

        if os.path.exists("game.html"):
            with open("game.html", "r", encoding="utf-8") as f:
                html_code = f.read()
            html_code = html_code.replace("let cloverScore = 0;", f"let cloverScore = {clovers};")
            components.html(html_code, height=600)
        else:
            st.error("File 'game.html' not found.")

    # ---------- SETTINGS ----------
    elif page == "Settings":
        st.header("⚙️ Settings")
        st.selectbox("Currency Display", ALL_CURRENCIES)
        new_color = st.color_picker("Pick Background Color", st.session_state.bg_color)
        if st.button("Apply Theme"):
            st.session_state.bg_color = new_color
            st.rerun()
            
        st.divider()
        if st.button("Logout", type="primary"):
            st.session_state.logged_in = False
            st.rerun()
