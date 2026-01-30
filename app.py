from flask import Flask, render_template, request, jsonify
from datetime import datetime
import random
app = Flask(__name__)
EXTRA_PERSON_CHARGE = 750
ROOMS = {
    "classic": {
        "name": "Classic Room",
        "price": 2500,
        "amenities": ["🛏 Double Bed", "🌀 Fan", "📺 TV", "🚿 Attached Bathroom"]
    },
    "premier": {
        "name": "Premier Room",
        "price": 4500,
        "amenities": ["🛏 Queen Bed", "❄ AC", "📶 Free WiFi", "📺 Smart TV", "🧴 Toiletries"]
    },
    "suite": {
        "name": "Suite Room",
        "price": 7500,
        "amenities": ["🛏 King Bed", "❄ AC", "📶 Free WiFi", "🍹 Mini Bar", "🌇 Balcony", "🛎 24/7 Service"]
    }
}
user = {"step": "name"}
@app.route("/")
def index():
    return render_template("index.html")
@app.route("/chat", methods=["POST"])
def chat():
    msg = request.json["message"].strip()
    year = datetime.now().year
    # NAME
    if user["step"] == "name":
        if not msg.replace(" ", "").isalpha():
            return jsonify({"reply": "❌ Invalid name. Use only alphabets."})
        user["name"] = msg
        user["step"] = "phone"
        return jsonify({"reply": "📞 Enter your 10-digit phone number:"})
    # PHONE
    if user["step"] == "phone":
        if not msg.isdigit() or len(msg) != 10:
            return jsonify({"reply": "❌ Phone number must be exactly 10 digits."})
        user["phone"] = msg
        user["step"] = "checkin"
        return jsonify({"reply": "📅 Select Check-in date (YYYY-MM-DD):", "calendar": True})
    # CHECK-IN
    if user["step"] == "checkin":
        try:
            d = datetime.strptime(msg, "%Y-%m-%d")
            if d.year != year:
                return jsonify({"reply": "❌ Only current year dates allowed."})
            user["checkin"] = d
            user["step"] = "checkout"
            return jsonify({"reply": "📅 Select Check-out date:", "calendar": True})
        except:
            return jsonify({"reply": "❌ Invalid date format."})
    # CHECK-OUT
    if user["step"] == "checkout":
        try:
            d = datetime.strptime(msg, "%Y-%m-%d")
            if d <= user["checkin"]:
                return jsonify({"reply": "❌ Check-out must be after check-in."})
            user["checkout"] = d
            user["step"] = "confirm_dates"
            nights = (d - user["checkin"]).days
            return jsonify({
                "reply": f"🗓 {nights} nights selected. Change date or Confirm?",
                "buttons": ["Change Date", "Confirm Date"]
            })
        except:
            return jsonify({"reply": "❌ Invalid date."})
    # DATE CONFIRM
    if user["step"] == "confirm_dates":
        if msg.lower() == "change date":
            user["step"] = "checkin"
            return jsonify({"reply": "📅 Re-enter Check-in date:", "calendar": True})
        user["step"] = "adults"
        return jsonify({"reply": "👨 Adults (minimum 1):"})
    # ADULTS
    if user["step"] == "adults":
        if not msg.isdigit() or int(msg) < 1:
            return jsonify({"reply": "❌ At least 1 adult required."})
        user["adults"] = int(msg)
        user["step"] = "children"
        return jsonify({"reply": "🧒 Children (0 allowed):"})
    # CHILDREN
    if user["step"] == "children":
        if not msg.isdigit() or int(msg) < 0:
            return jsonify({"reply": "❌ Invalid children count."})
        user["children"] = int(msg)
        user["step"] = "room"
        return jsonify({
            "reply": "🏨 Choose a room:",
            "rooms": ROOMS
        })
    # ROOM SELECT
    if user["step"] == "room":
        key = msg.lower()
        if key not in ROOMS:
            return jsonify({"reply": "❌ Invalid room choice."})
        user["room"] = ROOMS[key]
        nights = (user["checkout"] - user["checkin"]).days
        extra = max(0, user["adults"] - 2)
        total = (user["room"]["price"] * nights) + (extra * EXTRA_PERSON_CHARGE * nights)
        user["total"] = total
        user["step"] = "confirm_room"
        return jsonify({
            "reply": f"""
🏨 {user['room']['name']}
💰 ₹{user['room']['price']} / night
🛏 Amenities: {', '.join(user['room']['amenities'])}
➕ Extra Persons: {extra}
💵 Total: ₹{total}
""",
            "buttons": ["Change Room", "Confirm Room"]
        })
    # FINAL CONFIRM
    if user["step"] == "confirm_room":
        if msg.lower() == "change room":
            user["step"] = "room"
            return jsonify({"reply": "🏨 Choose a room:", "rooms": ROOMS})

        booking_id = "SG" + str(random.randint(10000, 99999))
        time = user["checkin"].strftime("%d %b %Y, 12:00 PM")

        user.clear()
        user["step"] = "name"

        return jsonify({
            "reply": f"""
🎉 BOOKING CONFIRMED 🎉

🆔 Booking ID: {booking_id}
📅 Check-in: {time}
💳 Payment: https://pay.example.com/{booking_id}

🪪 Please bring a valid ID proof.
🙏 Thank you for choosing us!
"""
        }) 
if __name__ == "__main__":
    app.run(debug=True)
