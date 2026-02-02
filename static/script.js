function calculateAndShowSummary() {

    const prices = {
        classic: 2500,
        premier: 4500,
        suite: 7500
    };

    const amenities = {
        classic: "🛏️ Double Bed, 📺 TV, 🚿 Bathroom",
        premier: "🛏️ Queen Bed, ❄️ AC, 📶 WiFi, 📺 Smart TV",
        suite: "🛏️ King Bed, 🍸 Mini Bar, 🌅 Balcony, ❄️ AC, 📶 WiFi"
    };

    const nights =
        (new Date(userData.checkout) - new Date(userData.checkin)) /
        (1000 * 60 * 60 * 24);

    const totalGuests = userData.adults + userData.children;

    const extraPersons = Math.max(0, totalGuests - 2);

    const extraChargePerPerson = 750;

    const extraCost = extraPersons * extraChargePerPerson * nights;

    const roomCost = prices[userData.room] * nights;

    const total = roomCost + extraCost;

    userData.total = total;

    addBotMessage(
        `🧾 <b>Booking Summary</b>\n\n` +
        `🏨 Room: ${userData.room.toUpperCase()}\n` +
        `✨ Amenities: ${amenities[userData.room]}\n` +
        `🌙 Nights: ${nights}\n` +
        `👥 Extra Persons: ${extraPersons}\n` +
        `💰 Total Amount: ₹${total}\n\n` +
        `Confirm booking?`
    );

    showButtons([
        { label: "Change Room", value: "change_room" },
        { label: "Confirm Booking", value: "confirm" }
    ]);
}
