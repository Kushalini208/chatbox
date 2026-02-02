from flask import Flask, render_template, request, jsonify
import sqlite3
import uuid
from datetime import datetime

app = Flask(__name__)

DB_NAME = "bookings.db"



# DATABASE SETUP (AUTO CREATE)
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_id TEXT,
            name TEXT,
            phone TEXT,
            checkin TEXT,
            checkout TEXT,
            adults INTEGER,
            children INTEGER,
            room TEXT,
            total INTEGER,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()


init_db()


# HOME PAGE

@app.route("/")
def index():
    return render_template("index.html")


# SAVE BOOKING (called from JS)
@app.route("/save-booking", methods=["POST"])
def save_booking():
    data = request.json

    booking_id = "HB" + uuid.uuid4().hex[:6].upper()

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO bookings
        (booking_id, name, phone, checkin, checkout, adults, children, room, total, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        booking_id,
        data["name"],
        data["phone"],
        data["checkin"],
        data["checkout"],
        data["adults"],
        data["children"],
        data["room"],
        data["total"],
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "status": "success",
        "booking_id": booking_id
    })
# VIEW BOOKING HISTORY (browser)
@app.route("/bookings")
def view_bookings():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM bookings ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()

    html = """
    <h2>📋 Booking History</h2>
    <table border="1" cellpadding="8">
    <tr>
        <th>ID</th>
        <th>Name</th>
        <th>Phone</th>
        <th>Room</th>
        <th>Checkin</th>
        <th>Checkout</th>
        <th>Total ₹</th>
        <th>Date</th>
    </tr>
    """

    for r in rows:
        html += f"""
        <tr>
            <td>{r[1]}</td>
            <td>{r[2]}</td>
            <td>{r[3]}</td>
            <td>{r[8]}</td>
            <td>{r[4]}</td>
            <td>{r[5]}</td>
            <td>{r[9]}</td>
            <td>{r[10]}</td>
        </tr>
        """

    html += "</table>"

    return html
# RUN
if __name__ == "__main__":
    app.run(debug=True)
