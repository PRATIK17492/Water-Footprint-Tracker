import os
from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from datetime import timedelta, datetime, date
import random
import json

app = Flask(__name__)
app.secret_key = "your_secret_key_here"
app.permanent_session_lifetime = timedelta(days=7)

# --- Enhanced Water usage data ---
WATER_DATA = {
    "cooking": {
        "Rice Cooking": {"rate": 3, "unit": "L/cup", "icon": "utensils", "description": "Water used for cooking rice"},
        "Vegetable Cooking": {"rate": 2, "unit": "L/kg", "icon": "carrot", "description": "Water for boiling vegetables"},
        "Meat Cooking": {"rate": 4, "unit": "L/kg", "icon": "drumstick-bite", "description": "Water for cooking meat"},
        "Tea Making": {"rate": 0.5, "unit": "L/cup", "icon": "mug-hot", "description": "Water for making tea"},
        "Coffee Making": {"rate": 0.3, "unit": "L/cup", "icon": "coffee", "description": "Water for brewing coffee"},
        "Dish Washing": {"rate": 20, "unit": "L/load", "icon": "utensils", "description": "Manual dish washing"},
        "Food Preparation": {"rate": 5, "unit": "L/session", "icon": "knife", "description": "Washing vegetables, fruits"}
    },
    "household": {
        "Floor Cleaning": {"rate": 10, "unit": "L/room", "icon": "broom", "description": "Mopping floors"},
        "Gardening": {"rate": 15, "unit": "L/min", "icon": "leaf", "description": "Watering garden plants"},
        "Plant Watering": {"rate": 2, "unit": "L/plant", "icon": "seedling", "description": "Watering indoor plants"},
        "House Cleaning": {"rate": 50, "unit": "L/house", "icon": "home", "description": "General house cleaning"},
        "Pet Care": {"rate": 5, "unit": "L/pet", "icon": "paw", "description": "Water for pets"},
        "Window Cleaning": {"rate": 3, "unit": "L/window", "icon": "window-restore", "description": "Cleaning windows"}
    },
    "washing": {
        "Car Washing": {"rate": 150, "unit": "L/wash", "icon": "car", "description": "Washing car with hose/bucket"},
        "Motorcycle Washing": {"rate": 50, "unit": "L/wash", "icon": "motorcycle", "description": "Washing motorcycle"},
        "Bicycle Washing": {"rate": 10, "unit": "L/wash", "icon": "bicycle", "description": "Washing bicycle"},
        "Yard Cleaning": {"rate": 30, "unit": "L/area", "icon": "tree", "description": "Cleaning yard with water"},
        "Outdoor Furniture": {"rate": 15, "unit": "L/item", "icon": "chair", "description": "Cleaning outdoor furniture"}
    },
    "bathroom": {
        "Shower": {"rate": 9, "unit": "L/min", "icon": "shower", "description": "Taking shower"},
        "Bath": {"rate": 80, "unit": "L/bath", "icon": "bath", "description": "Taking bath in tub"},
        "Toilet Flush": {"rate": 6, "unit": "L/flush", "icon": "toilet", "description": "Flushing toilet"},
        "Teeth Brushing": {"rate": 2, "unit": "L/time", "icon": "tooth", "description": "Brushing teeth with tap running"},
        "Hand Washing": {"rate": 1, "unit": "L/wash", "icon": "hands-wash", "description": "Washing hands"},
        "Face Washing": {"rate": 3, "unit": "L/wash", "icon": "user", "description": "Washing face"}
    },
    "laundry": {
        "Washing Machine": {"rate": 70, "unit": "L/load", "icon": "tshirt", "description": "Machine washing clothes"},
        "Hand Washing Clothes": {"rate": 30, "unit": "L/load", "icon": "hands", "description": "Hand washing clothes"},
        "Clothes Soaking": {"rate": 15, "unit": "L/load", "icon": "water", "description": "Soaking clothes before wash"},
        "Rinsing Clothes": {"rate": 20, "unit": "L/load", "icon": "tshirt", "description": "Rinsing washed clothes"}
    },
    "other": {
        "Drinking Water": {"rate": 0.5, "unit": "L/glass", "icon": "glass-whiskey", "description": "Drinking water consumption"},
        "Aquarium Maintenance": {"rate": 50, "unit": "L/tank", "icon": "fish", "description": "Aquarium water changes"},
        "Swimming Pool": {"rate": 1000, "unit": "L/week", "icon": "swimming-pool", "description": "Pool maintenance"},
        "Watering Lawn": {"rate": 20, "unit": "L/m²", "icon": "grass", "description": "Lawn watering"}
    }
}

