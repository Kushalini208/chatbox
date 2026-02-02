from flask import Flask, render_template, request, jsonify
import sqlite3
import uuid
from datetime import datetime

app = Flask(__name__)

DB_NAME = "bookings.db"

# DATABASE INIT (AUTO CREATE)
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
        nights INTEGER,
        total REAL,
        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()


init_db()
# ROUTES
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.json

    booking_id = str(uuid.uuid4())[:8]

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO bookings (
        booking_id, name, phone, checkin, checkout,
        adults, children, room, nights, total, created_at
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        booking_id,
        data.get("name"),
        data.get("phone"),
        data.get("checkin"),
        data.get("checkout"),
        data.get("adults"),
        data.get("children"),
        data.get("room"),
        data.get("nights"),
        data.get("total"),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "status": "success",
        "booking_id": booking_id
    })


@app.route("/bookings")
def view_bookings():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM bookings ORDER BY id DESC")
    rows = cursor.fetchall()

    conn.close()

    return jsonify(rows)
if __name__ == "__main__":
    app.run(debug=True)
