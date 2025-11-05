import os
from flask import Flask, render_template, request, session
from datetime import timedelta
import random

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "heTturch9abXD3u3p08YaaWhk5AYWhy0")
app.permanent_session_lifetime = timedelta(days=7)

# --- Water usage data in Litres ---
WATER_DATA = {
    "Shower (per hour)": 9*60,
    "Washing machine (per load)": 70,
    "Toilet flush (per flush)": 6,
    "1 kg Rice": 2500,
    "1 kg Chicken": 4300,
    "1 Glass Milk": 200,
    "1 Cup Tea": 30
}

# --- Tips ---
TIPS = {
    "Shower (per hour)": "Take shorter showers or use a low-flow showerhead.",
    "Washing machine (per load)": "Use full loads and water-efficient settings.",
    "Toilet flush (per flush)": "Install dual-flush or low-flow toilets.",
    "1 kg Rice": "Try millets or wheat once a week.",
    "1 kg Chicken": "Replace chicken with lentils or beans.",
    "1 Glass Milk": "Try plant-based milk occasionally.",
    "1 Cup Tea": "Reuse tea leaves or reduce waste."
}

# --- Badges ---
BADGES = {
    "Bronze Saver": 500,
    "Silver Saver": 2000,
    "Gold Saver": 5000,
    "Platinum Saver": 10000
}

# --- Mini Quiz ---
QUIZ = [
    {"q": "Which food uses more water: 1 kg Rice or 1 kg Chicken?", "a": "Chicken"},
    {"q": "How much water is saved by using a low-flow showerhead per hour?", "a": "up to 50%"},
    {"q": "True or False: Flushing toilets uses more water than one shower.", "a": "False"}
]

@app.route('/', methods=['GET'])
def index():
    return render_template("index.html", water_data=WATER_DATA)

@app.route('/result', methods=['POST'])
def result():
    total = 0
    details = []

    # Standard activities
    for activity, value in WATER_DATA.items():
        qty_str = request.form.get(activity, '0')
        try:
            qty = float(qty_str)
        except ValueError:
            qty = 0
        if qty > 0:
            used = qty * value
            total += used
            details.append((activity, qty, used))

    # Other activity
    other_name = request.form.get("other_activity_name", "").strip()
    try:
        other_value = float(request.form.get("other_activity_value", 0))
        other_qty = float(request.form.get("other_activity_qty", 0))
    except ValueError:
        other_value = 0
        other_qty = 0

    if other_name and other_value > 0 and other_qty > 0:
        used = other_value * other_qty
        total += used
        details.append((other_name, other_qty, used))
        TIPS[other_name] = "Try to reduce water use for this activity if possible."

    # Top 3 tips
    tips_list = [TIPS[a] for a, _, _ in sorted(details, key=lambda x: -x[2])[:3]]

    # Earned badge logic (smaller water = higher badge)
    earned_badge = None
    for name, threshold in sorted(BADGES.items(), key=lambda x: x[1]):
        if total <= threshold:
            earned_badge = name
            break

    # Save session for dashboard
    session['last_total'] = total
    session['last_details'] = details
    session['last_tips'] = tips_list
    session['last_badge'] = earned_badge

    return render_template("result.html", total=total, details=details, tips=tips_list, badge=earned_badge)

@app.route('/dashboard')
def dashboard():
    total = session.get('last_total', 0)
    details = session.get('last_details', [])
    badge = session.get('last_badge', None)

    labels = [d[0] for d in details]
    values = [d[2] for d in details]

    # Random community average
    community_avg = random.randint(int(total*0.8), int(total*1.2))

    # Random quiz
    quiz_q = random.choice(QUIZ)

    return render_template("dashboard.html",
                           total=total,
                           labels=labels,
                           values=values,
                           badge=badge,
                           community_avg=community_avg,
                           quiz=quiz_q)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
