from flask import Flask, render_template, request, jsonify
import psycopg2
import os
from datetime import datetime, date
import uuid

app = Flask(__name__)

#DATABASE CONNECTION
DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise Exception("DATABASE_URL not set")

conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

#CREATE TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS bookings (
    id SERIAL PRIMARY KEY,
    booking_id TEXT,
    name TEXT NOT NULL,
    phone TEXT NOT NULL,
    checkin DATE,
    checkout DATE,
    nights INT,
    adults INT,
    children INT,
    room TEXT,
    total INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

#CONSTANTS
ROOM_PRICES = {
    "classic": 2500,
    "premier": 4500,
    "suite": 7500
}

ROOM_AMENITIES = {
    "classic": ["🛏 Double Bed", "🌀 Fan", "📺 TV", "🚿 Attached Bathroom"],
    "premier": ["🛏 Queen Bed", "❄ AC", "📶 Free Wi-Fi", "📺 Smart TV", "🧴 Toiletries"],
    "suite": ["🛏 King Bed", "❄ AC", "📶 Free Wi-Fi", "🍸 Mini Bar", "🌅 Balcony", "🛎 24/7 Room Service"]
}

EXTRA_PERSON_CHARGE = 750

#SESSION DATA
user_state = {}

#ROUTES
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    msg = request.json.get("message", "").strip()
    state = user_state.get("stage", "name")

    #NAME
    if state == "name":
        if not msg.isalpha():
            return reply("❌ Invalid name. Use alphabets only.")
        user_state["name"] = msg
        user_state["stage"] = "phone"
        return reply("📞 Enter your 10-digit phone number:")

    #PHONE
    if state == "phone":
        if not msg.isdigit() or len(msg) != 10:
            return reply("❌ Phone number must be exactly 10 digits.")
        user_state["phone"] = msg
        user_state["stage"] = "checkin"
        return reply("📅 Select your Check-in date (YYYY-MM-DD):")

    #CHECKIN
    if state == "checkin":
        try:
            checkin = datetime.strptime(msg, "%Y-%m-%d").date()
            if checkin.year != date.today().year:
                raise ValueError
            user_state["checkin"] = checkin
            user_state["stage"] = "checkout"
            return reply("📅 Select your Check-out date (YYYY-MM-DD):")
        except:
            return reply("❌ Invalid date. Use current year only (YYYY-MM-DD).")

    #CHECKOUT
    if state == "checkout":
        try:
            checkout = datetime.strptime(msg, "%Y-%m-%d").date()
            if checkout <= user_state["checkin"]:
                raise ValueError
            user_state["checkout"] = checkout
            user_state["nights"] = (checkout - user_state["checkin"]).days
            user_state["stage"] = "adults"
            return reply("👨‍👩‍👧 Enter number of adults (minimum 1):")
        except:
            return reply("❌ Checkout must be after check-in.")
    #ADULTS
    if state == "adults":
        if not msg.isdigit() or int(msg) < 1:
            return reply("❌ Minimum 1 adult required.")
        user_state["adults"] = int(msg)
        user_state["stage"] = "children"
        return reply("🧒 Enter number of children (0 allowed):")
    #CHILDREN
    if state == "children":
        if not msg.isdigit() or int(msg) < 0:
            return reply("❌ Invalid number.")
        user_state["children"] = int(msg)
        user_state["stage"] = "room"
        return reply(
            "🏨 Available Rooms:\n"
            "🏠 Classic Room – ₹2500/night\n"
            "🏢 Premier Room – ₹4500/night\n"
            "🏰 Suite Room – ₹7500/night\n\n"
            "Type: classic / premier / suite"
        )
    #ROOM
    if state == "room":
        room = msg.lower()
        if room not in ROOM_PRICES:
            return reply("❌ Choose classic, premier, or suite.")
        user_state["room"] = room
        nights = user_state["nights"]
        base = ROOM_PRICES[room] * nights
        extra_people = max(0, user_state["adults"] - 2)
        extra_cost = extra_people * EXTRA_PERSON_CHARGE * nights
        total = base + extra_cost
        user_state["total"] = total
        user_state["stage"] = "confirm"
        amenities = ", ".join(ROOM_AMENITIES[room])
        return reply(
            f"📋 Booking Summary\n\n"
            f"Room: {room.upper()}\n"
            f"Amenities: {amenities}\n"
            f"Nights: {nights}\n"
            f"Extra Persons: {extra_people}\n"
            f"💰 Total Amount: ₹{total}\n\n"
            f"Type CONFIRM to proceed or CHANGE to select room again."
        )

    #CONFIRM
    if state == "confirm":
        if msg.lower() == "change":
            user_state["stage"] = "room"
            return reply("🔁 Select room again: classic / premier / suite")

        if msg.lower() == "confirm":
            booking_id = str(uuid.uuid4())[:8]

            cursor.execute("""
                INSERT INTO bookings
                (booking_id, name, phone, checkin, checkout, nights, adults, children, room, total)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                booking_id,
                user_state["name"],
                user_state["phone"],
                user_state["checkin"],
                user_state["checkout"],
                user_state["nights"],
                user_state["adults"],
                user_state["children"],
                user_state["room"],
                user_state["total"]
            ))
            conn.commit()
            user_state.clear()

            return reply(
                f"✅ Booking Confirmed!\n\n"
                f"🆔 Booking ID: {booking_id}\n"
                f"📅 Check-in: {date.today()} at 12:00 PM\n"
                f"💳 Payment link will be shared\n"
                f"🪪 Bring ID proof at check-in\n\n"
                f"Thank you for choosing us ❤️"
            )

        return reply("❌ Type CONFIRM or CHANGE")

    return reply("❌ Something went wrong. Refresh and try again.")

#HELPER
def reply(text):
    return jsonify({"reply": text})

#RUN
if __name__ == "__main__":
    app.run(debug=True)
