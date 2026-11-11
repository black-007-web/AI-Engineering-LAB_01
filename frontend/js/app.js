
const API_URL = "http://127.0.0.1:8000";

const statusElement = document.getElementById("status");
const checkButton = document.getElementById("checkButton");

async function checkBackend() {
    statusElement.textContent = "Connecting...";

    try {
        const response = await fetch(`${API_URL}/health`);

        if (!response.ok) {
            throw new Error("API request failed");
        }

        const data = await response.json();

        statusElement.textContent =
            `Backend status: ${data.status}`;

    } catch (error) {
        statusElement.textContent =
            "Backend unavailable. Check your API server.";
    }
}

checkButton.addEventListener("click", checkBackend);

checkBackend();
