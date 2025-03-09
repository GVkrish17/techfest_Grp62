from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from fact_check import fact_check_website, check_fact
from database import get_db_connection
import openai

# ✅ Correct CORS setup
app = Flask(__name__, static_folder='../static', template_folder='../templates')
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

openai.api_key = "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"

# Route to serve the homepage
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/fact-check', methods=['POST'])
def fact_check():
    data = request.get_json()
    claim = data.get('claim')

    if not claim:
        return jsonify({'error': 'No claim provided'}), 400
    
    result = check_fact(claim)
    
    # ✅ Save to MySQL Database
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO queries (user_query, ai_response, confidence_score) VALUES (%s, %s, %s)",
        (claim, result['explanation'], result['confidence_score'])
    )
    connection.commit()
    connection.close()
    
    return jsonify(result)

@app.route('/fact-check-url', methods=['POST'])
def fact_check_url():
    data = request.get_json()
    url = data.get('url')
    
    if not url:
        return jsonify({"error": "No URL provided"}), 400
    
    try:
        result = fact_check_website(url)
        if 'error' in result:
            return jsonify({"error": result['error']}), 500
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    
@app.route('/chatbot', methods=['POST'])
def chatbot():
    data = request.get_json()
    user_input = data.get('message')

    if not user_input:
        return jsonify({"error": "No message provided"}), 400

    try:
        # OpenAI to generate response
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert in misinformation awareness."},
                {"role": "user", "content": user_input}
            ],
            max_tokens=100,
            temperature=0.5,
            
        ).choices[0].message['content'].strip()

        return jsonify({"response": response})

    except Exception as e:
        app.logger.error(f"Error processing request: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)