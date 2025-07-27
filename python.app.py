import streamlit as st
import pandas as pd
import random
import matplotlib.pyplot as plt
from fpdf import FPDF
import tempfile
import os

# ------------------ CSS ------------------
def set_custom_css():
    st.markdown("""
    <style>
    body { background-color: #f4f4f9; }
    .main { display: flex; flex-direction: column; align-items: center; }
    .stForm { background-color: #ffffff; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); padding: 20px; margin-top: 20px; }
    .stButton button { background-color: #007bff; color: white; border: none; border-radius: 5px; padding: 10px 20px; }
    .stButton button:hover { background-color: #0056b3; }
    .stSelectbox, .stSlider, .stTextInput { margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# ------------------ Calculations ------------------
def calculate_bmi(weight, height):
    height_m = height / 100
    return weight / (height_m ** 2)

def interpret_bmi(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal weight"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"

def calculate_bmr(weight, height, age, gender):
    return 10 * weight + 6.25 * height - 5 * age + (5 if gender == "Male" else -161)

def calculate_tdee(bmr, activity_level):
    factors = {
        "Sedentary": 1.2,
        "Lightly Active": 1.375,
        "Moderately Active": 1.55,
        "Very Active": 1.725,
        "Extra Active": 1.9
    }
    return bmr * factors.get(activity_level, 1.2)

def calculate_macros(tdee):
    return round(0.2 * tdee / 4), round(0.3 * tdee / 9), round(0.5 * tdee / 4)

# ------------------ Visuals ------------------
def plot_macros(protein, fat, carbs):
    fig, ax = plt.subplots()
    ax.pie([protein, fat, carbs], labels=["Protein", "Fat", "Carbs"],
           autopct='%1.1f%%', startangle=90, colors=["#ff9999", "#66b3ff", "#99ff99"])
    ax.set_title("Macronutrient Distribution")
    st.pyplot(fig)

# ------------------ PDF Generator ------------------
def generate_pdf(name, city, tdee, protein, fat, carbs, bmi, bmi_category, df):
    pdf = FPDF()
    pdf.add_page()

    # Logo
    logo_path = "Final Logo 360.png"
    if os.path.exists(logo_path):
        pdf.image(logo_path, x=80, y=10, w=50)
        pdf.ln(30)  # Space after logo

    # Title and Subheader
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "TaskMaker AI - Personalized 7-Day Indian Diet Planner", ln=True, align='C')
    pdf.set_font("Arial", 'I', 12)
    pdf.cell(200, 10, "Courtesy: TaskMaker AI", ln=True, align='C')
    pdf.ln(10)

    # User Info
    pdf.set_font("Arial", '', 12)
    pdf.cell(200, 10, f"Name: {name}    City: {city}", ln=True)
    pdf.cell(200, 10, f"Calories: {int(tdee)} kcal | Protein: {protein} g | Fat: {fat} g | Carbs: {carbs} g", ln=True)
    pdf.cell(200, 10, f"BMI: {bmi:.2f} ({bmi_category})", ln=True)
    pdf.ln(5)

    # Meal Plan Table
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(60, 10, "Day", border=1)
    pdf.cell(60, 10, "Meal", border=1)
    pdf.cell(70, 10, "Food", border=1)
    pdf.ln()

    pdf.set_font("Arial", '', 12)
    for _, row in df.iterrows():
        day = row['Day'] if row['Day'] else "-"
        meal = row['Meal']
        food = row['Food']
        pdf.cell(60, 10, day, border=1)
        pdf.cell(60, 10, meal, border=1)
        pdf.cell(70, 10, food, border=1)
        pdf.ln()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        pdf.output(tmp.name)
        return tmp.name

# ------------------ App Interface ------------------
def main():
    set_custom_css()
    st.image('Final Logo 360.png', width=150, caption='Logo')
    st.title("TaskMaker AI - Personalized 7-Day Indian Diet Planner 🍱")
    st.markdown("This App provides your nutrient requirements based on selected parameters only.")

    # --- User Input ---
    with st.form("user_input"):
        col1, col2, col3 = st.columns(3)
        with col1:
            name = st.text_input("Your Name")
            city = st.text_input("Your City")
        with col2:
            weight = st.number_input("Weight (kg)", 30, 150, 70)
            height = st.number_input("Height (cm)", 120, 250, 170)
        with col3:
            age = st.number_input("Age", 10, 100, 30)
            gender = st.selectbox("Gender", ["Male", "Female"])
        activity_level = st.selectbox("Activity Level", ["Sedentary", "Lightly Active", "Moderately Active", "Very Active", "Extra Active"])
        blood_glucose = st.slider("Blood Glucose Level (mg/dL)", 70, 250, 100)
        submitted = st.form_submit_button("🔍 Calculate My Nutrition")

    if submitted:
        bmr = calculate_bmr(weight, height, age, gender)
        tdee = calculate_tdee(bmr, activity_level)
        protein, fat, carbs = calculate_macros(tdee)
        bmi = calculate_bmi(weight, height)
        bmi_category = interpret_bmi(bmi)

        st.session_state.update({
            "name": name, "city": city,
            "tdee": tdee, "protein": protein, "fat": fat, "carbs": carbs,
            "bmi": bmi, "bmi_category": bmi_category
        })

    if "tdee" in st.session_state:
        st.subheader("🧮 Your Daily Nutritional Requirements")
        st.write(f"**Calories:** {int(st.session_state['tdee'])} kcal")
        st.write(f"**Protein:** {st.session_state['protein']} g | Fat: {st.session_state['fat']} g | Carbs: {st.session_state['carbs']} g")
        st.write(f"**BMI:** {st.session_state['bmi']:.2f} → *{st.session_state['bmi_category']}*")
        plot_macros(st.session_state['protein'], st.session_state['fat'], st.session_state['carbs'])

        # --- Preferences ---
        st.subheader("🍛 Select Your Meal Preferences")
        region = st.selectbox("Preferred Region", ["North", "South", "East", "West"])
        diet_type = st.selectbox("Diet Type", ["Vegetarian", "Non-Vegetarian"])

        regional_foods = {
            "North": {"Breakfast": ["Paratha", "Poha", "Chana", "Aloo Puri"], "Lunch": ["Dal", "Paneer", "Veg Curry", "Chicken"], "Dinner": ["Dal", "Mix Veg", "Curd", "Khichdi"]},
            "South": {"Breakfast": ["Idli", "Dosa", "Uttapam", "Upma"], "Lunch": ["Sambar", "Rasam", "Veg Poriyal", "Chicken Curry"], "Dinner": ["Sambar", "Vegetable Stew", "Curd"]},
            "East": {"Breakfast": ["Luchi", "Cholar Dal", "Puffed Rice"], "Lunch": ["Dal", "Vegetable Curry", "Fish Curry"], "Dinner": ["Dal", "Potato Curry", "Curd"]},
            "West": {"Breakfast": ["Thepla", "Methi Paratha", "Poha"], "Lunch": ["Dal", "Veg Kolhapuri", "Chicken Curry"], "Dinner": ["Bhindi", "Dal", "Curd"]}
        }

        base_items = {"Breakfast": ["Tea/Milk"], "Lunch": ["Rice/Roti"], "Dinner": ["Rice/Roti"]}
        meal_categories = {meal: base_items[meal] + regional_foods[region][meal] for meal in ["Breakfast", "Lunch", "Dinner"]}
        if diet_type == "Vegetarian":
            for meal in meal_categories:
                meal_categories[meal] = [item for item in meal_categories[meal] if item not in ["Chicken", "Fish Curry", "Mutton", "Egg"]]

        selected_meals = {meal: st.multiselect(f"{meal} Options", options, default=options[:2]) for meal, options in meal_categories.items()}

        # --- Generate Plan ---
        if st.button("📅 Generate Weekly Meal Plan"):
            plan = []
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            for day in days:
                for meal in ["Breakfast", "Lunch", "Dinner"]:
                    fixed = base_items[meal]
                    variable = random.sample(selected_meals[meal], min(2, len(selected_meals[meal])))
                    plan.append({
                        "Day": day if meal == "Breakfast" else "",
                        "Meal": meal,
                        "Food": ", ".join(fixed + variable)
                    })

            df = pd.DataFrame(plan)
            st.subheader("📋 Your 7-Day Personalized Diet Plan")
            st.dataframe(df, use_container_width=True)

            pdf_path = generate_pdf(st.session_state['name'], st.session_state['city'],
                                    st.session_state['tdee'], st.session_state['protein'],
                                    st.session_state['fat'], st.session_state['carbs'],
                                    st.session_state['bmi'], st.session_state['bmi_category'], df)
            with open(pdf_path, "rb") as f:
                st.download_button("📥 Download Diet Plan PDF", f, file_name="diet_plan.pdf")
            os.remove(pdf_path)

# ------------------ Run ------------------
if __name__ == "__main__":
    main()
