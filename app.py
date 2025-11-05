import os
from flask import Flask, render_template, request, session, redirect, url_for
from datetime import timedelta
import random

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "heTturch9abXD3u3p08YaaWhk5AYWhy0")
app.permanent_session_lifetime = timedelta(days=7)

# --- Water usage data (base rates per standard unit) ---
WATER_DATA = {
    "Shower": {"rate": 9, "unit": "L/min"},  # 9 liters per minute
    "Washing machine": {"rate": 70, "unit": "L/load"},  # 70 liters per load
    "Dishwashing": {"rate": 20, "unit": "L/load"},  # 20 liters per load
    "Gardening": {"rate": 15, "unit": "L/min"},  # 15 liters per minute
    "Car Washing": {"rate": 150, "unit": "L/wash"},  # 150 liters per wash
    "Rice": {"rate": 2500, "unit": "L/kg"},  # 2500 liters per kg
    "Chicken": {"rate": 4300, "unit": "L/kg"},  # 4300 liters per kg
    "Milk": {"rate": 200, "unit": "L/glass"},  # 200 liters per glass (250ml)
    "Tea": {"rate": 30, "unit": "L/cup"}  # 30 liters per cup (250ml)
}

# Conversion factors
UNIT_CONVERSIONS = {
    # Volume conversions
    'ml': 0.001, 'l': 1, 'L': 1, 'liter': 1, 'liters': 1, 'litre': 1, 'litres': 1,
    'cup': 0.25, 'cups': 0.25, 'glass': 0.25, 'glasses': 0.25,
    'gallon': 3.785, 'gallons': 3.785,
    
    # Weight conversions  
    'g': 0.001, 'gm': 0.001, 'gram': 0.001, 'grams': 0.001,
    'kg': 1, 'kilo': 1, 'kilos': 1, 'kilogram': 1, 'kilograms': 1,
    
    # Time conversions
    'min': 1, 'mins': 1, 'minute': 1, 'minutes': 1,
    'hour': 60, 'hours': 60, 'hr': 60, 'hrs': 60,
    
    # Count conversions
    'load': 1, 'loads': 1, 'wash': 1, 'washes': 1, 'use': 1, 'uses': 1,
    'time': 1, 'times': 1
}

TIPS = {
    "Shower": "Take shorter showers or use a low-flow showerhead to save water.",
    "Washing machine": "Use full loads and water-efficient settings to reduce water usage.",
    "Dishwashing": "Use a basin for washing and rinsing, or run full dishwasher loads.",
    "Gardening": "Water plants in the early morning to reduce evaporation and use drip irrigation.",
    "Car Washing": "Use a bucket instead of a running hose, or visit a commercial car wash that recycles water.",
    "Rice": "Consider alternative grains like millets or quinoa that use less water.",
    "Chicken": "Include more plant-based proteins in your diet to reduce water footprint.",
    "Milk": "Try plant-based milk alternatives which generally have lower water footprints.",
    "Tea": "Boil only the water you need and reuse tea leaves when possible."
}

BADGES = [
    ("💎 Platinum Water Saver", 1000),
    ("🥇 Gold Water Saver", 3000),
    ("🥈 Silver Water Saver", 6000),
    ("🥉 Bronze Water Saver", 10000),
    ("💧 Water Conscious", 20000)
]

QUIZ = [
    {"q": "Which activity typically uses the most water in a household?", "a": "Showering"},
    {"q": "How much water can you save by fixing a leaky faucet per day?", "a": "Up to 20 gallons"},
    {"q": "True or False: Running the dishwasher uses less water than hand washing.", "a": "True"},
    {"q": "What's the best time to water plants to reduce evaporation?", "a": "Early morning"},
    {"q": "Which food has a higher water footprint: 1kg beef or 1kg rice?", "a": "1kg beef"}
]

def parse_quantity(input_str):
    """Parse quantity input and return (value, unit)"""
    if not input_str:
        return 0, ''
    
    input_str = str(input_str).strip()
    
    # Try to extract numeric value and unit
    value_str = ''
    unit_str = ''
    
    # Find where numbers end and text begins
    for i, char in enumerate(input_str):
        if char.isdigit() or char in '. ':
            value_str += char
        else:
            unit_str = input_str[i:].strip()
            break
    
    try:
        value = float(value_str.strip())
        unit = unit_str.lower() if unit_str else ''
        return value, unit
    except ValueError:
        return 0, ''

def convert_to_standard_unit(value, from_unit, activity_type):
    """Convert any unit to the standard unit for calculation"""
    if not from_unit or from_unit in UNIT_CONVERSIONS:
        conversion_factor = UNIT_CONVERSIONS.get(from_unit, 1)
        return value * conversion_factor
    else:
        # If unit not recognized, assume it's already in standard unit
        return value

@app.route('/', methods=['GET'])
def index():
    return render_template("index.html", water_data=WATER_DATA)