# Enhanced badge system with more badges
BADGE_SYSTEM = {
    "water_saver": {
        "name": "💧 Water Saver",
        "description": "Save more than 30% water compared to average",
        "condition": lambda stats: stats.get('water_saved_percentage', 0) > 30,
        "color": "#00bcd4",
        "icon": "tint"
    },
    "frequent_tracker": {
        "name": "📊 Active Tracker", 
        "description": "Track water usage for 7+ consecutive days",
        "condition": lambda stats: stats.get('consecutive_days', 0) >= 7,
        "color": "#3498db",
        "icon": "chart-line"
    },
    "category_explorer": {
        "name": "🔍 Category Explorer",
        "description": "Use all 6 activity categories at least once",
        "condition": lambda stats: len(stats.get('used_categories', [])) >= 6,
        "color": "#9b59b6",
        "icon": "compass"
    },
    "conservation_hero": {
        "name": "🌍 Conservation Hero",
        "description": "Save over 5000 liters of water total",
        "condition": lambda stats: stats.get('total_water_saved', 0) > 5000,
        "color": "#e74c3c",
        "icon": "globe-americas"
    },
    "smart_shopper": {
        "name": "🛒 Smart Shopper",
        "description": "Use water-efficient appliances in 3+ categories",
        "condition": lambda stats: stats.get('efficient_categories', 0) >= 3,
        "color": "#f39c12",
        "icon": "shopping-cart"
    },
    "early_adopter": {
        "name": "🚀 Early Adopter",
        "description": "Use the app within first week of signing up",
        "condition": lambda stats: stats.get('days_since_signup', 0) <= 7,
        "color": "#2ecc71",
        "icon": "rocket"
    },
    "weekend_warrior": {
        "name": "⚡ Weekend Warrior",
        "description": "Complete tracking on both weekend days",
        "condition": lambda stats: stats.get('weekend_tracking', False),
        "color": "#e84393",
        "icon": "bolt"
    },
    "habit_master": {
        "name": "🎯 Habit Master",
        "description": "Maintain consistent tracking for 30 days",
        "condition": lambda stats: stats.get('consistent_days', 0) >= 30,
        "color": "#00cec9",
        "icon": "bullseye"
    },
    "eco_warrior": {
        "name": "🌱 Eco Warrior",
        "description": "Save 100+ liters in a single day",
        "condition": lambda stats: stats.get('max_daily_saving', 0) >= 100,
        "color": "#27ae60",
        "icon": "leaf"
    },
    "water_wizard": {
        "name": "🧙‍♂️ Water Wizard",
        "description": "Achieve 5 different badges",
        "condition": lambda stats: len(stats.get('earned_badges', [])) >= 5,
        "color": "#8e44ad",
        "icon": "hat-wizard"
    }
}

