import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd
from io import BytesIO
import requests
from datetime import datetime
from fpdf import FPDF
import base64
import random

# === Streamlit Config ===
st.set_page_config(layout="wide", page_title="Personal Carbon Calculator")
st.title("🧮 Personal Carbon Footprint Calculator")

# === Background & Styling ===
def get_base64(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

backgroundfp_base64 = get_base64("C:/Users/abror/Downloads/Test New/foto_carbon.jpg")

st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{backgroundfp_base64}");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
        background-position: center;
        color: black;
    }}
    /* Untuk beberapa komponen yang override style */
    h1, h2, h3, h4, h5, h6, label, p, span, div, .stTextInput > label, .stSlider > label, .stNumberInput > label, .stSelectbox > label {{
        color: black !important;
    }}

    /* Tombol utama seperti "Calculate My Carbon Footprint" */
    button[kind="primary"] {{
        background-color: #0E1117 !important;
        color: white !important;
    }}

    /* Label kamera (Take photo) dan tombol "Clear photo" */
    .stCameraInput label,
    .stCameraInput button {{
        color: white !important;
    }}

    /* Dropdown dan pilihannya */
    .stSelectbox div[role="button"],
    .stSelectbox label,
    .stSelectbox span {{
        color: white !important;
    }}

    /* Perbaikan dropdown (daftar pilihan) */
    div[role="listbox"] > div {{
        color: white !important;
        background-color: rgba(0, 0, 0, 0.85) !important;
    }}

    div[role="option"]:hover {{
        background-color: #444 !important;
    }}
    </style>
