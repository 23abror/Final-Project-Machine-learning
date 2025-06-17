import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
from io import BytesIO
import requests
from datetime import datetime
from fpdf import FPDF
import base64
import random
import os

# === Streamlit Config ===
st.set_page_config(layout="wide", page_title="Personal Carbon Calculator")
st.title("🧮 Personal Carbon Footprint Calculator")

# Garis
st.markdown("<hr style='border: 1px solid black;'>", unsafe_allow_html=True)

# === Inisialisasi Session State (SUDAH BENAR) ===
# Ini adalah "memori" aplikasi.
if 'calculation_done' not in st.session_state:
    st.session_state.calculation_done = False
    st.session_state.results = {}

# === Definisi Class PDF (SUDAH BENAR) ===
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
        # Mengatasi error unicode dengan FPDF
        self.multi_cell(0, 10, body.encode('latin-1', 'replace').decode('latin-1'))
        self.ln()

# === Background & Styling (SUDAH BENAR) ===
def get_base64_from_path(file_path):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        st.warning(f"File background tidak ditemukan di: {file_path}. Pastikan path file sudah benar.")
        return None

backgroundfp_base64 = get_base64_from_path("C:/Users/abror/Downloads/Test New/foto_carbon.jpg")

if backgroundfp_base64:
    st.markdown(f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{backgroundfp_base64}");
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
            background-position: center;
        }}
        /* Sisanya sama */
        h1, h2, h3, h4, h5, h6, label, p, span, div, .stTextInput > label, .stSlider > label, .stNumberInput > label, .stSelectbox > label, .stButton > button {{
            color: black !important;
        }}
        button[kind="primary"] {{
            background-color: #0E1117 !important;
            color: white !important;
        }}
        </style>
    """, unsafe_allow_html=True)


# === Sidebar: Language & About us (SUDAH BENAR) ===
st.sidebar.title("🌱 Personal Carbon Calculator")
language = st.sidebar.selectbox("🌐Choose Language / Pilih Bahasa", ["English", "Bahasa Indonesia"])

st.sidebar.markdown("### ℹ️ About Us")
about_text = {
    "English": "This calculator estimates your annual carbon footprint...",
    "Bahasa Indonesia": "Kalkulator ini memperkirakan jejak karbon tahunan Anda..."
}
st.sidebar.info(about_text[language])

# === Eco Tip of the Day (SUDAH BENAR) ===
tips_daily = {
    "English": ["🚲 Use bike or walk when possible.", "💡 Switch to energy-saving LED lights."],
    "Bahasa Indonesia": ["🚲 Gunakan sepeda atau jalan kaki bila memungkinkan.", "💡 Gunakan lampu LED hemat energi."]
}
st.sidebar.markdown("### 🌍 Eco Tip of the Day")
st.sidebar.success(random.choice(tips_daily[language]))

# === UI Input Pengguna (SUDAH BENAR) ===
country = "Indonesia"
st.subheader("🙋 User Info")
name = st.text_input("Your name" if language == "English" else "Nama Anda")
age = st.number_input("Your age" if language == "English" else "Usia Anda", min_value=5, max_value=120, value=25, step=1)
photo = st.camera_input("Take a photo (optional)" if language == "English" else "Ambil foto (opsional)")

EMISSION_FACTORS = { "Indonesia": { "Transportation": {"car": 0.21, "motorcycle": 0.09, "bus": 0.105, "train": 0.045, "walk_or_bike": 0.0}, "Electricity": 0.82, "Diet": {"meat_heavy": 2.5, "omnivore": 1.5, "vegetarian": 1.0, "vegan": 0.6}, "Waste": 0.1, "Flights": {"domestic": 250, "international": 900}, "Plastic": 6.0, "Clothing": 20 } }

st.header("🚗 Transportation")
col1, col2 = st.columns(2)
with col1:
    transport_mode = st.selectbox("Mode of daily transport", ["car", "motorcycle", "bus", "train", "walk_or_bike"])
    daily_distance = st.slider("Daily commute distance (km)", 0.0, 100.0, 10.0)
with col2:
    flight_domestic = st.number_input("Domestic flights per year", 0, step=1)
    flight_international = st.number_input("International flights per year", 0, step=1)

st.header("💡 Energy Consumption")
monthly_kwh = st.slider("Monthly electricity usage (kWh)", 0.0, 2000.0, 400.0)

st.header("🍽️ Diet & Consumption")
col3, col4 = st.columns(2)
with col3:
    diet_type = st.selectbox("Your diet type", ["meat_heavy", "omnivore", "vegetarian", "vegan"])
    meals_per_day = st.slider("Meals per day", 1, 5, 3)
with col4:
    clothes_purchased = st.number_input("Clothes purchased per year", 0, 100, 10)
    plastic_use = st.slider("Plastic waste per week (kg)", 0.0, 10.0, 1.0)

st.header("🗑️ Household Waste")
weekly_waste = st.slider("General waste per week (kg)", 0.0, 50.0, 5.0)


# === BAGIAN LOGIKA UTAMA: Kalkulasi & Penyimpanan State ===
# Ini adalah bagian yang direvisi total.
# Tugas blok ini hanya MENGHITUNG dan MENYIMPAN ke memori.
if st.button("🧾 Calculate My Carbon Footprint", type="primary"):
    # 1. Lakukan semua kalkulasi satu kali. Hapus semua duplikasi.
    yearly_distance = daily_distance * 365
    yearly_kwh = monthly_kwh * 12
    yearly_meals = meals_per_day * 365
    yearly_plastic = plastic_use * 52
    yearly_waste = weekly_waste * 52

    transport_emission = yearly_distance * EMISSION_FACTORS["Indonesia"]["Transportation"][transport_mode]
    flight_emission = flight_domestic * EMISSION_FACTORS["Indonesia"]["Flights"]["domestic"] + flight_international * EMISSION_FACTORS["Indonesia"]["Flights"]["international"]
    electricity_emission = yearly_kwh * EMISSION_FACTORS["Indonesia"]["Electricity"]
    diet_emission = EMISSION_FACTORS["Indonesia"]["Diet"][diet_type] * yearly_meals
    clothing_emission = clothes_purchased * EMISSION_FACTORS["Indonesia"]["Clothing"]
    plastic_emission = yearly_plastic * EMISSION_FACTORS["Indonesia"]["Plastic"]
    waste_emission = yearly_waste * EMISSION_FACTORS["Indonesia"]["Waste"]

    total_emissions_kg = sum([transport_emission, flight_emission, electricity_emission, diet_emission, clothing_emission, plastic_emission, waste_emission])
    total_tonnes = round(total_emissions_kg / 1000, 2)
    trees_needed = int(total_emissions_kg / 21) # 1 pohon serap 21 kg CO2/tahun

    emission_data_tonnes = {
        "Transportation": transport_emission / 1000, "Flights": flight_emission / 1000,
        "Electricity": electricity_emission / 1000, "Diet": diet_emission / 1000,
        "Clothing": clothing_emission / 1000, "Plastic": plastic_emission / 1000,
        "Waste": waste_emission / 1000,
    }
    
    if total_tonnes < 3:
        rating_display, rating_pdf = "🟢 Low", "Low"
    elif total_tonnes < 7:
        rating_display, rating_pdf = "🟡 Medium", "Medium"
    else:
        rating_display, rating_pdf = "🔴 High", "High"

    # Cari kategori emisi tertinggi
    highest_emission_category = max(emission_data_tonnes, key=emission_data_tonnes.get)

    # 2. Simpan SEMUA hasil yang dibutuhkan nanti ke dalam 'st.session_state.results'
    st.session_state.results = {
        "name": name,
        "age": age,
        "country": country,
        "photo_bytes": photo.getvalue() if photo else None,
        "total_tonnes": total_tonnes,
        "trees_needed": trees_needed,
        "rating_display": rating_display,
        "rating_pdf": rating_pdf,
        "emission_data_tonnes": emission_data_tonnes,
        "highest_emission_category": highest_emission_category,
    }
    
    # 3. Tandai bahwa kalkulasi sudah selesai
    st.session_state.calculation_done = True
    
    # 4. Paksa script untuk jalan ulang agar masuk ke blok penampilan hasil
    st.rerun()


# === BAGIAN PENAMPILAN HASIL & PEMBUATAN PDF ===
# Ini juga bagian yang direvisi total.
# Blok ini hanya berjalan JIKA kalkulasi sudah selesai.
# Tugasnya hanya MEMBACA dari memori dan MENAMPILKAN.
if st.session_state.calculation_done:
    # Ambil semua hasil dari "memori"
    res = st.session_state.results

    # --- Tampilkan Hasil di Aplikasi Streamlit ---
    st.success(f"🌍 Your estimated total carbon footprint is **{res['total_tonnes']} tonnes CO₂/year**")

    st.subheader("📉 Your Carbon Footprint Level")
    st.warning(f"Your carbon footprint rating: **{res['rating_display']} impact**")

    st.markdown("### 🔍 Breakdown by Category (in tonnes CO₂)")
    for category, value in res['emission_data_tonnes'].items():
        st.info(f"{category}: {round(value, 2)}")
    
    st.markdown("## 📊 Visualize Your Carbon Footprint")
    col_left, col_right = st.columns(2)
    with col_left:
        st.markdown("### 🥧 Pie Chart")
        fig1, ax1 = plt.subplots()
        ax1.pie(res['emission_data_tonnes'].values(), labels=res['emission_data_tonnes'].keys(), autopct='%1.1f%%', startangle=90, textprops={'color': 'black'})
        ax1.axis('equal')
        fig1.patch.set_alpha(0)  # Membuat background figure transparan
        ax1.patch.set_alpha(0)  # Membuat background axes transparan
        st.pyplot(fig1)
    with col_right:
        st.markdown("### 📈 Bar Chart")
        fig2 = px.bar(x=list(res['emission_data_tonnes'].keys()), y=list(res['emission_data_tonnes'].values()), labels={'x': 'Category', 'y': 'Tonnes CO₂'}, title="Annual Emissions by Category")
        fig2.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='black', title_font_color='black')
        fig2.update_traces(marker_color='darkblue')
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("## 🌳 Carbon Offset Suggestion")
    st.info(f"To offset your footprint, you would need to plant approximately **{res['trees_needed']} trees**.")
    st.caption("Note: One mature tree absorbs about 21 kg of CO₂ per year on average.")
    
    st.markdown("## 🌱 Lifestyle Recommendations")
    highest_emission_category = res['highest_emission_category']
    tips = {
        "Transportation": ["Cobalah menggunakan transportasi umum atau berbagi kendaraan (carpool)."], "Flights": ["Kurangi frekuensi penerbangan, terutama penerbangan internasional."],
        "Electricity": ["Gunakan lampu LED hemat energi dan cabut perangkat elektronik jika tidak digunakan."], "Diet": ["Kurangi konsumsi daging merah dan olahan."],
        "Clothing": ["Kurangi pembelian pakaian baru; pilih produk second-hand atau berkualitas tinggi agar tahan lama."], "Plastic": ["Gunakan botol dan tas belanja yang dapat digunakan ulang."],
        "Waste": ["Pisahkan sampah organik dan anorganik."]
    }
    st.subheader(f"📌 Fokus utama kamu: **{highest_emission_category}**")
    for tip in tips.get(highest_emission_category, []):
        st.markdown(f"- {tip}")

    # --- Kirim ke Google Sheets ---
    if res['name'] and res['age']:
        payload = {
            "Timestamp": datetime.now().isoformat(), "Name": res['name'], "Age": res['age'], "Total (Tonnes)": res['total_tonnes'],
            "Transport": round(res['emission_data_tonnes']['Transportation'], 2), "Flights": round(res['emission_data_tonnes']['Flights'], 2),
            "Electricity": round(res['emission_data_tonnes']['Electricity'], 2), "Diet": round(res['emission_data_tonnes']['Diet'], 2),
            "Clothing": round(res['emission_data_tonnes']['Clothing'], 2), "Plastic": round(res['emission_data_tonnes']['Plastic'], 2),
            "Waste": round(res['emission_data_tonnes']['Waste'], 2),
        }
        SHEET_BEST_URL = "https://api.sheetbest.com/sheets/c1663a28-e75f-4501-8341-c497b1b9867b"
        response = requests.post(SHEET_BEST_URL, json=payload)
        
        if response.status_code == 200:
            st.success("✅ Data successfully submitted to Google Sheet!")
        else:
            st.error("❌ Failed to submit data. Please check your Sheet.best link.")
    else:
        st.warning("Isi nama dan umur terlebih dahulu agar data bisa dikirim ke spreadsheet.")

    # --- Tombol Download PDF ---
    st.markdown("---")
    st.subheader("Download Full Report")

    # Membuat PDF di dalam memori
    pdf = PDF()
    pdf.add_page()
    pdf.chapter_title("User Information")
    pdf.chapter_body(f"Name: {res['name']}\nAge: {res['age']}\nCountry: {res['country']}")
    
    if res['photo_bytes']:
        photo_path = "temp_photo.jpg"
        with open(photo_path, "wb") as f:
            f.write(res['photo_bytes'])
        pdf.image(photo_path, w=100)
        pdf.ln(5)

    pdf.chapter_title("Total Carbon Footprint")
    pdf.chapter_body(f"{res['total_tonnes']} tonnes CO2 per year")

    pdf.chapter_title("Carbon Footprint Rating")
    pdf.chapter_body(f"Your impact rating is: {res['rating_pdf']}") # Versi PDF tanpa emoji

    pdf.chapter_title("Emission Breakdown (tonnes CO2)")
    for cat, val in res['emission_data_tonnes'].items():
        pdf.chapter_body(f"- {cat}: {round(val, 2)}")

    pdf.chapter_title("Trees Needed to Offset")
    pdf.chapter_body(f"You need approximately {res['trees_needed']} trees to offset your carbon emissions.")

    pdf.chapter_title(f"Recommended Focus Area: {highest_emission_category}")
    for tip in tips.get(highest_emission_category, []):
        pdf.chapter_body(f"- {tip}")

    # Simpan grafik untuk PDF
    pie_chart_path, bar_chart_path = "pie_chart.png", "bar_chart.png"
    fig_pie, ax_pie = plt.subplots()
    ax_pie.pie(res['emission_data_tonnes'].values(), labels=list(res['emission_data_tonnes'].keys()), autopct='%1.1f%%', startangle=90)
    ax_pie.axis('equal'); fig_pie.savefig(pie_chart_path); plt.close(fig_pie)
    
    fig_bar, ax_bar = plt.subplots(figsize=(8, 5)); ax_bar.bar(res['emission_data_tonnes'].keys(), res['emission_data_tonnes'].values(), color='skyblue')
    ax_bar.set_ylabel("Tonnes CO2"); plt.setp(ax_bar.get_xticklabels(), rotation=45, ha="right"); fig_bar.tight_layout(); fig_bar.savefig(bar_chart_path); plt.close(fig_bar)
    
    pdf.add_page(); pdf.chapter_title("Charts"); pdf.image(pie_chart_path, w=150); pdf.ln(5); pdf.image(bar_chart_path, w=150)

    # Ekspor PDF ke buffer
    pdf_output = pdf.output(dest='S').encode('latin-1')
    pdf_buffer = BytesIO(pdf_output)

    st.download_button(
        label="Download Your Report (PDF)",
        data=pdf_buffer,
        file_name=f"carbon_report_{res['name']}.pdf",
        mime="application/pdf"
    )

# === Bagian paling bawah (SUDAH BENAR) ===
st.sidebar.markdown("---")
track_future = st.sidebar.checkbox("📅 Track my monthly carbon footprint", value=False)
if track_future:
    st.sidebar.info("🔔 We'll remind you to check your carbon footprint every month! (feature coming soon)")
st.caption("📝 Emission factors are approximations. Results may vary based on lifestyle and region.")