@app.route('/result', methods=['POST'])
def result():
    total = 0
    details = []

    # Process standard activities
    for activity, data in WATER_DATA.items():
        base_rate = data["rate"]
        standard_unit = data["unit"]
        
        # Get quantity input
        qty_input = request.form.get(f"{activity}_qty", '').strip()
        frequency_input = request.form.get(f"{activity}_freq", '1').strip()
        
        if qty_input:
            # Parse quantity and unit
            qty_value, qty_unit = parse_quantity(qty_input)
            freq_value, freq_unit = parse_quantity(frequency_input)
            
            if qty_value > 0:
                # Convert quantity to standard units
                if activity in ["Shower", "Gardening"]:
                    # Time-based activities - convert to minutes
                    qty_standard = convert_to_standard_unit(qty_value, qty_unit, "time")
                    water_used = qty_standard * base_rate * freq_value
                    display_qty = f"{qty_value} {qty_unit if qty_unit else 'min'}"
                    
                elif activity in ["Rice", "Chicken"]:
                    # Weight-based activities - convert to kg
                    qty_standard = convert_to_standard_unit(qty_value, qty_unit, "weight")
                    water_used = qty_standard * base_rate * freq_value
                    display_qty = f"{qty_value} {qty_unit if qty_unit else 'kg'}"
                    
                elif activity in ["Milk", "Tea"]:
                    # Volume-based activities - convert to standard servings
                    qty_standard = convert_to_standard_unit(qty_value, qty_unit, "volume")
                    water_used = qty_standard * base_rate * freq_value
                    display_qty = f"{qty_value} {qty_unit if qty_unit else 'serving'}"
                    
                else:
                    # Other activities (count-based)
                    qty_standard = convert_to_standard_unit(qty_value, qty_unit, "count")
                    water_used = qty_standard * base_rate * freq_value
                    display_qty = f"{qty_value} {qty_unit if qty_unit else 'use'}"
                
                if freq_value > 1:
                    display_qty += f" × {freq_value} times"
                
                total += water_used
                details.append((activity, display_qty, round(water_used, 1)))

    # Process other activity
    other_name = request.form.get("other_activity_name", "").strip()
    other_qty_input = request.form.get("other_activity_qty", "").strip()
    other_unit = request.form.get("other_activity_unit", "").strip()
    
    if other_name and other_qty_input:
        other_qty_value, detected_unit = parse_quantity(other_qty_input)
        # Use detected unit if no unit specified, otherwise use specified unit
        final_unit = detected_unit if detected_unit else other_unit.lower()
        
        if other_qty_value > 0:
            # For other activities, we need the water usage rate
            other_rate_input = request.form.get("other_activity_rate", "0").strip()
            other_rate_value, other_rate_unit = parse_quantity(other_rate_input)
            
            if other_rate_value > 0:
                # Convert both quantity and rate to liters
                qty_liters = convert_to_standard_unit(other_qty_value, final_unit, "volume")
                rate_liters = convert_to_standard_unit(other_rate_value, other_rate_unit, "volume")
                water_used = qty_liters * rate_liters
                
                display_qty = f"{other_qty_value} {final_unit if final_unit else 'unit'}"
                if other_rate_unit:
                    display_qty += f" ({other_rate_value} {other_rate_unit} each)"
                
                total += water_used
                details.append((other_name, display_qty, round(water_used, 1)))
                TIPS[other_name] = "Consider ways to reduce water usage for this activity."

    # Generate top 3 tips based on highest water usage activities
    if details:
        top_activities = sorted(details, key=lambda x: x[2], reverse=True)[:3]
        tips_list = []
        for activity, _, _ in top_activities:
            if activity in TIPS:
                tips_list.append(TIPS[activity])
        
        # Add general tips if needed
        general_tips = [
            "Fix leaky faucets and pipes promptly.",
            "Install water-efficient fixtures and appliances.",
            "Collect rainwater for gardening and outdoor use."
        ]
        while len(tips_list) < 3:
            tips_list.append(general_tips[len(tips_list)])
    else:
        tips_list = [
            "Start tracking your water usage to identify savings opportunities.",
            "Small changes in daily habits can lead to significant water savings.",
            "Consider installing water-efficient appliances and fixtures."
        ]

    # Calculate badge
    earned_badge = "🌍 Water Warrior"
    for name, threshold in BADGES:
        if total <= threshold:
            earned_badge = name
            break

    # Save session for dashboard
    session.permanent = True
    session['last_total'] = total
    session['last_details'] = details
    session['last_tips'] = tips_list
    session['last_badge'] = earned_badge

    return render_template("result.html", 
                         total=total, 
                         details=details, 
                         tips=tips_list, 
                         badge=earned_badge)

@app.route('/dashboard')
def dashboard():
    total = session.get('last_total', 0)
    details = session.get('last_details', [])
    badge = session.get('last_badge', "💧 Water Conscious")

    # Prepare chart data
    if details:
        labels = [d[0] for d in details]
        values = [d[2] for d in details]
    else:
        labels = ['Shower', 'Washing machine', 'Gardening']
        values = [540, 140, 450]

    community_avg = random.randint(int(total * 0.7), int(total * 1.3)) if total > 0 else 2500
    quiz = random.choice(QUIZ)

    return render_template("dashboard.html",
                         total=total,
                         labels=labels,
                         values=values,
                         badge=badge,
                         community_avg=community_avg,
                         quiz=quiz)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)