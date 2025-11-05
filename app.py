import os
from flask import Flask, render_template, request, session
from datetime import timedelta
import random

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "heTturch9abXD3u3p08YaaWhk5AYWhy0")  # Secret key for sessions
app.permanent_session_lifetime = timedelta(days=7)

# --- Water usage data in Litres ---
WATER_DATA = {
    "Shower (per hour)": 9*60,       # 9 L per minute * 60 = 540 L/hour
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

# --- Routes ---

@app.route('/', methods=['GET'])
def index():
    """Home page with input form"""
    return render_template("index.html", water_data=WATER_DATA)

@app.route('/result', methods=['POST'])
def result():
    """Calculate total water usage and show result page"""
    total = 0
    details = []
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
    
    # Top 3 tips
    tips_list = [TIPS[a] for a, _, _ in sorted(details, key=lambda x: -x[2])[:3]]

    # Earned badges
    earned_badges = [name for name, threshold in BADGES.items() if total <= threshold]

    # Save in session for dashboard
    session['last_total'] = total
    session['last_details'] = details
    session['last_tips'] = tips_list
    session['last_badges'] = earned_badges

    return render_template("result.html", total=total, details=details, tips=tips_list, badges=earned_badges)

@app.route('/dashboard')
def dashboard():
    """Show interactive dashboard with chart, badges, quiz, and community stats"""
    total = session.get('last_total', 0)
    details = session.get('last_details', [])
    badges = session.get('last_badges', [])

    # Chart data
    labels = [d[0] for d in details]
    values = [d[2] for d in details]

    # Community stats (demo)
    community_avg = random.randint(int(total*0.8), int(total*1.2))

    # Random quiz question
    quiz_q = random.choice(QUIZ)

    return render_template("dashboard.html",
                           total=total,
                           labels=labels,
                           values=values,
                           badges=badges,
                           community_avg=community_avg,
                           quiz=quiz_q)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
