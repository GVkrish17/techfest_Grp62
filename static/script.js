const API_URL = 'http://127.0.0.1:5000';

/* ✅ Handle Fact Checking */
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

/* ✅ Handle URL Fact Checking */
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

/* ✅ Display Fact/URL Results */
function displayResult(data) {
    const container = document.getElementById('resultContainer');
    

    container.innerHTML = `
    <div class="result-card">
        <p><strong>Explanation:</strong></p>
        <p>${formatExplanation(data.explanation || 'No explanation available.')}</p>
    </div>
`;

}

/* ✅ Set Color Based on Confidence */
function getConfidenceColor(score) {
    if (score >= 0.75) return 'high-confidence'; // Green for high confidence
    if (score >= 0.50) return 'medium-confidence'; // Yellow for medium confidence
    return 'low-confidence'; // Red for low confidence
}

/* ✅ Format Explanation */
function formatExplanation(explanation) {
    return explanation
        .split('\n') // Split into lines
        .map(line => `• ${line}`) // Add bullet points
        .join('<br>'); // Join lines with line breaks
}

/* ✅ Toggle Chatbot Visibility */
function toggleChatbot() {
    const chatbot = document.getElementById('chatbot-container');
    chatbot.style.display = chatbot.style.display === 'block' ? 'none' : 'block';
}

/* ✅ Handle Chatbot Messaging */
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

/* ✅ Display Messages in Chatbot */
function displayMessage(message, className) {
    const messagesContainer = document.getElementById('chatbot-messages');
    const messageElement = document.createElement('div');
    messageElement.className = className;
    messageElement.innerText = message;
    messagesContainer.appendChild(messageElement);

    // Auto-scroll to latest message
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

/* ✅ Handle Image Upload */
async function uploadImage() {
    const fileInput = document.getElementById('fileInput');
    if (!fileInput.files.length) return alert("Please select a file");

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    try {
        const response = await fetch(`${API_URL}/detect-image`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        displayImageResult(data);

        // ✅ Show uploaded image
        displayUploadedImage(fileInput.files[0]);

    } catch (error) {
        alert("Failed to connect to server.");
        console.error('Error:', error);
    }
}

/* ✅ Display Uploaded Image */
function displayUploadedImage(file) {
    const uploadedImage = document.getElementById('uploadedImage');
    const imageUrl = URL.createObjectURL(file);

    uploadedImage.src = imageUrl;
    uploadedImage.style.display = 'block'; // Show the image
}

/* ✅ Display Image Result */
function displayImageResult(data) {
    const resultContainer = document.getElementById('imageResult');

    if (data.is_fake) {
        resultContainer.innerHTML = `<p style="color: red; font-weight: bold;">🚨 Fake Image Detected! Confidence: ${(data.confidence * 100).toFixed(2)}%</p>`;
    } else {
        resultContainer.innerHTML = `<p style="color: green; font-weight: bold;">✅ Real Image Detected! Confidence: ${(data.confidence * 100).toFixed(2)}%</p>`;
    }
}

/* ✅ Handle File Preview */
const fileInput = document.getElementById('fileInput');
const uploadedImage = document.getElementById('uploadedImage');

fileInput.addEventListener('change', (event) => {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            uploadedImage.src = e.target.result;
            uploadedImage.style.display = 'block'; // ✅ Show the image
        };
        reader.readAsDataURL(file);
    }
});
