import requests
import openai
from bs4 import BeautifulSoup

# Google Fact-Check API and GPT Keys
GOOGLE_FACT_CHECK_API_KEY = "AIzaSyDqZY9IJPB_MC7TXx3ciPxdE0y4kgKFhXY"
openai.api_key = "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"

def check_fact(claim):
    # Step 1: Use Google Fact-Check API
    url = f"https://factchecktools.googleapis.com/v1alpha1/claims:search?query={claim}&key={GOOGLE_FACT_CHECK_API_KEY}"
    response = requests.get(url).json()

    if 'claims' in response and len(response['claims']) > 0:
        claim_result = response['claims'][0]['claimReview'][0]
        result = claim_result['textualRating']
        source = claim_result['publisher']['name']
    else:
        result = "Unknown"
        source = "No data available"

    # Step 2: Use GPT to Explain
    explanation = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a fact-checking assistant."},
        {"role": "user", "content": f"Explain why this claim is true or false: {claim}"}
    ],
    max_tokens=100
).choices[0].message['content'].strip()

    confidence_score = 0.85 if result.lower() == 'true' else 0.45

    return {
        'result': result,
        'source': source,
        'explanation': explanation,
        'confidence_score': confidence_score
    }

# ✅ Fact-Check Source Website
def fact_check_website(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        text = ' '.join(soup.stripped_strings)[:500]

        explanation = openai.Completion.create(
            engine="gpt-4",
            prompt=f"Check if the following information is factual: {text}",
            max_tokens=100
        ).choices[0].text.strip()

        return {
            "explanation": explanation
        }
    except Exception as e:
        return {"error": str(e)}