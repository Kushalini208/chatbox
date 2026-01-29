from flask import Flask, render_template, request, jsonify
from datetime import datetime
import json
import os
app = Flask(__name__)
user_data = {}
EXTRA_PERSON_CHARGE = 750 
BOOKING_FILE = "bookings.json"
ROOMS = {
    "standard": {"name": "Standard Room", "price": 2500},
    "deluxe": {"name": "Deluxe Room", "price": 4500},
    "suite": {"name": "Suite Room", "price": 7500}
}
def load_bookings():
    if not os.path.exists(BOOKING_FILE):
        with open(BOOKING_FILE, "w") as f:
            json.dump([], f)
    with open(BOOKING_FILE, "r") as f:
        return json.load(f)
def save_booking(booking):
    bookings = load_bookings()
    bookings.append(booking)
    with open(BOOKING_FILE, "w") as f:
        json.dump(bookings, f, indent=4)
def generate_booking_id():
    bookings = load_bookings()
    next_id = len(bookings) + 1
    return f"SG-{str(next_id).zfill(3)}"
@app.route("/")
def home():
    return render_template("index.html")
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json or {}
    msg = data.get("message", "").strip()
    action = data.get("action", "")
    # RESET CHAT
    if action == "reset" or not user_data:
        user_data.clear()
        user_data["stage"] = "name"
        return jsonify({
            "reply": "Welcome to StayGenie 🏨\nPlease enter your name:"
        })
    # NAME
    if user_data["stage"] == "name":
        if not msg.isalpha():
            return jsonify({"reply": "❌ Enter a valid name (letters only):"})
        user_data["name"] = msg
        user_data["stage"] = "phone"
        return jsonify({"reply": f"Hi {msg}! Enter your 10-digit phone number 📞:"})
    # PHONE
    if user_data["stage"] == "phone":
        if not msg.isdigit() or len(msg) != 10:
            return jsonify({"reply": "❌ Invalid phone number. Enter again:"})
        user_data["phone"] = msg
        user_data["stage"] = "checkin"
        return jsonify({"reply": "Enter Check-in Date (YYYY-MM-DD):"})
    # CHECK-IN
    if user_data["stage"] == "checkin":
        try:
            checkin = datetime.strptime(msg, "%Y-%m-%d")
            user_data["checkin"] = checkin
            user_data["stage"] = "checkout"
            return jsonify({"reply": "Enter Check-out Date (YYYY-MM-DD):"})
        except:
            return jsonify({"reply": "❌ Invalid date format. Use YYYY-MM-DD"})
    # CHECK-OUT
    if user_data["stage"] == "checkout":
        try:
            checkout = datetime.strptime(msg, "%Y-%m-%d")
            if checkout <= user_data["checkin"]:
                return jsonify({"reply": "❌ Check-out must be after Check-in date:"})
            user_data["checkout"] = checkout
            nights = (checkout - user_data["checkin"]).days
            user_data["nights"] = nights
            user_data["stage"] = "date_confirm"
            return jsonify({
                "reply": f"🗓 Your stay is for {nights} night(s).\nDo you want to continue or change dates?",
                "date_confirm": True
            })
        except:
            return jsonify({"reply": "❌ Invalid date format. Use YYYY-MM-DD"})
    # CHANGE DATES
    if action == "change_dates":
        user_data["stage"] = "checkin"
        return jsonify({"reply": "Enter new Check-in Date (YYYY-MM-DD):"})
    # DATE CONFIRM → CONTINUE
    if action == "confirm_dates" and user_data["stage"] == "date_confirm":
        user_data["stage"] = "adults"
        return jsonify({"reply": "Enter number of adults:"})
    # ADULTS
    if user_data["stage"] == "adults":
        if not msg.isdigit() or int(msg) < 1:
            return jsonify({"reply": "❌ Adults must be at least 1:"})
        user_data["adults"] = int(msg)
        user_data["stage"] = "children"
        return jsonify({"reply": "Enter number of children (0 if none):"})
    # CHILDREN
    if user_data["stage"] == "children":
        if not msg.isdigit() or int(msg) < 0:
            return jsonify({"reply": "❌ Enter valid number:"})
        user_data["children"] = int(msg)
        user_data["stage"] = "room"
        return jsonify({"reply": "Select a room type:", "rooms": ROOMS})
    # CHANGE ROOM
    if action == "change_room":
        user_data["stage"] = "room"
        return jsonify({"reply": "Select a room type:", "rooms": ROOMS})
    # ROOM SELECTION
    if action == "select_room":
        room = ROOMS[msg]
        user_data["room"] = msg
        nights = user_data["nights"]
        people = user_data["adults"] + user_data["children"]
        extra_people = max(0, people - 2)
        room_cost = room["price"] * nights
        extra_cost = extra_people * EXTRA_PERSON_CHARGE * nights
        total = room_cost + extra_cost
        user_data["total"] = total
        reply = (
            f"🏨 {room['name']}\n\n"
            f"Price per night: ₹{room['price']}\n"
            f"Nights: {nights}\n"
            f"Room cost: ₹{room_cost}\n\n"
            f"Extra persons: {extra_people} × ₹{EXTRA_PERSON_CHARGE} × {nights} nights = ₹{extra_cost}\n\n"
            f"💰 Total Amount: ₹{total}\n\n"
            f"Do you want to confirm this booking or change the room?"
        )
        return jsonify({
            "reply": reply,
            "room_confirm": True
        })
    # FINAL CONFIRM BOOKING
    if action == "confirm_booking":
        room = ROOMS[user_data["room"]]
        booking_id = generate_booking_id()
        booking_data = {
            "booking_id": booking_id,
            "name": user_data["name"],
            "phone": user_data["phone"],
            "room": room["name"],
            "checkin": user_data["checkin"].strftime("%Y-%m-%d"),
            "checkout": user_data["checkout"].strftime("%Y-%m-%d"),
            "nights": user_data["nights"],
            "total_amount": user_data["total"]
        }
        save_booking(booking_data)
        reply = (
            f"🎉 Booking Confirmed!\n\n"
            f"Booking ID: {booking_id}\n"
            f"Guest: {user_data['name']}\n"
            f"Room: {room['name']}\n"
            f"Check-in: {booking_data['checkin']}\n"
            f"Check-out: {booking_data['checkout']}\n"
            f"Nights: {booking_data['nights']}\n"
            f"Total Amount: ₹{booking_data['total_amount']}\n\n"
            f"Please proceed to payment:\n"
            f"https://rzp.io/l/demo-payment"
        )
        return jsonify({
            "reply": reply,
            "payment": "https://rzp.io/l/demo-payment"
        })
    return jsonify({"reply": "⚠ Something went wrong. Please refresh and start again."})
if __name__ == "__main__":
    app.run(debug=True)
