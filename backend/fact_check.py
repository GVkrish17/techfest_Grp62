import requests
import openai
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from fake_useragent import UserAgent

# ✅ API Keys
GOOGLE_FACT_CHECK_API_KEY = "AIzaSyDqZY9IJPB_MC7TXx3ciPxdE0y4kgKFhXY"
openai.api_key = "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"
openai.organization = "org-cyCkntgHctxSMIqLZ2DJWmEQ"

# ✅ Fact-checking for URLs:
def fact_check_website(url):
    try:
        # ✅ Check if the site allows scraping using robots.txt
        try:
            robots_txt = requests.get(f"{url}/robots.txt").text
            if "Disallow: /" in robots_txt:
                return {"error": "Scraping is blocked by the site."}
        except Exception:
            pass
        
        # ✅ Use undetected_chromedriver to bypass bot detection
        options = uc.ChromeOptions()

        # ✅ Add headers using fake_useragent
        ua = UserAgent()
        options.add_argument(f"user-agent={ua.random}")

        # ✅ Remove headless mode if needed
        options.add_argument("--headless")  # Remove this line to see the browser window
        
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920x1080")
        options.add_argument("--disable-blink-features=AutomationControlled")  # Bypass "headless" detection

        # ✅ PROXY (Optional) → Uncomment if using a proxy
        # options.add_argument("--proxy-server=http://username:password@proxy.brightdata.com:22225")

        driver = uc.Chrome(options=options)
        driver.get(url)

        # ✅ Give time for the page to load (if needed)
        driver.implicitly_wait(5)

        html = driver.page_source
        driver.quit()

        # ✅ Scrape the site content with BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        text = ' '.join(soup.stripped_strings)[:500]

        if not text:
            return {"error": "No meaningful text extracted from the site."}

        # ✅ OpenAI Explanation
        explanation = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a fact-checking assistant."},
                {"role": "user", "content": f"Check if the following information is factual: {text}"}
            ],
            max_tokens=150
        ).choices[0].message['content'].strip()

        # ✅ Confidence Score (based on content length)
        confidence_score = min(len(text) / 1000, 1.0)

        return {
            "explanation": explanation,
            "confidence_score": confidence_score
        }

    except Exception as e:
        return {"error": str(e)}


# ✅ Fact-checking for Claims:
def check_fact(claim):
    try:
        # ✅ Use Google Fact Check API
        url = f"https://factchecktools.googleapis.com/v1alpha1/claims:search?query={claim}&key={GOOGLE_FACT_CHECK_API_KEY}"
        response = requests.get(url).json()

        if 'claims' in response and len(response['claims']) > 0:
            claim_result = response['claims'][0]['claimReview'][0]
            result = claim_result['textualRating']
            source = claim_result['publisher']['name']

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

        # ✅ Use OpenAI to explain the result
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

    except Exception as e:
        return {"error": str(e)}
