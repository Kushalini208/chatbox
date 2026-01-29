function sendMessage() {
    let input = document.getElementById("messageInput");
    let text = input.value.trim();
    if (text === "") return;
    addMessage(text, "user");
    input.value = "";
    fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text })
    })
    .then(res => res.json())
    .then(showBotResponse);
}
function showBotResponse(data) {
    addMessage(data.reply, "bot");
    // Switch input type for date picking
    let reply = data.reply.toLowerCase();
    if (reply.includes("check-in") || reply.includes("check in") ||
        reply.includes("check-out") || reply.includes("check out")) {
        setDateInput();
    } else {
        setTextInput();
    }
    // Date confirmation stage buttons
    if (data.date_confirm) {
        showDateConfirmButtons();
    }
    // Room selection buttons
    if (data.rooms) {
        showRoomButtons(data.rooms);
    }
    // Room confirmation buttons
    if (data.room_confirm) {
        showRoomConfirmButtons();
    }
    // Payment link
    if (data.payment) {
        addMessage("💳 Payment Link:\n" + data.payment, "bot");
    }
}
// Show room buttons
function showRoomButtons(rooms) {
    let div = document.createElement("div");
    div.className = "button-group";
    for (let key in rooms) {
        let btn = document.createElement("button");
        btn.innerText = `${rooms[key].name} ₹${rooms[key].price}/night`;
        btn.onclick = () => sendAction("select_room", key);
        div.appendChild(btn);
    }
    document.getElementById("chatMessages").appendChild(div);
    scrollBottom();
}
// After date selection → Continue / Change Dates
function showDateConfirmButtons() {
    let div = document.createElement("div");
    div.className = "button-group";
    let continueBtn = document.createElement("button");
    continueBtn.innerText = "✅ Continue";
    continueBtn.onclick = () => sendAction("confirm_dates", "");
    let changeBtn = document.createElement("button");
    changeBtn.innerText = "🔄 Change Dates";
    changeBtn.onclick = () => sendAction("change_dates", "");
    div.appendChild(continueBtn);
    div.appendChild(changeBtn);
    document.getElementById("chatMessages").appendChild(div);
    scrollBottom();
}
// After room price summary → Confirm Booking / Change Room
function showRoomConfirmButtons() {
    let div = document.createElement("div");
    div.className = "button-group";
    let confirmBtn = document.createElement("button");
    confirmBtn.innerText = "✅ Confirm Booking";
    confirmBtn.onclick = () => sendAction("confirm_booking", "");
    let changeRoomBtn = document.createElement("button");
    changeRoomBtn.innerText = "🔄 Change Room";
    changeRoomBtn.onclick = () => sendAction("change_room", "");
    div.appendChild(confirmBtn);
    div.appendChild(changeRoomBtn);
    document.getElementById("chatMessages").appendChild(div);
    scrollBottom();
}
function sendAction(action, value) {
    fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            action: action,
            message: value
        })
    })
    .then(res => res.json())
    .then(showBotResponse);
}
function addMessage(text, type) {
    let msg = document.createElement("div");
    msg.className = "message " + type;
    msg.innerText = text;
    document.getElementById("chatMessages").appendChild(msg);
    scrollBottom();
}
function scrollBottom() {
    let chat = document.getElementById("chatMessages");
    chat.scrollTop = chat.scrollHeight;
}
// Switch input to calendar
function setDateInput() {
    let input = document.getElementById("messageInput");
    input.type = "date";
    input.value = "";
}
// Switch input back to normal text
function setTextInput() {
    let input = document.getElementById("messageInput");
    input.type = "text";
    input.placeholder = "Type your message...";
}
// Auto start & reset chat on refresh
window.onload = function () {
    fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "reset" })
    })
    .then(res => res.json())
    .then(showBotResponse);
};
