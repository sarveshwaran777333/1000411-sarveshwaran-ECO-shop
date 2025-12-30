import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import random
import base64

st.set_page_config(page_title="GreenBasket", layout="wide")

USER_FILE = "users.json"
PRODUCT_FILE = "products.json"
ECO_FILE = "eco_alternatives.json"

if "bg_color" not in st.session_state:
    st.session_state.bg_color = "#1b5e20"

def get_text_color(bg):
    bg = bg.lstrip("#")
    r, g, b = int(bg[0:2], 16), int(bg[2:4], 16), int(bg[4:6], 16)
    brightness = (r * 299 + g * 587 + b * 114) / 1000
    return "#000000" if brightness > 140 else "#ffffff"

def set_background(bg_color):
    text_color = get_text_color(bg_color)
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: {bg_color};
            color: {text_color};
        }}

        [data-testid="stSidebar"] {{
            background-color: {bg_color};
        }}
        [data-testid="stSidebar"] * {{
            color: {text_color} !important;
            font-weight: bold;
        }}

        h1, h2, h3, h4, h5, h6, p, label {{
            color: {text_color} !important;
        }}

        /* Apply Button Styling */
        div.stButton > button {{
            border: 2px solid {text_color} !important;
            color: {text_color} !important;
            background-color: transparent !important;
            border-radius: 12px !important;
            padding: 10px 24px !important;
            font-weight: bold !important;
        }}

        /* ===== THE COLOR PICKER OUTLINE FIX ===== */
        /* Targets the specific outer wrapper of the color picker */
        [data-testid="stColorPicker"] {{
            border: 2px solid {text_color} !important;
            border-radius: 12px !important;
            padding: 10px !important;
            width: fit-content !important;
            background-color: rgba(255, 255, 255, 0.05) !important;
        }}

        /* Removes any internal faint borders that Streamlit adds */
        [data-testid="stColorPicker"] div {{
            border: none !important;
        }}

        /* Optional: Adds a tiny border just to the color square itself */
        [data-testid="stColorPicker"] div[role="button"] {{
            border: 1px solid {text_color} !important;
            border-radius: 4px !important;
        }}

        input {{
            background-color: white !important;
            color: black !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

set_background(st.session_state.bg_color)

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

users = safe_load_json(USER_FILE, {})
PRODUCTS = safe_load_json(PRODUCT_FILE, {"Clothing": ["T-Shirt"], "Groceries": ["Apple"]})
ECO_ALTS = safe_load_json(ECO_FILE, {"Apple": ["Organic Local Apple"]})

def save_users():
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)


def eco_runner_game():
    img_path = os.path.join(os.getcwd(), "robo.png")
    if not os.path.exists(img_path):
        st.error("Missing asset: robo.png")
        return

    with open(img_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()

    html = f"""
    <div style="border:3px solid green; padding:10px; border-radius:15px; background: white; text-align: center;">
      <canvas id="game" width="820" height="320" style="border-radius:10px;"></canvas>
      <div style="margin-top:10px;">
        <button id="restartBtn" style="padding:10px 20px; font-weight:bold; border:2px solid #1b5e20; background:#e8f5e9; cursor:pointer; border-radius:8px;">Restart Game</button>
      </div>
    </div>
    <script>
      const canvas = document.getElementById("game");
      const ctx = canvas.getContext("2d");
      const robot = new Image();
      robot.src = "data:image/png;base64,{img_b64}";

      let y = 220, vy = 0, gravity = 0.7, jumping = false;
      let coins = [], obstacles = [], score = 0;
      let obstacleCooldown = 0, gameOver = false;

      document.addEventListener("keydown", (e) => {{
        if (e.code === "Space" && !gameOver) {{
          if(!jumping) {{ vy = -13; jumping = true; }}
          e.preventDefault();
        }}
      }});

      document.getElementById("restartBtn").onclick = () => {{
        score = 0; coins = []; obstacles = []; gameOver = false;
        y = 220; vy = 0; jumping = false; obstacleCooldown = 0;
      }};

      function spawn() {{
        if (Math.random() < 0.03) coins.push({{ x: 820, y: 170 + Math.random()*60 }});
        if (obstacleCooldown <= 0) {{
          if (Math.random() < 0.03) {{
            obstacles.push({{ x: 820, y: 240, w: 28, h: 28 }});
            obstacleCooldown = 120;
          }}
        }} else {{ obstacleCooldown--; }}
      }}

      function update() {{
        if (gameOver) return;
        vy += gravity; y += vy;
        if (y >= 220) {{ y = 220; vy = 0; jumping = false; }}
        coins.forEach(c => c.x -= 4);
        obstacles.forEach(o => o.x -= 5);

        coins = coins.filter(c => {{
          if (Math.abs(c.x - 90) < 30 && Math.abs(c.y - y) < 40) {{ score++; return false; }}
          return c.x > 0;
        }});

        obstacles.forEach(o => {{
          if (50 < o.x + o.w && 110 > o.x && y + 60 > o.y) gameOver = true;
        }});
      }}

      function draw() {{
        ctx.fillStyle = "#f1f8e9";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(robot, 50, y, 60, 60);
        ctx.fillStyle = "gold";
        coins.forEach(c => {{ ctx.beginPath(); ctx.arc(c.x, c.y, 10, 0, Math.PI*2); ctx.fill(); }});
        ctx.fillStyle = "#d32f2f";
        obstacles.forEach(o => {{ ctx.fillRect(o.x, o.y, o.w, o.h); }});
        ctx.fillStyle = "#1b5e20";
        ctx.font = "bold 20px Arial";
        ctx.fillText("💰 Score: " + score, 20, 40);
        if (gameOver) {{
          ctx.fillStyle = "rgba(0,0,0,0.7)";
          ctx.fillRect(0,0,820,320);
          ctx.fillStyle = "white"; ctx.font = "bold 30px Arial";
          ctx.fillText("GAME OVER", 330, 160);
        }}
      }}

      function loop() {{ spawn(); update(); draw(); requestAnimationFrame(loop); }}
      robot.onload = loop;
    </script>
    """
    st.components.v1.html(html, height=460)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🌱 GreenBasket")
    t1, t2 = st.tabs(["Login", "Sign Up"])
    with t1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Login"):
            if u in users and users[u]["password"] == p:
                st.session_state.logged_in = True
                st.session_state.user = u
                st.rerun()
            else: st.error("Wrong credentials")
    with t2:
        nu = st.text_input("New User")
        np = st.text_input("New Pass", type="password")
        if st.button("Register"):
            if nu in users: st.error("Exists")
            else:
                users[nu] = {"password": np, "purchases": []}
                save_users()
                st.success("Success! Please Login.")
else:
    user = st.session_state.user
    if user not in users:
        st.session_state.logged_in = False
        st.rerun()
    
    profile = users[user]
    
    st.sidebar.title("GreenBasket")
    page = st.sidebar.radio("Navigate", ["Home", "Add Purchase", "Dashboard", "Eco Game", "Settings"])

    if page == "Home":
        st.title(f"Welcome, {user}!")
        st.write("Track your shopping and save the planet.")

    elif page == "Add Purchase":
        st.header("Add Purchase")
        cat = st.selectbox("Category", list(PRODUCTS.keys()))
        prod = st.selectbox("Product", PRODUCTS[cat])
        price = st.number_input("Price (₹)", min_value=0.0)
        if st.button("Add"):
            profile["purchases"].append({
                "date": datetime.now().strftime("%Y-%m-%d"),
                "product": prod, "price": price, "impact": price * 1.2
            })
            save_users()
            st.success("Saved!")

    elif page == "Dashboard":
        st.header("Your Impact")
        if profile["purchases"]:
            df = pd.DataFrame(profile["purchases"])
            st.dataframe(df)
            st.line_chart(df["impact"])
        else: st.info("No data.")

    elif page == "Eco Game":
        st.header("Eco Runner")
        eco_runner_game()

    elif page == "Settings":
        st.header("⚙️ Settings")
        st.session_state.bg_color = st.color_picker("Choose Theme Color", st.session_state.bg_color)
        if st.button("Apply Theme"):
            st.rerun()

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()
