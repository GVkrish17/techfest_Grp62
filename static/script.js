const API_URL = 'http://localhost:5000';

async function checkFact() {
    const claim = document.getElementById('claimInput').value;

    const response = await fetch(`${API_URL}/fact-check`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ claim })
    });

    const data = await response.json();
    displayResult(data);
}

async function checkURL() {
    const url = document.getElementById('urlInput').value;

    const response = await fetch(`${API_URL}/fact-check-url`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ url })
    });

    const data = await response.json();
    displayResult(data);
}

function displayResult(data) {
    const container = document.getElementById('resultContainer');
    container.innerHTML = `
        <div class="result-card">
            <p><strong>Confidence Score:</strong> 
                <span class="confidence-score ${getConfidenceColor(data.confidence_score)}">
                    ${(data.confidence_score * 100).toFixed(2)}%
                </span>
            </p>
            <p><strong>Explanation:</strong></p>
            <p>${formatExplanation(data.explanation)}</p>
        </div>
    `;
}

function getConfidenceColor(score) {
    if (score >= 0.75) return 'high-confidence';
    if (score >= 0.50) return 'medium-confidence';
    return 'low-confidence';
}

function formatExplanation(explanation) {
    return explanation.split('\n').map(line => `• ${line}`).join('<br>');
}
