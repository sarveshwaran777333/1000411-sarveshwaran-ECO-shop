import streamlit as st
import streamlit.components.v1 as components
import json
import os
import pandas as pd
from datetime import datetime
import random
from PIL import Image, ImageDraw
import math

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
    "Local (Within Country)": 150
}

COUNTRY_COORDS = {
    "India": (20.5937, 78.9629),
    "Pakistan": (30.3753, 69.3451),
    "Bangladesh": (23.6850, 90.3563),
    "Sri Lanka": (7.8731, 80.7718),
    "Nepal": (28.3949, 84.1240),
    "Bhutan": (27.5142, 90.4336),
    "China": (35.8617, 104.1954),
    "Japan": (36.2048, 138.2529),
    "South Korea": (35.9078, 127.7669),
    "North Korea": (40.3399, 127.5101),
    "Thailand": (15.8700, 100.9925),
    "Malaysia": (4.2105, 101.9758),
    "Singapore": (1.3521, 103.8198),
    "Indonesia": (-0.7893, 113.9213),
    "Philippines": (12.8797, 121.7740),
    "Vietnam": (14.0583, 108.2772),
    "Cambodia": (12.5657, 104.9910),
    "Laos": (19.8563, 102.4955),
    "Myanmar": (21.9162, 95.955974),
    "Afghanistan": (33.9391, 67.7100),
    "Iran": (32.4279, 53.6880),
    "Iraq": (33.2232, 43.6793),
    "Israel": (31.0461, 34.8516),
    "Jordan": (30.5852, 36.2384),
    "Saudi Arabia": (23.8859, 45.0792),
    "UAE": (23.4241, 53.8478),
    "Qatar": (25.3548, 51.1839),
    "Kuwait": (29.3759, 47.9774),
    "Oman": (21.5126, 55.9233),
    "Turkey": (38.9637, 35.2433),
    "Kazakhstan": (48.0196, 66.9237),
    "Uzbekistan": (41.3775, 64.5853),
    "Turkmenistan": (38.9697, 59.5563),
    "Kyrgyzstan": (41.2044, 74.7661),
    "Tajikistan": (38.8610, 71.2761),
    "Mongolia": (46.8625, 103.8467),
    "UK": (55.3781, -3.4360),
    "Ireland": (53.1424, -7.6921),
    "Germany": (51.1657, 10.4515),
    "France": (46.2276, 2.2137),
    "Italy": (41.8719, 12.5674),
    "Spain": (40.4637, -3.7492),
    "Portugal": (39.3999, -8.2245),
    "Netherlands": (52.1326, 5.2913),
    "Belgium": (50.5039, 4.4699),
    "Switzerland": (46.8182, 8.2275),
    "Austria": (47.5162, 14.5501),
    "Poland": (51.9194, 19.1451),
    "Czech Republic": (49.8175, 15.4730),
    "Slovakia": (48.6690, 19.6990),
    "Hungary": (47.1625, 19.5033),
    "Romania": (45.9432, 24.9668),
    "Bulgaria": (42.7339, 25.4858),
    "Greece": (39.0742, 21.8243),
    "Sweden": (60.1282, 18.6435),
    "Norway": (60.4720, 8.4689),
    "Finland": (61.9241, 25.7482),
    "Denmark": (56.2639, 9.5018),
    "Russia": (61.5240, 105.3188),
    "Ukraine": (48.3794, 31.1656),
    "Belarus": (53.7098, 27.9534),
    "Lithuania": (55.1694, 23.8813),
    "Latvia": (56.8796, 24.6032),
    "Estonia": (58.5953, 25.0136),
    "Serbia": (44.0165, 21.0059),
    "Croatia": (45.1, 15.2),
    "Slovenia": (46.1512, 14.9955),
    "Bosnia and Herzegovina": (43.9159, 17.6791),
    "North Macedonia": (41.6086, 21.7453),
    "Albania": (41.1533, 20.1683),
    "Montenegro": (42.7087, 19.3744),
    "Iceland": (64.9631, -19.0208),
    "Egypt": (26.8206, 30.8025),
    "South Africa": (-30.5595, 22.9375),
    "Nigeria": (9.0820, 8.6753),
    "Kenya": (-0.0236, 37.9062),
    "Ethiopia": (9.1450, 40.4897),
    "Somalia": (5.1521, 46.1996),
    "Tanzania": (-6.3690, 34.8888),
    "Uganda": (1.3733, 32.2903),
    "Rwanda": (-1.9403, 29.8739),
    "Burundi": (-3.3731, 29.9189),
    "Ghana": (7.9465, -1.0232),
    "Senegal": (14.4974, -14.4524),
    "Morocco": (31.7917, -7.0926),
    "Algeria": (28.0339, 1.6596),
    "Tunisia": (33.8869, 9.5375),
    "Libya": (26.3351, 17.2283),
    "Sudan": (12.8628, 30.2176),
    "South Sudan": (6.8770, 31.3070),
    "Zambia": (-13.1339, 27.8493),
    "Zimbabwe": (-19.0154, 29.1549),
    "Botswana": (-22.3285, 24.6849),
    "Namibia": (-22.9576, 18.4904),
    "Angola": (-11.2027, 17.8739),
    "Mozambique": (-18.6657, 35.5296),
    "Madagascar": (-18.7669, 46.8691),
    "USA": (37.0902, -95.7129),
    "Canada": (56.1304, -106.3468),
    "Mexico": (23.6345, -102.5528),
    "Brazil": (-14.2350, -51.9253),
    "Argentina": (-38.4161, -63.6167),
    "Chile": (-35.6751, -71.5430),
    "Peru": (-9.1899, -75.0152),
    "Colombia": (4.5709, -74.2973),
    "Venezuela": (6.4238, -66.5897),
    "Bolivia": (-16.2902, -63.5887),
    "Paraguay": (-23.4425, -58.4438),
    "Uruguay": (-32.5228, -55.7658),
    "Ecuador": (-1.8312, -78.1834),
    "Panama": (8.5379, -80.7821),
    "Costa Rica": (9.7489, -83.7534),
    "Cuba": (21.5218, -77.7812),
    "Jamaica": (18.1096, -77.2975),
    "Dominican Republic": (18.7357, -70.1627),
    "Haiti": (18.9712, -72.2852),
    "Australia": (-25.2744, 133.7751),
    "New Zealand": (-40.9006, 174.8860),
    "Papua New Guinea": (-6.314993, 143.95555),
    "Fiji": (-17.7134, 178.0650),
    "Solomon Islands": (-9.6457, 160.1562),
    "Samoa": (-13.7590, -172.1046),
    "Tonga": (-21.1790, -175.1982),
    "Vanuatu": (-15.3767, 166.9592)
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

def calculate_distance_km(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

# ---------------- BADGE SYSTEM ----------------
def calculate_badge(purchases):
    if not purchases:
        return "🌱 Green Beginner", "Start making eco-friendly choices to earn badges!"

    total_impact = sum(p.get("impact", 0) for p in purchases)
    eco_count = sum(1 for p in purchases if p.get("clovers_earned", 0) >= 10)
    eco_ratio = eco_count / len(purchases)

    if eco_ratio > 0.7 and total_impact < 400:
        return "🏆 Eco Champion", "Outstanding! You consistently make low-impact choices!"
    elif eco_ratio > 0.5:
        return "🌿 Eco Saver", "Great job choosing sustainable options!"
    elif eco_ratio > 0.3:
        return "🌎 Conscious Shopper", "You're on the path to greener shopping!"
    else:
        return "🌍 Getting Started", "Keep improving your eco-friendly habits!"

def draw_badge_image(badge_name):
    img = Image.new("RGBA", (220, 220), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    colors = {
        "🌱 Green Beginner": "#A5D6A7",
        "🌍 Getting Started": "#81C784",
        "🌎 Conscious Shopper": "#66BB6A",
        "🌿 Eco Saver": "#43A047",
        "🏆 Eco Champion": "#2E7D32"
    }

    color = colors.get(badge_name, "#4CAF50")
    draw.ellipse((10, 10, 210, 210), fill=color, outline="darkgreen", width=5)
    draw.ellipse((80, 70, 140, 150), fill="white")
    draw.polygon([(110, 50), (125, 20), (140, 50)], fill="white")

    short_text = badge_name.split(" ", 1)[1] if " " in badge_name else badge_name
    draw.text((110, 170), short_text[:12], fill="white", anchor="mm")

    return img

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
            else:
                st.error("Invalid credentials")
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
    page = st.sidebar.radio("Menu", ["Home", "Add Purchase", "Dashboard", "Eco Game", "Settings"])

    # ---------- HOME ----------
    if page == "Home":
        st.title(f"Welcome, {user} 👋")
        st.info(f"💡 {random.choice(ECO_TIPS)}")

        clovers = sum(p.get("clovers_earned", 0) for p in profile.get("purchases", []))
        st.metric("Total Clovers", f"🍀 {clovers}")

        badge, badge_msg = calculate_badge(profile.get("purchases", []))
        st.subheader("🎖 Your Sustainability Badge")
        st.image(draw_badge_image(badge), width=160)
        st.success(badge)
        st.caption(badge_msg)

    # ---------- ADD PURCHASE ----------
    elif page == "Add Purchase":
        st.header("🛒 Log New Purchase")

        categories = list(PRODUCTS.keys())
        cat = st.selectbox("Category", categories)
        cat_data = PRODUCTS.get(cat, {})
        items = cat_data.get("items", [])
        brands_info = cat_data.get("brands", {})

        std_brands = brands_info.get("Standard", [])
        eco_brands = brands_info.get("Eco-Friendly", []) + brands_info.get("EcoFriendly", [])
        all_brands_list = std_brands + eco_brands

        col1, col2 = st.columns(2)
        with col1:
            prod = st.selectbox("Product", items)
            brand = st.selectbox("Brand", all_brands_list)
            price = st.number_input("Price", min_value=0.0, step=1.0)

        with col2:
            origin_options = ["Local (Within Country)"] + list(COUNTRY_COORDS.keys())
            origin = st.selectbox("Origin Country", origin_options)
            mode = st.selectbox("Transport Mode", list(TRANSPORT_FACTORS.keys()))
            is_eco = brand in eco_brands

            if brand in std_brands and eco_brands:
                st.warning(f"🌱 Consider switching to **{random.choice(eco_brands)}**!")

            if st.button("Add to Basket"):
                dist = COUNTRY_DISTANCES[origin]
                impact_calc = price * (0.4 if is_eco else 1.2) + (dist * TRANSPORT_FACTORS[mode])
                earned_clovers = 15 if is_eco else 5

                profile["purchases"].append({
                    "product": prod,
                    "brand": brand,
                    "price": price,
                    "impact": round(impact_calc, 2),
                    "clovers_earned": earned_clovers,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M")
                })

                save_users()
                badge, badge_msg = calculate_badge(profile["purchases"])

                st.balloons()
                st.image(draw_badge_image(badge), width=150)
                st.success(f"🎉 Badge Earned: {badge}")
                st.caption(badge_msg)
                st.rerun()

    # ---------- DASHBOARD ----------
    elif page == "Dashboard":
        st.header("📊 Sustainability Insights")
        history = profile.get("purchases", [])

        if history:
            df = pd.DataFrame(history)
            st.metric("Total CO₂ Footprint", f"{sum(df['impact']):.2f} kg")
            st.line_chart(df.set_index("date")["impact"])
            st.dataframe(df)

        badge, badge_msg = calculate_badge(history)
        st.markdown("### 🎖 Current Badge")
        st.image(draw_badge_image(badge), width=140)
        st.info(f"{badge} — {badge_msg}")

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
        new_color = st.color_picker("Pick Background Color", st.session_state.bg_color)
        if st.button("Apply Theme"):
            st.session_state.bg_color = new_color
            st.rerun()

        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()
