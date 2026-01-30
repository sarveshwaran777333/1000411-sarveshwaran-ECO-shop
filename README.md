# 1000411-sarveshwaran-ECO-shop

# ShopImpact: Conscious Shopping Dashboard
Transforming everyday shopping into a mindful, eco-conscious experience.

# Project Overview
ShopImpact is an interactive web application designed for ShopImpact Ltd. to help users visualize the hidden environmental costs of their purchases. By logging planned buys, the app calculates an estimated CO₂ footprint and nudges users toward sustainable habits through rewards and ethical alternatives.

# User Focus
1. Target Audience: Young adults, students, and eco-conscious families.
2. Problem Solved: Bridges the gap between purchasing and environmental awareness by making carbon footprints visible.
3. Design Philosophy: Uses a "Design Thinking" approach to create empowerment rather than guilt.

# Key Features
As per the project brief, this application integrates the following:
1. Real-time CO₂ Calculation: Uses curated multipliers to estimate the environmental cost (Price × Multiplier).
2. Live Dashboard: A monthly summary of total spending and carbon impact.
3. Eco-Badges: Automated rewards like "Eco Saver" or "Low Impact Shopper" based on user choices.
4. Ethical Suggestions: Provides a list of greener brand alternatives for different product types.
5. Mascot Graphics: Displays visual "leaves" or "eco-badges" using Python’s Turtle library when positive choices are made.
6. Random Eco-Tips: Motivational quotes and facts about sustainable living (e.g., benefits of bamboo).

# Integration & Logic
1. Core Constructs: The app utilizes Python lists and dictionaries to store purchase history and product impact multipliers.
2. Modular Design: Built with specific functions for impact calculation and UI rendering to ensure clean, maintainable code.
3. UI/UX: Developed in Streamlit using an earthy color palette (greens, beiges) and a clear visual hierarchy for elderly and tech-savvy users alike.

# Deployment Instructions
To view the project, you can visit the [Web App Link](https://1000411-sarveshwaran-eco-shop-dh8jxzwuqlacc6lpn97pcn.streamlit.app/)

# To run locally:
1. Clone this repository.
2. Ensure you have the dependencies installed
3. Run the command: streamlit run app.py.

# Application Flow

The ShopImpact app follows a sequential flow designed to move the user from data entry to reflection and reward:

1. User Input Stage (Data Entry)
Product Details: The user enters the product type, brand, and price into the Streamlit input fields.
Planned Purchase Log: The user clicks a button to "Log Purchase," which triggers the Python logic to store the data in a list or dictionary structure.
2. Processing & Logic Stage (The "Engine")
CO₂ Estimation: The app applies a specific multiplier to the product type (e.g., high impact for leather, low impact for second-hand).
Impact Calculation: The system calculates the environmental cost using the formula: Price x Multiplier.
State Management: The purchase is appended to a session-wide list to keep the dashboard updated in real-time.
3. Visualization Stage (The Dashboard)
Real-time Summary: The app displays a monthly dashboard summarizing the total amount spent and the total estimated CO₂ impact.
Visual Hierarchy: Large headers and earthy colors are used to ensure important numbers stand out for the user.
4. Feedback & Nudging Stage (Social Good)
Badge Awarding: The logic checks if the user's footprint is under a certain threshold and awards fun badges like “Eco Saver of the Month”.
Greener Alternatives: Based on the product type entered, the app displays a list of suggested ethical or eco-friendly brand alternatives.
5. Deployment & Accessibility
Cloud Hosting: The final solution is deployed via Streamlit Cloud, making the "Social Good" tool accessible to a real-world audience via a live URL.

# Repository Structure

1. app.py: Main Python file containing the Streamlit interface and logic.
2. requirements.txt: List of necessary Python packages for Streamlit Cloud deployment.
3. assets/: Contains wireframe sketches and product images.

# Story board
[story board link](https://www.canva.com/design/DAG7R0IKjhY/R_1WE0b1CVk_fCrz60k61g/edit?utm_content=DAG7R0IKjhY&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton)

# screenshots

<img width="1780" height="568" alt="login and sign up page" src="https://github.com/user-attachments/assets/370f3923-4c01-454a-874b-5b74fd848a7d" />

<img width="1837" height="573" alt="home page" src="https://github.com/user-attachments/assets/dcf7e5c5-8e3c-4ee1-a4e4-6d6b1cdadc7a" />

<img width="1871" height="622" alt="add purchase page" src="https://github.com/user-attachments/assets/97a388a3-9e65-40bc-932d-2622bd8d4a20" />

<img width="1808" height="783" alt="dashboard page" src="https://github.com/user-attachments/assets/bdb58ed2-f213-4bb3-b229-e956785e776b" />

<img width="1918" height="767" alt="eco game page" src="https://github.com/user-attachments/assets/86181bb6-8bec-48ab-afec-3bb72f47d317" />

<img width="1856" height="487" alt="settings page" src="https://github.com/user-attachments/assets/2040e189-48a6-4fe9-982d-c066d9da53dd" />

# Tested by

Sister: tested design and logic part of the app

Saif (friend): 

# Credits & Acknowledgements

This project was developed as part of the Summative Assessment for the Python Programming course under the Artificial Intelligence program.

School Name: Jain Vidyalaya
Student Name: K.Sarveshwaran
Class: XI
Registration ID: 1000411
Mentor: Syedali Beema
