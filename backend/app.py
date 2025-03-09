from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from fact_check import fact_check_website, check_fact
from database import get_db_connection

# ✅ Correct CORS setup
app = Flask(__name__, static_folder='../static', template_folder='../templates')
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

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

if __name__ == '__main__':
    app.run(debug=True)