# Enhanced tips system
TIPS = {
    "cooking": {
        "Rice Cooking": "Use measured water and avoid overfilling the pot.",
        "Vegetable Cooking": "Steam vegetables instead of boiling to save water.",
        "Meat Cooking": "Use pressure cooking to reduce water and time.",
        "Tea Making": "Boil only the amount of water you need.",
        "Coffee Making": "Use exact water measurements for coffee.",
        "Dish Washing": "Use a basin instead of running water.",
        "Food Preparation": "Wash fruits and vegetables in a bowl."
    },
    "household": {
        "Floor Cleaning": "Use a mop bucket and change water only when necessary.",
        "Gardening": "Water plants in early morning or late evening.",
        "Plant Watering": "Use drip irrigation for potted plants.",
        "House Cleaning": "Collect and reuse rainwater for cleaning.",
        "Pet Care": "Use pet water bowls that minimize spillage.",
        "Window Cleaning": "Use vinegar solution and squeegee."
    },
    "washing": {
        "Car Washing": "Use a bucket instead of a hose.",
        "Motorcycle Washing": "Use a spray bottle for efficient cleaning.",
        "Bicycle Washing": "Wipe with damp cloth instead of hosing.",
        "Yard Cleaning": "Use broom instead of water hose.",
        "Outdoor Furniture": "Use damp cloth for cleaning furniture."
    },
    "bathroom": {
        "Shower": "Take shorter showers (5 minutes or less).",
        "Bath": "Take showers instead of baths when possible.",
        "Toilet Flush": "Install dual-flush toilet system.",
        "Teeth Brushing": "Turn off tap while brushing teeth.",
        "Hand Washing": "Use automatic sensor taps if possible.",
        "Face Washing": "Use a basin instead of running water."
    },
    "laundry": {
        "Washing Machine": "Wait for full loads before washing.",
        "Hand Washing Clothes": "Soak clothes before washing to reduce water.",
        "Clothes Soaking": "Reuse soaking water for plants.",
        "Rinsing Clothes": "Use efficient rinsing techniques."
    },
    "other": {
        "Drinking Water": "Store drinking water in covered containers.",
        "Aquarium Maintenance": "Reuse aquarium water for plants.",
        "Swimming Pool": "Use pool covers to reduce evaporation.",
        "Watering Lawn": "Water lawn deeply but less frequently."
    }
}

# Enhanced quiz system
QUIZ = [
    {"q": "What's the most water-efficient way to wash dishes?", "a": "Full dishwasher load"},
    {"q": "How much water can you save by fixing a leaky faucet?", "a": "Up to 20 gallons daily"},
    {"q": "True or False: Showers use less water than baths.", "a": "True"},
    {"q": "Best time to water plants to reduce evaporation?", "a": "Early morning"},
    {"q": "Which uses less water: hand washing or machine washing?", "a": "Machine washing with full load"},
    {"q": "What percentage of household water is typically used in bathrooms?", "a": "About 60-70%"},
    {"q": "How much water does a running toilet waste per day?", "a": "Up to 200 gallons"},
    {"q": "What's the water-saving benefit of low-flow showerheads?", "a": "Save 15-20 gallons per shower"}
]

# Store user history (in production, use a database)
USER_HISTORY = {}

def parse_quantity(input_str):
    """Parse quantity input and return (value, unit)"""
    if not input_str:
        return 0, ''
    
    input_str = str(input_str).strip()
    value_str = ''
    unit_str = ''
    
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

UNIT_CONVERSIONS = {
    'ml': 0.001, 'l': 1, 'L': 1, 'liter': 1, 'liters': 1,
    'cup': 0.25, 'cups': 0.25, 'glass': 0.25, 'glasses': 0.25,
    'g': 0.001, 'gm': 0.001, 'gram': 0.001, 'grams': 0.001,
    'kg': 1, 'kilo': 1, 'kilos': 1, 'kilogram': 1, 'kilograms': 1,
    'min': 1, 'mins': 1, 'minute': 1, 'minutes': 1,
    'hour': 60, 'hours': 60, 'hr': 60, 'hrs': 60,
    'load': 1, 'loads': 1, 'wash': 1, 'washes': 1,
    'time': 1, 'times': 1, 'flush': 1, 'flushes': 1
}

def convert_to_standard_unit(value, from_unit):
    """Convert any unit to liters"""
    if not from_unit or from_unit in UNIT_CONVERSIONS:
        conversion_factor = UNIT_CONVERSIONS.get(from_unit, 1)
        return value * conversion_factor
    else:
        return value