""", unsafe_allow_html=True)

# === Sidebar: Language & About us ===
st.sidebar.title("🌱 Personal Carbon Calculator")
language = st.sidebar.selectbox("🌐Choose Language / Pilih Bahasa", ["English", "Bahasa Indonesia"])

st.sidebar.markdown("### ℹ️ About Us")
about_text = {
    "English": "This calculator estimates your annual carbon footprint based on daily habits like transportation, electricity usage, diet, and lifestyle. Understand your impact and take action for a sustainable future!",
    "Bahasa Indonesia": "Kalkulator ini memperkirakan jejak karbon tahunan Anda berdasarkan kebiasaan harian seperti transportasi, konsumsi listrik, pola makan, dan gaya hidup. Pahami dampakmu dan ambil langkah menuju masa depan berkelanjutan!"
}
st.sidebar.info(about_text[language])

# === Eco Tip of the Day ===
tips_daily = {
    "English": [
        "🚲 Use bike or walk when possible.",
        "💡 Switch to energy-saving LED lights.",
        "🥦 Try Meatless Mondays!",
        "🛍️ Bring reusable bags when shopping."
    ],
    "Bahasa Indonesia": [
        "🚲 Gunakan sepeda atau jalan kaki bila memungkinkan.",
        "💡 Gunakan lampu LED hemat energi.",
        "🥦 Coba hari tanpa daging (Meatless Monday)!",
        "🛍️ Bawa tas belanja yang bisa digunakan ulang."
    ]
}
st.sidebar.markdown("### 🌍 Eco Tip of the Day")
st.sidebar.success(random.choice(tips_daily[language]))

# Default country
country = "Indonesia"

# === User Input ===
st.subheader("🙋 User Info")
name = st.text_input("Your name" if language == "English" else "Nama Anda")
age = st.number_input("Your age" if language == "English" else "Usia Anda", min_value=5, max_value=120, step=1)
photo = st.camera_input("Take a photo (optional)" if language == "English" else "Ambil foto (opsional)")

# === EMISSION FACTORS ===
EMISSION_FACTORS = {
    "Indonesia": {
        "Transportation": {
            "car": 0.21,
            "motorcycle": 0.09,
            "bus": 0.105,
            "train": 0.045,
            "walk_or_bike": 0.0
        },
        "Electricity": 0.82,
        "Diet": {
            "meat_heavy": 2.5,
            "omnivore": 1.5,
            "vegetarian": 1.0,
            "vegan": 0.6
        },
        "Waste": 0.1,
        "Flights": {
            "domestic": 250,
            "international": 900
        },
        "Plastic": 6.0,
        "Clothing": 20
    }
}

# === Section: Transportation ===
st.header("🚗 Transportation")
col1, col2 = st.columns(2)
with col1:
    transport_mode = st.selectbox("Mode of daily transport", ["car", "motorcycle", "bus", "train", "walk_or_bike"])
    daily_distance = st.slider("Daily commute distance (km)", 0.0, 100.0, 10.0)
with col2:
    flight_domestic = st.number_input("Domestic flights per year", 0, step=1)
    flight_international = st.number_input("International flights per year", 0, step=1)

# === Section: Electricity ===
st.header("💡 Energy Consumption")
monthly_kwh = st.slider("Monthly electricity usage (kWh)", 0.0, 2000.0, 400.0)

# === Section: Diet & Lifestyle ===
st.header("🍽️ Diet & Consumption")
col3, col4 = st.columns(2)
with col3:
    diet_type = st.selectbox("Your diet type", ["meat_heavy", "omnivore", "vegetarian", "vegan"])
    meals_per_day = st.slider("Meals per day", 1, 5, 3)
with col4:
    clothes_purchased = st.number_input("Clothes purchased per year", 0, 100, 10)
    plastic_use = st.slider("Plastic waste per week (kg)", 0.0, 10.0, 1.0)

# === Section: Household Waste ===
st.header("🗑️ Household Waste")
weekly_waste = st.slider("General waste per week (kg)", 0.0, 50.0, 5.0)

# === Carbon Footprint Rating ===
if total_tonnes < 3:
    rating = "🟢 Low"
elif total_tonnes < 7:
    rating = "🟡 Medium"
else:
    rating = "🔴 High"

st.subheader("📉 Your Carbon Footprint Level")
st.warning(f"Your carbon footprint rating: **{rating} impact**")

pdf.chapter_title("📉 Carbon Footprint Rating")
pdf.chapter_body(f"Your impact rating is: {rating}")

# === Future Tracking (Simulasi Placeholder) ===
st.sidebar.markdown("---")
track_future = st.sidebar.checkbox("📅 Track my monthly carbon footprint", value=False)
if track_future:
    st.sidebar.info("🔔 We'll remind you to check your carbon footprint every month! (feature coming soon)")


# === CALCULATION ===
if st.button("🧾 Calculate My Carbon Footprint"):
    ef = EMISSION_FACTORS[country]

    # Convert to yearly
    yearly_distance = daily_distance * 365
    yearly_kwh = monthly_kwh * 12
    yearly_meals = meals_per_day * 365
    yearly_plastic = plastic_use * 52
    yearly_waste = weekly_waste * 52

    # Calculate emissions
    transport_emission = yearly_distance * ef["Transportation"][transport_mode]
    flight_emission = flight_domestic * ef["Flights"]["domestic"] + flight_international * ef["Flights"]["international"]
    electricity_emission = yearly_kwh * ef["Electricity"]
    diet_emission = ef["Diet"][diet_type] * yearly_meals
    clothing_emission = clothes_purchased * ef["Clothing"]
    plastic_emission = yearly_plastic * ef["Plastic"]
    waste_emission = yearly_waste * ef["Waste"]

    # Total emissions
    total_emissions = transport_emission + flight_emission + electricity_emission + diet_emission + clothing_emission + plastic_emission + waste_emission
    total_tonnes = round(total_emissions / 1000, 2)

    # === Carbon Offset Estimation ===
st.markdown("## 🌳 Carbon Offset Suggestion")
carbon_offset_per_tree = 0.021  # average 21 kg co2/year per tree 
trees_needed = int(total_tonnes * 1000 / (carbon_offset_per_tree * 1000))  # convert tonnes to kg

st.info(f"To offset your footprint, you would need to plant approximately **{trees_needed} trees**.")
st.caption("Note: One mature tree absorbs about 21 kg of CO₂ per year on average.")
pdf.chapter_title("🌳 Trees Needed to Offset")
pdf.chapter_body(f"You need approximately {trees_needed} trees to offset your carbon emissions.")

    # === Display Results ===
    st.success(f"🌍 Your estimated total carbon footprint is **{total_tonnes} tonnes CO₂/year**")

    # === SEND TO GOOGLE SHEETS ===
    if name and age:
        payload = {
            "Timestamp": datetime.now().isoformat(),
            "Name": name,
            "Age": age,
            "Total (Tonnes)": total_tonnes,
            "Transport": round(transport_emission / 1000, 2),
            "Flights": round(flight_emission / 1000, 2),
            "Electricity": round(electricity_emission / 1000, 2),
            "Diet": round(diet_emission / 1000, 2),
            "Clothing": round(clothing_emission / 1000, 2),
            "Plastic": round(plastic_emission / 1000, 2),
            "Waste": round(waste_emission / 1000, 2),
        }

        SHEET_BEST_URL = "https://api.sheetbest.com/sheets/c1663a28-e75f-4501-8341-c497b1b9867b"
        response = requests.post(SHEET_BEST_URL, json=payload)

        if response.status_code == 200:
            st.success("✅ Data successfully submitted to Google Sheet!")
        else:
            st.error("❌ Failed to submit data. Please check your Sheet.best link.")
    else:
        st.warning("Isi nama dan umur terlebih dahulu agar data bisa dikirim ke spreadsheet.")


    # === Visualization & Tips ===
    st.markdown("### 🔍 Breakdown by Category (in tonnes CO₂)")
    emission_data = {
        "Transportation": transport_emission / 1000,
        "Flights": flight_emission / 1000,
        "Electricity": electricity_emission / 1000,
        "Diet": diet_emission / 1000,
        "Clothing": clothing_emission / 1000,
        "Plastic": plastic_emission / 1000,
        "Waste": waste_emission / 1000,
    }

    for category, value in emission_data.items():
        st.info(f"{category}: {round(value, 2)}")

    # Recommendation Engine
    st.markdown("## 🌱 Lifestyle Recommendations")
    highest_emission = max(emission_data, key=emission_data.get)
    tips = {
        "Transportation": [
            "Cobalah menggunakan transportasi umum atau berbagi kendaraan (carpool).",
            "Jika memungkinkan, pilih berjalan kaki atau bersepeda."
        ],
        "Flights": [
            "Kurangi frekuensi penerbangan, terutama penerbangan internasional.",
            "Gunakan konferensi daring bila memungkinkan untuk perjalanan bisnis."
        ],
        "Electricity": [
            "Gunakan lampu LED hemat energi dan cabut perangkat elektronik jika tidak digunakan.",
            "Pertimbangkan memasang panel surya jika memungkinkan."
        ],
        "Diet": [
            "Kurangi konsumsi daging merah dan olahan.",
            "Mulailah dengan satu hari tanpa daging setiap minggu (Meatless Monday)."
        ],
        "Clothing": [
            "Kurangi pembelian pakaian baru; pilih produk second-hand atau berkualitas tinggi agar tahan lama.",
            "Daur ulang atau donasikan pakaian lama."
        ],
        "Plastic": [
            "Gunakan botol dan tas belanja yang dapat digunakan ulang.",
            "Hindari produk sekali pakai seperti sedotan dan kemasan plastik."
        ],
        "Waste": [
            "Pisahkan sampah organik dan anorganik.",
            "Gunakan komposter untuk mengolah limbah dapur menjadi pupuk alami."
        ]
    }

    st.subheader(f"📌 Fokus utama kamu: **{highest_emission}**")
    for tip in tips[highest_emission]:
        st.markdown(f"- {tip}")

    # Visualizations with transparent backgrounds ===
    st.markdown("## 📊 Visualize Your Carbon Footprint")
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("### 🥧 Pie Chart")
        fig1, ax1 = plt.subplots()
        ax1.pie(
            emission_data.values(),
            labels=emission_data.keys(),
            autopct='%1.1f%%',
            startangle=90,
            textprops={'color': 'black'}
        )
        ax1.axis('equal')
        fig1.patch.set_alpha(0)  # transparan
        ax1.patch.set_alpha(0)   # transparan
        st.pyplot(fig1)

    with col_right:
        st.markdown("### 📈 Bar Chart")
        fig2 = px.bar(
            x=list(emission_data.keys()),
            y=list(emission_data.values()),
            labels={'x': 'Category', 'y': 'Tonnes CO₂'},
            title="Annual Emissions by Category"
        )
        fig2.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='black',
            title_font_color='black'
        )
        fig2.update_traces(marker_color='darkblue')
        st.plotly_chart(fig2, use_container_width=True)

    # Save charts for PDF
    plt.figure()
    plt.pie(emission_data.values(), labels=emission_data.keys(), autopct='%1.1f%%', startangle=90)
    plt.axis('equal')
    plt.savefig("pie_chart.png")
    plt.close()

    plt.figure()
    plt.bar(emission_data.keys(), emission_data.values(), color='skyblue')
    plt.ylabel("Tonnes CO2")
    plt.title("Emissions by Category")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("bar_chart.png")
    plt.close()

    # PDF Class Definition
    class PDF(FPDF):
        def header(self):
            self.set_font("Arial", "B", 14)
            self.cell(0, 10, "Carbon Footprint Report", ln=True, align="C")
            self.ln(10)

        def chapter_title(self, title):
            self.set_font("Arial", "B", 12)
            self.cell(0, 10, title, ln=True)
            self.ln(2)

        def chapter_body(self, body):
            self.set_font("Arial", "", 11)
            self.multi_cell(0, 10, body)
            self.ln()

    # Build PDF
    pdf = PDF()
    pdf.add_page()
    pdf.chapter_title("User Information")
    pdf.chapter_body(f"Name: {name}\nAge: {age}\nCountry: {country}")

    if photo is not None:
        # Simpan foto sementara
        photo_path = "photo.jpg"
        with open(photo_path, "wb") as f:
            f.write(photo.getbuffer())

        pdf.image(photo_path, w=100)
        pdf.ln(5)
        pdf.chapter_title("Photo User")
    pdf.chapter_title("Total Carbon Footprint")
    pdf.chapter_body(f"{total_tonnes} tonnes CO2 per year")
    pdf.chapter_title("Emission Breakdown")
    for cat, val in emission_data.items():
        pdf.chapter_body(f"{cat}: {round(val, 2)} tonnes CO2")
    pdf.chapter_title(f"Recommended Focus Area: {highest_emission}")
    for tip in tips[highest_emission]:
        pdf.chapter_body(f"- {tip}")
    pdf.chapter_title("Pie Chart")
    pdf.image("pie_chart.png", w=150)
    pdf.chapter_title("Bar Chart")
    pdf.image("bar_chart.png", w=150)


    # Export PDF to buffer
    pdf_output = pdf.output(dest='S').encode('latin1')
    pdf_buffer = BytesIO(pdf_output)

    # Download button
    st.download_button(
        label="📥 Download Your Report (PDF)",
        data=pdf_buffer,
        file_name="carbon_report.pdf",
        mime="application/pdf"
    )

    st.markdown("---")
    st.caption("📝 Emission factors are approximations. Results may vary based on lifestyle and region.")
