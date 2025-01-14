// Show the typing indicator
function showTypingIndicator() {
    const typingIndicator = document.getElementById("typing-indicator");
    typingIndicator.classList.remove("hidden");
}

// Hide the typing indicator
function hideTypingIndicator() {
    const typingIndicator = document.getElementById("typing-indicator");
    typingIndicator.classList.add("hidden");
}


function toggleChatbox() {
    const chatboxModal = document.getElementById("chatbox-modal");
    const isVisible = chatboxModal.classList.contains("active");

    chatboxModal.classList.toggle("active");
    chatboxModal.setAttribute("aria-hidden", isVisible);
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

    // Show the typing indicator
    showTypingIndicator();

    // Send message to backend
    fetch("/chat_support", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: userMessage }),
    })

        .then((response) => response.json())
        .then((data) => {
            // Hide the typing indicator once a response is received
            hideTypingIndicator();

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

    // Add a class for the message type (user/assistant)
    messageElement.classList.add("message");
    if (sender === "You") {
        messageElement.classList.add("user");
    } else {
        messageElement.classList.add("assistant");
    }

    // Set the message content
    messageElement.innerHTML = `<strong>${sender}:</strong> ${message}`;

    // Append the message to the container
    messagesContainer.appendChild(messageElement);

    // Scroll to the latest message
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