def calculate_user_stats(user_data, current_usage, category, details):
    """Calculate comprehensive user statistics for badge system"""
    stats = user_data.get('stats', {})
    
    # Update tracking dates
    today = datetime.now().date()
    if 'tracking_dates' not in stats:
        stats['tracking_dates'] = []
    
    # Convert any string dates back to date objects for processing
    processed_dates = []
    for date_item in stats['tracking_dates']:
        if isinstance(date_item, str):
            # Convert string back to date object
            try:
                processed_dates.append(datetime.strptime(date_item, '%Y-%m-%d').date())
            except ValueError:
                # If conversion fails, skip this date
                continue
        else:
            processed_dates.append(date_item)
    
    # Add today's date if not already present
    if today not in processed_dates:
        processed_dates.append(today)
    
    # Sort dates and convert back to strings for JSON serialization
    processed_dates.sort()
    stats['tracking_dates'] = [str(d) for d in processed_dates]
    
    # Calculate consecutive days
    consecutive = 1
    for i in range(1, len(processed_dates)):
        if (processed_dates[i] - processed_dates[i-1]).days == 1:
            consecutive += 1
        else:
            consecutive = 1
    stats['consecutive_days'] = consecutive
    
    # Track used categories
    if 'used_categories' not in stats:
        stats['used_categories'] = []
    
    if category not in stats['used_categories']:
        stats['used_categories'].append(category)
    
    # Track total usage and savings
    if 'total_usage' not in stats:
        stats['total_usage'] = 0
    stats['total_usage'] += current_usage
    
    # Track daily usage for trends
    if 'daily_usage' not in stats:
        stats['daily_usage'] = {}
    stats['daily_usage'][str(today)] = stats['daily_usage'].get(str(today), 0) + current_usage
    
    # Store detailed history
    if 'history' not in stats:
        stats['history'] = []
    
    stats['history'].append({
        'date': str(today),
        'category': category,
        'total_usage': current_usage,
        'details': details,
        'timestamp': datetime.now().isoformat()
    })
    
    # Calculate water saved (assuming 30% reduction from average)
    average_usage = 150  # Average daily usage in liters
    daily_saving = average_usage - current_usage
    stats['water_saved'] = daily_saving
    stats['water_saved_percentage'] = ((average_usage - current_usage) / average_usage) * 100 if average_usage > 0 else 0
    
    # Track max daily saving
    if 'max_daily_saving' not in stats:
        stats['max_daily_saving'] = 0
    stats['max_daily_saving'] = max(stats['max_daily_saving'], daily_saving)
    
    # Track total water saved
    if 'total_water_saved' not in stats:
        stats['total_water_saved'] = 0
    stats['total_water_saved'] += max(0, daily_saving)
    
    # Track days since signup
    if 'signup_date' not in stats:
        stats['signup_date'] = str(today)
    
    # Convert signup_date to date object for calculation
    try:
        signup_date = datetime.strptime(stats['signup_date'], '%Y-%m-%d').date()
        stats['days_since_signup'] = (today - signup_date).days
    except (ValueError, TypeError):
        stats['days_since_signup'] = 0
    
    # Track weekend usage
    if today.weekday() in [5, 6]:  # Saturday or Sunday
        stats['weekend_tracking'] = True
    else:
        stats['weekend_tracking'] = False
    
    # Track consistent usage (tracking at least 5 days per week)
    recent_dates = [d for d in processed_dates if (today - d).days <= 30]
    stats['consistent_days'] = len(recent_dates)
    
    # Track category-wise usage
    if 'category_usage' not in stats:
        stats['category_usage'] = {}
    stats['category_usage'][category] = stats['category_usage'].get(category, 0) + current_usage
    
    # Calculate efficiency score (0-100)
    efficiency_score = max(0, min(100, (150 - current_usage) / 150 * 100))
    stats['efficiency_score'] = efficiency_score
    
    # Track weekly and monthly usage for analytics
    week_start = today - timedelta(days=today.weekday())
    month_start = date(today.year, today.month, 1)
    
    if 'weekly_usage' not in stats:
        stats['weekly_usage'] = {}
    if 'monthly_usage' not in stats:
        stats['monthly_usage'] = {}
    
    stats['weekly_usage'][str(week_start)] = stats['weekly_usage'].get(str(week_start), 0) + current_usage
    stats['monthly_usage'][str(month_start)] = stats['monthly_usage'].get(str(month_start), 0) + current_usage
    
    # Initialize efficient categories
    if 'efficient_categories' not in stats:
        stats['efficient_categories'] = 0
    
    return stats

