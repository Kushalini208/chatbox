const chatBox = document.getElementById("chat-box");
const input = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");
let stage = "name";
let userData = {};
// UI HELPERS
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
function clearInput() {
    input.value = "";
}
// TYPING ANIMATION
function botTyping(callback) {
    const typing = document.createElement("div");
    typing.className = "bot-message typing";
    typing.innerText = "Typing...";
    chatBox.appendChild(typing);

    setTimeout(() => {
        typing.remove();
        callback();
    }, 600);
}
// BUTTON HELPER
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
}
// MAIN FLOW
function handleUserInput(text) {
    if (!text) return;
    addUserMessage(text);
    clearInput();
    switch (stage) {
        //NAME
        case "name":
            if (!/^[A-Za-z ]+$/.test(text)) {
                botTyping(() => addBotMessage("❌ Name must contain only alphabets.\nTry again:"));
                return;
            }
            userData.name = text;
            stage = "phone";
            botTyping(() => addBotMessage("📞 Enter your 10-digit phone number:"));
            break;
        //PHONE
        case "phone":
            if (!/^\d{10}$/.test(text)) {
                botTyping(() => addBotMessage("❌ Must be exactly 10 digits."));
                return;
            }
            userData.phone = text;
            stage = "checkin";
            botTyping(() => {
                addBotMessage("📅 Select Check-in date:");
                showDatePicker("checkin");
            });
            break;
        //CHECKIN
        case "checkin":
            userData.checkin = text;
            stage = "checkout";
            botTyping(() => {
                addBotMessage("📅 Select Check-out date:");
                showDatePicker("checkout");
            });
            break;
        //CHECKOUT
        case "checkout":
            userData.checkout = text;
            stage = "confirm_dates";

            botTyping(() => {
                addBotMessage(
                    `🗓️ Check-in: ${userData.checkin}\nCheck-out: ${userData.checkout}\n\nChange dates?`
                );
                showButtons([
                    { label: "Change Date", value: "change_date" },
                    { label: "Confirm Date", value: "confirm_date" }
                ]);
            });
            break;
        //DATE CONFIRM
        case "confirm_dates":
            if (text === "change_date") {
                stage = "checkin";
                showDatePicker("checkin");
            } else {
                stage = "adults";
                botTyping(() => addBotMessage("👨 Number of adults (min 1):"));
            }
            break;
        //ADULTS
        case "adults":
            if (isNaN(text) || Number(text) < 1) {
                botTyping(() => addBotMessage("❌ Must be at least 1 adult."));
                return;
            }
            userData.adults = Number(text);
            stage = "children";
            botTyping(() => addBotMessage("👶 Number of children (0 allowed):"));
            break;
        //CHILDREN
        case "children":
            userData.children = Number(text) || 0;
            stage = "room";
            showRoomOptions();
            break;
        //ROOM
        case "room":
            userData.room = text;
            stage = "confirm_room";
            calculateAndShowSummary();
            break;
        //FINAL CONFIRM
        case "confirm_room":
            if (text === "change_room") {
                stage = "room";
                showRoomOptions();
            } else {
                confirmBooking();
            }
            break;
    }
}
// DATE PICKER
function showDatePicker(type) {
    const div = document.createElement("div");
    div.className = "bot-message";
    const inputDate = document.createElement("input");
    inputDate.type = "date";
    inputDate.onchange = () => handleUserInput(inputDate.value);
    div.appendChild(inputDate);
    chatBox.appendChild(div);
}
// ROOM CARDS (WITH IMAGES)
function showRoomOptions() {
    addBotMessage("🏨 Available Rooms:");

    const roomsHTML = `
        <div class="room-card" onclick="handleUserInput('classic')">
            <img src="/static/images/classic.jpg">
            <h4>Classic Room</h4>
            <p>₹2500 / night</p>
        </div>

        <div class="room-card" onclick="handleUserInput('premier')">
            <img src="/static/images/premier.jpg">
            <h4>Premier Room</h4>
            <p>₹4500 / night</p>
        </div>

        <div class="room-card" onclick="handleUserInput('suite')">
            <img src="/static/images/suite.jpg">
            <h4>Suite Room</h4>
            <p>₹7500 / night</p>
        </div>
    `;

    const div = document.createElement("div");
    div.className = "bot-message";
    div.innerHTML = roomsHTML;

    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// SUMMARY + AMENITIES
function calculateAndShowSummary() {
    const prices = {
        classic: 2500,
        premier: 4500,
        suite: 7500
    };
    const amenities = {
        classic: "🛏️ Bed, 📺 TV, 🚿 Bathroom",
        premier: "🛏️ Queen Bed, ❄️ AC, 📶 WiFi, ☕ Coffee",
        suite: "🛏️ King Bed, 🍸 Mini Bar, 🌅 Balcony, 🛁 Bathtub"
    };
    const nights =
        (new Date(userData.checkout) - new Date(userData.checkin)) /
        (1000 * 60 * 60 * 24);
    const totalGuests = userData.adults + userData.children;
    const extraPersons = Math.max(0, totalGuests - 2);
    const extraCost = extraPersons * 750 * nights;
    const total = prices[userData.room] * nights + extraCost;
    userData.nights = nights;
    userData.total = total;
    botTyping(() => {
        addBotMessage(
            `🧾 Booking Summary\n\n` +
            `Room: ${userData.room.toUpperCase()}\n` +
            `Amenities: ${amenities[userData.room]}\n` +
            `Nights: ${nights}\n` +
            `Extra Persons: ${extraPersons}\n` +
            `💰 Total: ₹${total}\n\nConfirm booking?`
        );

        showButtons([
            { label: "Change Room", value: "change_room" },
            { label: "Confirm Booking", value: "confirm" }
        ]);
    });
}
// SAVE TO BACKEND
function confirmBooking() {

    fetch("/save-booking", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(userData)
    });

    addBotMessage("✅ Booking Confirmed!");
}

// SEND + ENTER
sendBtn.onclick = () => handleUserInput(input.value);
input.addEventListener("keydown", e => {
    if (e.key === "Enter") handleUserInput(input.value);
});
// AUTO START
window.onload = () => {
    botTyping(() =>
        addBotMessage("👋 Welcome to Hotel Booking Assistant!\n\nPlease enter your name:")
    );
};
