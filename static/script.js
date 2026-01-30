const chatBox = document.getElementById("chat-box");
const input = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");

let stage = "name";
let userData = {};

// ---------- UI HELPERS ----------
function addBotMessage(text) {
    const div = document.createElement("div");
    div.className = "bot-message";
    div.innerHTML = text.replace(/\n/g, "<br>");
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function addUserMessage(text) {
    const div = document.createElement("div");
    div.className = "user-message";
    div.innerText = text;
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function showButtons(buttons) {
    const div = document.createElement("div");
    div.className = "bot-message";

    buttons.forEach(btn => {
        const b = document.createElement("button");
        b.innerText = btn.label;
        b.onclick = () => handleUserInput(btn.value);
        div.appendChild(b);
    });

    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function clearInput() {
    input.value = "";
}

// ---------- BOT FLOW ----------
function handleUserInput(text) {
    if (!text) return;
    addUserMessage(text);
    clearInput();

    switch (stage) {

        // ---------- NAME ----------
        case "name":
            if (!/^[A-Za-z ]+$/.test(text)) {
                addBotMessage("❌ Invalid name. Use alphabets only.\nPlease enter your name:");
                return;
            }
            userData.name = text;
            stage = "phone";
            addBotMessage("📞 Please enter your 10-digit phone number:");
            break;

        // ---------- PHONE ----------
        case "phone":
            if (!/^\d{10}$/.test(text)) {
                addBotMessage("❌ Invalid phone number.\nEnter exactly 10 digits:");
                return;
            }
            userData.phone = text;
            stage = "checkin";
            addBotMessage("📅 Select your Check-in date:");
            showDatePicker("checkin");
            break;

        // ---------- CHECK-IN ----------
        case "checkin":
            userData.checkin = text;
            stage = "checkout";
            addBotMessage("📅 Select your Check-out date:");
            showDatePicker("checkout");
            break;

        // ---------- CHECK-OUT ----------
        case "checkout":
            userData.checkout = text;
            stage = "confirm_dates";
            addBotMessage(
                `🗓️ You selected:\nCheck-in: ${userData.checkin}\nCheck-out: ${userData.checkout}\n\nDo you want to change the dates?`
            );
            showButtons([
                { label: "Change Date", value: "change_date" },
                { label: "Confirm Date", value: "confirm_date" }
            ]);
            break;

        // ---------- DATE CONFIRM ----------
        case "confirm_dates":
            if (text === "change_date") {
                stage = "checkin";
                addBotMessage("📅 Please select Check-in date again:");
                showDatePicker("checkin");
            } else {
                stage = "adults";
                addBotMessage("👨‍👩‍👧 Enter number of adults (minimum 1):");
            }
            break;

        // ---------- ADULTS ----------
        case "adults":
            if (isNaN(text) || Number(text) < 1) {
                addBotMessage("❌ Adults must be at least 1.\nEnter again:");
                return;
            }
            userData.adults = Number(text);
            stage = "children";
            addBotMessage("👶 Enter number of children (0 allowed):");
            break;

        // ---------- CHILDREN ----------
        case "children":
            if (isNaN(text) || Number(text) < 0) {
                addBotMessage("❌ Invalid number.\nEnter children count:");
                return;
            }
            userData.children = Number(text);
            stage = "room";
            showRoomOptions();
            break;

        // ---------- ROOM ----------
        case "room":
            userData.room = text;
            stage = "confirm_room";
            calculateAndShowSummary();
            break;

        // ---------- ROOM CONFIRM ----------
        case "confirm_room":
            if (text === "change_room") {
                stage = "room";
                showRoomOptions();
            } else {
                stage = "done";
                confirmBooking();
            }
            break;
    }
}

// ---------- DATE PICKER ----------
function showDatePicker(type) {
    const div = document.createElement("div");
    div.className = "bot-message";

    const inputDate = document.createElement("input");
    inputDate.type = "date";
    inputDate.onchange = () => {
        stage = type;
        handleUserInput(inputDate.value);
    };

    div.appendChild(inputDate);
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// ---------- ROOM OPTIONS ----------
function showRoomOptions() {
    addBotMessage(
        "🏨 Available Rooms:\n\n" +
        "🏠 Classic Room – ₹2500/night\n" +
        "🛏️ Premier Room – ₹4500/night\n" +
        "🏢 Suite Room – ₹7500/night\n\nSelect a room:"
    );

    showButtons([
        { label: "Classic Room", value: "classic" },
        { label: "Premier Room", value: "premier" },
        { label: "Suite Room", value: "suite" }
    ]);
}

// ---------- SUMMARY ----------
function calculateAndShowSummary() {
    const prices = { classic: 2500, premier: 4500, suite: 7500 };
    const amenities = {
        classic: "🛏️ Bed, 📺 TV, 🚿 Bathroom",
        premier: "🛏️ Queen Bed, ❄️ AC, 📶 WiFi",
        suite: "🛏️ King Bed, 🍸 Mini Bar, 🌅 Balcony"
    };

    const nights =
        (new Date(userData.checkout) - new Date(userData.checkin)) /
        (1000 * 60 * 60 * 24);

    const extraPersons = Math.max(0, userData.adults + userData.children - 2);
    const extraCost = extraPersons * 750 * nights;
    const total = prices[userData.room] * nights + extraCost;

    userData.total = total;

    addBotMessage(
        `🧾 Booking Summary\n\n` +
        `Room: ${userData.room.toUpperCase()}\n` +
        `Amenities: ${amenities[userData.room]}\n` +
        `Nights: ${nights}\n` +
        `Extra Persons: ${extraPersons}\n` +
        `💰 Total Amount: ₹${total}\n\nConfirm booking?`
    );

    showButtons([
        { label: "Change Room", value: "change_room" },
        { label: "Confirm Booking", value: "confirm" }
    ]);
}

// ---------- FINAL CONFIRM ----------
function confirmBooking() {
    const bookingId = "HB" + Math.floor(Math.random() * 100000);

    addBotMessage(
        `✅ Booking Confirmed!\n\n` +
        `🆔 Booking ID: ${bookingId}\n` +
        `📅 Check-in: ${userData.checkin} (12:00 PM)\n\n` +
        `💳 Payment Link: https://pay.example.com\n\n` +
        `📄 Please carry a valid ID proof.\n\n` +
        `🙏 Thank you for choosing us!`
    );
}

//SEND + ENTER
sendBtn.onclick = () => handleUserInput(input.value);
input.addEventListener("keydown", e => {
    if (e.key === "Enter") handleUserInput(input.value);
});

//AUTO START
window.onload = () => {
    addBotMessage("👋 Welcome to our Hotel Booking Assistant!\n\nPlease enter your full name:");
};