def get_earned_badges(user_stats):
    """Calculate which badges the user has earned"""
    earned_badges = []
    for badge_id, badge_info in BADGE_SYSTEM.items():
        try:
            if badge_info['condition'](user_stats):
                earned_badges.append({
                    'id': badge_id,
                    'name': badge_info['name'],
                    'description': badge_info['description'],
                    'color': badge_info['color'],
                    'icon': badge_info['icon']
                })
        except Exception as e:
            print(f"Error checking badge {badge_id}: {e}")
            continue
    
    # Store earned badges in stats for tracking
    user_stats['earned_badges'] = [badge['id'] for badge in earned_badges]
    
    return earned_badges

def calculate_badge_progress(badge_id, user_stats):
    """Calculate progress percentage for next badges"""
    progress_data = {
        "water_saver": min(100, (user_stats.get('water_saved_percentage', 0) / 30) * 100),
        "frequent_tracker": min(100, (user_stats.get('consecutive_days', 0) / 7) * 100),
        "category_explorer": min(100, (len(user_stats.get('used_categories', [])) / 6) * 100),
        "conservation_hero": min(100, (user_stats.get('total_water_saved', 0) / 5000) * 100),
        "smart_shopper": min(100, (user_stats.get('efficient_categories', 0) / 3) * 100),
        "early_adopter": min(100, max(0, (7 - user_stats.get('days_since_signup', 0)) / 7) * 100),
        "habit_master": min(100, (user_stats.get('consistent_days', 0) / 30) * 100),
        "weekend_warrior": 50 if user_stats.get('weekend_tracking', False) else 0,
        "eco_warrior": min(100, (user_stats.get('max_daily_saving', 0) / 100) * 100),
        "water_wizard": min(100, (len(user_stats.get('earned_badges', [])) / 5) * 100)
    }
    return progress_data.get(badge_id, 0)

def generate_weekly_trends(user_stats):
    """Generate weekly usage trends"""
    daily_usage = user_stats.get('daily_usage', {})
    if not daily_usage:
        return []
    
    # Get last 7 days of data
    trends = []
    for i in range(7):
        target_date = date.today() - timedelta(days=i)
        date_key = str(target_date)
        usage = daily_usage.get(date_key, 0)
        trends.append({
            'date': date_key,
            'usage': usage,
            'day': target_date.strftime('%a')
        })
    
    return list(reversed(trends))

def generate_category_breakdown(user_stats):
    """Generate category-wise water usage breakdown"""
    category_usage = user_stats.get('category_usage', {})
    total_usage = user_stats.get('total_usage', 1)  # Avoid division by zero
    
    breakdown = []
    for category, usage in category_usage.items():
        percentage = (usage / total_usage) * 100
        breakdown.append({
            'category': category.capitalize(),
            'usage': usage,
            'percentage': round(percentage, 1)
        })
    
    # Sort by usage descending
    breakdown.sort(key=lambda x: x['usage'], reverse=True)
    return breakdown

def generate_water_savings_insights(user_stats, current_usage, community_avg):
    """Generate insights about water savings"""
    total_saved = user_stats.get('total_water_saved', 0)
    efficiency = user_stats.get('efficiency_score', 0)
    daily_saving = user_stats.get('water_saved', 0)
    
    insights = []
    
    if total_saved > 0:
        insights.append(f"🌊 You've saved {total_saved:.0f} liters of water so far!")
    
    if efficiency > 80:
        insights.append("🎯 Excellent water efficiency! You're doing great!")
    elif efficiency > 60:
        insights.append("👍 Good water usage habits! Keep it up!")
    else:
        insights.append("💡 Some room for improvement in water efficiency.")
    
    # Compare with community average
    if current_usage < community_avg:
        savings = community_avg - current_usage
        insights.append(f"✅ You're using {savings:.1f}L less than community average today!")
    elif current_usage > community_avg:
        excess = current_usage - community_avg
        insights.append(f"💡 You're using {excess:.1f}L more than average. Try our water-saving tips!")
    
    # Add personalized insights based on usage patterns
    category_usage = user_stats.get('category_usage', {})
    if 'bathroom' in category_usage and category_usage['bathroom'] > 100:
        insights.append("🚿 Consider shorter showers to save more water.")
    
    if 'laundry' in category_usage and category_usage['laundry'] > 80:
        insights.append("👕 Try full laundry loads to optimize water usage.")
    
    if 'washing' in category_usage and category_usage['washing'] > 100:
        insights.append("🚗 Use bucket instead of hose for car washing.")
    
    return insights[:4]  # Return max 4 insights

