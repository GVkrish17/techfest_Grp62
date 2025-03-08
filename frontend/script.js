const API_URL = 'http://localhost:5000';

async function checkFact() {
    const claim = document.getElementById('claimInput').value;

    const response = await fetch(`${API_URL}/fact-check`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({claim})
    });

    const data = await response.json();
    displayResult(data);
}

async function checkURL() {
    const url = document.getElementById('urlInput').value;

    const response = await fetch(`${API_URL}/fact-check-url`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({url})
    });

    const data = await response.json();
    displayResult(data);
}

function displayResult(data) {
    const container = document.getElementById('resultContainer');
    container.innerHTML = JSON.stringify(data, null, 2);
}
