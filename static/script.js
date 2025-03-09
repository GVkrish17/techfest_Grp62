const API_URL = 'http://127.0.0.1:5000';

async function checkFact() {
    const claim = document.getElementById('claimInput').value;

    try {
        const response = await fetch(`${API_URL}/fact-check`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ claim })
        });

        const data = await response.json();

        if (response.ok) {
            displayResult(data);
        } else {
            displayResult({
                explanation: data.error || 'Failed to process claim',
                confidence_score: 0
            });
        }
    } catch (error) {
        displayResult({
            explanation: 'Failed to connect to server.',
            confidence_score: 0
        });
    }
}

async function checkURL() {
    const url = document.getElementById('urlInput').value;

    try {
        const response = await fetch(`${API_URL}/fact-check-url`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url })
        });

        const data = await response.json();

        if (response.ok) {
            displayResult(data);
        } else {
            displayResult({
                explanation: data.error || 'Failed to process URL',
                confidence_score: 0
            });
        }
    } catch (error) {
        displayResult({
            explanation: 'Failed to connect to server.',
            confidence_score: 0
        });
    }
}

function displayResult(data) {
    const container = document.getElementById('resultContainer');
    
    // Format the confidence score (if available)
    const confidence = data.confidence_score
        ? `${(data.confidence_score * 100).toFixed(2)}%`
        : 'N/A';

    container.innerHTML = `
        <div class="result-card">
            <p><strong>Confidence Score:</strong> 
                <span class="${getConfidenceColor(data.confidence_score || 0)}">
                    ${confidence}
                </span>
            </p>
            <p><strong>Explanation:</strong></p>
            <p>${formatExplanation(data.explanation || 'No explanation available.')}</p>
        </div>
    `;
}

function getConfidenceColor(score) {
    if (score >= 0.75) return 'high-confidence'; // Green for high confidence
    if (score >= 0.50) return 'medium-confidence'; // Yellow for medium confidence
    return 'low-confidence'; // Red for low confidence
}

// ✅ Format Explanation with Bullet Points
function formatExplanation(explanation) {
    return explanation
        .split('\n') // Split explanation into lines
        .map(line => `• ${line}`) // Add bullet points
        .join('<br>'); // Join lines with a line break
}

// Toggle chatbot visibility
function toggleChatbot() {
    const chatbot = document.getElementById('chatbot-container');
    chatbot.style.display = chatbot.style.display === 'block' ? 'none' : 'block';
}

// Send message to backend

async function sendMessage() {
    const inputElement = document.getElementById('chatbot-input');
    const input = inputElement.value.trim();

    if (!input) return;

    displayMessage(input, 'user-message');
    try {
        const response = await fetch(`${API_URL}/chatbot`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: input })
        });

        const data = await response.json();
        displayMessage(data.response, 'bot-message');
    } catch (error) {
        displayMessage("Failed to connect to server.", 'bot-message');
        console.error('Error:', error);
    }
}


// Display messages in chatbot
function displayMessage(message, className) {
    const messagesContainer = document.getElementById('chatbot-messages');
    const messageElement = document.createElement('div');
    messageElement.className = className;
    messageElement.innerText = message;
    messagesContainer.appendChild(messageElement);

    // Auto-scroll to latest message
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