def calculate_usage_analytics(user_stats, current_usage):
    """Calculate comprehensive usage analytics for dashboard"""
    # Weekly, monthly, yearly estimates based on current usage pattern
    weekly_estimate = current_usage * 7
    monthly_estimate = current_usage * 30
    yearly_estimate = current_usage * 365
    
    # Community averages (these would typically come from a database)
    community_weekly = 150 * 7  # 150L daily average * 7 days
    community_monthly = 150 * 30
    community_yearly = 150 * 365
    
    analytics = {
        'week': {
            'user': weekly_estimate,
            'community': community_weekly
        },
        'month': {
            'user': monthly_estimate,
            'community': community_monthly
        },
        'year': {
            'user': yearly_estimate,
            'community': community_yearly
        }
    }
    
    return analytics

def generate_personalized_suggestions(user_stats, current_usage, community_avg, category_breakdown):
    """Generate personalized water-saving suggestions"""
    suggestions = []
    
    # Basic suggestions based on usage comparison
    if current_usage > community_avg:
        excess = current_usage - community_avg
        suggestions.append(f"💧 You're using {excess:.1f}L more than average. Try reducing high-usage activities.")
    else:
        savings = community_avg - current_usage
        suggestions.append(f"🌱 Great! You're saving {savings:.1f}L compared to average. Keep it up!")
    
    # Suggestions based on category breakdown
    if category_breakdown:
        top_category = category_breakdown[0] if category_breakdown else None
        if top_category and top_category['percentage'] > 40:
            suggestions.append(f"🎯 Focus on reducing {top_category['category'].lower()} activities - they're {top_category['percentage']}% of your usage.")
    
    # Suggestions based on user stats
    if user_stats.get('consecutive_days', 0) < 3:
        suggestions.append("📊 Track your usage for a few more days to get better personalized insights.")
    
    if user_stats.get('total_water_saved', 0) > 1000:
        suggestions.append(f"🏆 Amazing! You've saved {user_stats['total_water_saved']:.0f}L total. Share your tips with others!")
    
    # General water-saving tips
    general_tips = [
        "🚿 Reduce shower time by 2 minutes to save ~18L per shower",
        "💧 Fix leaky faucets - they can waste up to 75L daily",
        "🌱 Water plants in early morning to reduce evaporation",
        "👕 Wait for full loads before running washing machine"
    ]
    
    # Add general tips if we don't have enough personalized ones
    while len(suggestions) < 4:
        tip = general_tips.pop(0) if general_tips else "Track more activities for better suggestions"
        suggestions.append(tip)
        if not general_tips:
            break
    
    return suggestions[:4]  # Return max 4 suggestions

def get_user_history(username):
    """Get user's tracking history"""
    if username in USER_HISTORY:
        return USER_HISTORY[username]
    return []

def save_user_history(username, entry):
    """Save user tracking entry to history"""
    if username not in USER_HISTORY:
        USER_HISTORY[username] = []
    USER_HISTORY[username].append(entry)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        # Auto-login for any user (no fixed credentials)
        if username and password:
            session['user'] = username
            session['logged_in'] = True
            session['user_data'] = {
                'name': username,
                'location': 'Unknown',
                'household_size': 1,
                'stats': {}
            }
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Please enter both username and password")
    
    return render_template('login.html')

@app.route('/index')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template("index.html", water_data=WATER_DATA)

@app.route('/form/<category>')
def category_form(category):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    if category not in WATER_DATA:
        return redirect(url_for('index'))
    
    return render_template("form.html", 
                         category=category, 
                         activities=WATER_DATA[category],
                         tips=TIPS.get(category, {}))

