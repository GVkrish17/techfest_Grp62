import requests
import openai
from bs4 import BeautifulSoup

# Google Fact-Check API and GPT Keys
GOOGLE_FACT_CHECK_API_KEY = "AIzaSyDqZY9IJPB_MC7TXx3ciPxdE0y4kgKFhXY"
openai.api_key = "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"
openai.organization = "org-cyCkntgHctxSMIqLZ2DJWmEQ"

def check_fact(claim):
    # Step 1: Use Google Fact-Check API
    url = f"https://factchecktools.googleapis.com/v1alpha1/claims:search?query={claim}&key={GOOGLE_FACT_CHECK_API_KEY}"
    response = requests.get(url).json()

    if 'claims' in response and len(response['claims']) > 0:
        claim_result = response['claims'][0]['claimReview'][0]
        result = claim_result['textualRating']
        source = claim_result['publisher']['name']
        # Confidence based on source credibility and result
        if result.lower() == 'true':
            confidence_score = 0.9 if 'reliable' in source.lower() else 0.75
        elif result.lower() == 'false':
            confidence_score = 0.3 if 'unreliable' in source.lower() else 0.5
        else:
            confidence_score = 0.6
    else:
        result = "Unknown"
        source = "No data available"
        confidence_score = 0.5
    # Step 2: Use GPT to Explain
    explanation = openai.ChatCompletion.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a fact-checking assistant."},
        {"role": "user", "content": f"Explain why this claim is true or false: {claim}"}
    ],
    max_tokens=150
).choices[0].message['content'].strip()

    

    return {
        
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
            engine="gpt-4o",
            prompt=f"Check if the following information is factual: {text}",
            max_tokens=100
        ).choices[0].text.strip()

        return {
            "explanation": explanation
        }
    except Exception as e:
        return {"error": str(e)}