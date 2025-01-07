function toggleChatbox() {
    const chatboxModal = document.getElementById("chatbox-modal");
    chatboxModal.classList.toggle("hidden");
}

function handleInput(event) {
    if (event.key === "Enter") {
        sendMessage();
    }
}

function sendMessage() {
    const inputField = document.getElementById("chatbox-input");
    const userMessage = inputField.value.trim();
    if (!userMessage) return;

    // Add user message to chatbox
    addMessage("You", userMessage);

    // Send message to backend
    fetch("/chat_support", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: userMessage }),
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.error) {
                addMessage("Support", "Sorry, we couldn't process your request.");
            } else {
                addMessage("Support", data.response || "Here is what I found: " + JSON.stringify(data.results));
            }
        })
        .catch((error) => {
            console.error("Error:", error);
            addMessage("Support", "Sorry, there was an issue processing your query.");
        });

    inputField.value = "";
}

function addMessage(sender, message) {
    const messagesContainer = document.getElementById("chatbox-messages");
    const messageElement = document.createElement("div");
    messageElement.classList.add("message");
    messageElement.innerHTML = `<strong>${sender}:</strong> ${message}`;
    messagesContainer.appendChild(messageElement);

    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}