@app.route('/result', methods=['POST'])
def result():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    total = 0
    details = []
    category = request.form.get('category', '')
    
    print(f"Processing category: {category}")  # Debug
    
    # Process ALL activities from the category
    if category in WATER_DATA:
        for activity, data in WATER_DATA[category].items():
            base_rate = data["rate"]
            
            qty_input = request.form.get(f"{activity}_qty", '').strip()
            frequency_input = request.form.get(f"{activity}_freq", '1').strip()
            duration_input = request.form.get(f"{activity}_duration", '1').strip()
            
            print(f"Processing {activity}: qty='{qty_input}', freq='{frequency_input}', duration='{duration_input}'")  # Debug
            
            if qty_input:
                qty_value, qty_unit = parse_quantity(qty_input)
                freq_value, _ = parse_quantity(frequency_input)
                duration_value, _ = parse_quantity(duration_input)
                
                print(f"Parsed values: qty={qty_value}, unit='{qty_unit}', freq={freq_value}, duration={duration_value}")  # Debug
                
                if qty_value > 0:
                    # Convert to standard units and calculate
                    qty_standard = convert_to_standard_unit(qty_value, qty_unit)
                    water_used = qty_standard * base_rate * freq_value * duration_value
                    
                    print(f"Calculation: {qty_standard} * {base_rate} * {freq_value} * {duration_value} = {water_used}")  # Debug
                    
                    display_qty = f"{qty_value} {qty_unit if qty_unit else 'unit'}"
                    if freq_value > 1:
                        display_qty += f" × {freq_value}"
                    if duration_value > 1:
                        display_qty += f" for {duration_value} days"
                    
                    total += water_used
                    details.append((activity, display_qty, round(water_used, 1)))

    print(f"Final total: {total}")  # Debug
    print(f"Details: {details}")  # Debug

    # Update user statistics
    if 'user_data' in session:
        session['user_data']['stats'] = calculate_user_stats(
            session['user_data'], total, category, details
        )
        session.modified = True

    # Save to history
    if 'user' in session:
        save_user_history(session['user'], {
            'date': datetime.now().date().isoformat(),
            'category': category,
            'total': total,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })

    # Generate personalized tips
    tips_list = []
    if details:
        # Get tips for activities with highest usage
        top_activities = sorted(details, key=lambda x: x[2], reverse=True)[:3]
        for activity, _, _ in top_activities:
            if category in TIPS and activity in TIPS[category]:
                tips_list.append(TIPS[category][activity])
    
    # Add general tips if needed
    general_tips = [
        "Fix leaky faucets immediately - they can waste up to 20 gallons daily",
        "Install water-efficient fixtures and appliances",
        "Collect rainwater for gardening and cleaning purposes",
        "Use broom instead of hose for cleaning outdoor areas"
    ]
    
    while len(tips_list) < 3:
        tips_list.append(general_tips[len(tips_list) % len(general_tips)])

    # Calculate earned badges
    user_stats = session.get('user_data', {}).get('stats', {})
    earned_badges = get_earned_badges(user_stats)

    # Save session data
    session['last_total'] = total
    session['last_details'] = details
    session['last_tips'] = tips_list
    session['last_badges'] = earned_badges
    session['last_category'] = category

    return render_template("result.html", 
                         total=total, 
                         details=details, 
                         tips=tips_list, 
                         badges=earned_badges,
                         category=category)

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    total = session.get('last_total', 0)
    details = session.get('last_details', [])
    badges = session.get('last_badges', [])
    category = session.get('last_category', 'general')
    user_stats = session.get('user_data', {}).get('stats', {})

    # Prepare chart data
    if details:
        labels = [d[0] for d in details]
        values = [d[2] for d in details]
    else:
        labels = ['Shower', 'Cooking', 'Cleaning', 'Laundry', 'Drinking', 'Other']
        values = [45, 25, 30, 40, 5, 15]

    # Generate community average (dynamic based on user's usage pattern)
    community_avg = random.randint(int(total * 0.8), int(total * 1.5)) if total > 0 else 150
    quiz = random.choice(QUIZ)
    
    # Generate analytics data
    weekly_trends = generate_weekly_trends(user_stats)
    category_breakdown = generate_category_breakdown(user_stats)
    usage_analytics = calculate_usage_analytics(user_stats, total)
    water_insights = generate_water_savings_insights(user_stats, total, community_avg)
    personalized_suggestions = generate_personalized_suggestions(user_stats, total, community_avg, category_breakdown)

    # Calculate progress for next badges
    next_badges = []
    for badge_id, badge_info in BADGE_SYSTEM.items():
        if not badge_info['condition'](user_stats):
            progress = calculate_badge_progress(badge_id, user_stats)
            next_badges.append({
                'name': badge_info['name'],
                'description': badge_info['description'],
                'progress': progress,
                'icon': badge_info['icon']
            })

    # Calculate efficiency metrics
    efficiency_score = user_stats.get('efficiency_score', 0)
    water_saved_today = user_stats.get('water_saved', 0)
    total_water_saved = user_stats.get('total_water_saved', 0)

    return render_template("dashboard.html",
                         total=total,
                         labels=labels,
                         values=values,
                         badges=badges,
                         next_badges=next_badges[:4],
                         user_stats=user_stats,
                         community_avg=community_avg,
                         quiz=quiz,
                         category=category,
                         weekly_trends=weekly_trends,
                         category_breakdown=category_breakdown,
                         water_insights=water_insights,
                         efficiency_score=efficiency_score,
                         water_saved_today=water_saved_today,
                         total_water_saved=total_water_saved,
                         usage_analytics=usage_analytics,
                         personalized_suggestions=personalized_suggestions)

@app.route('/history')
def history():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    username = session.get('user')
    user_stats = session.get('user_data', {}).get('stats', {})
    history_data = user_stats.get('history', [])
    
    # Sort history by timestamp (newest first)
    history_data.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    
    # Calculate summary statistics
    total_entries = len(history_data)
    total_water_used = sum(entry.get('total_usage', 0) for entry in history_data)
    average_daily = total_water_used / total_entries if total_entries > 0 else 0
    
    # Get category distribution
    category_distribution = {}
    for entry in history_data:
        category = entry.get('category', 'unknown')
        category_distribution[category] = category_distribution.get(category, 0) + entry.get('total_usage', 0)
    
    return render_template("history.html",
                         history_data=history_data,
                         total_entries=total_entries,
                         total_water_used=total_water_used,
                         average_daily=average_daily,
                         category_distribution=category_distribution,
                         user_stats=user_stats)

@app.route('/records')
def records():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    user_stats = session.get('user_data', {}).get('stats', {})
    
    # Calculate records and achievements
    records_data = {
        'consecutive_days': user_stats.get('consecutive_days', 0),
        'total_water_saved': user_stats.get('total_water_saved', 0),
        'max_daily_saving': user_stats.get('max_daily_saving', 0),
        'efficiency_score': user_stats.get('efficiency_score', 0),
        'total_categories': len(user_stats.get('used_categories', [])),
        'total_tracking_days': len(user_stats.get('tracking_dates', [])),
        'badges_earned': len(user_stats.get('earned_badges', [])),
        'current_streak': user_stats.get('consecutive_days', 0)
    }
    
    # Calculate weekly and monthly averages
    weekly_usage = user_stats.get('weekly_usage', {})
    monthly_usage = user_stats.get('monthly_usage', {})
    
    weekly_avg = sum(weekly_usage.values()) / len(weekly_usage) if weekly_usage else 0
    monthly_avg = sum(monthly_usage.values()) / len(monthly_usage) if monthly_usage else 0
    
    return render_template("records.html",
                         records_data=records_data,
                         weekly_avg=weekly_avg,
                         monthly_avg=monthly_avg,
                         user_stats=user_stats)

@app.route('/api/usage-data')
def api_usage_data():
    """API endpoint for dynamic usage data"""
    if not session.get('logged_in'):
        return jsonify({'error': 'Not authenticated'}), 401
    
    user_stats = session.get('user_data', {}).get('stats', {})
    total = session.get('last_total', 0)
    
    analytics = calculate_usage_analytics(user_stats, total)
    
    return jsonify({
        'analytics': analytics,
        'user_stats': user_stats,
        'current_usage': total
    })

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)