from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from fact_check import check_fact, fact_check_website
from database import get_db_connection

# ✅ Tell Flask where the static folder is located
app = Flask(__name__, static_folder='../static', template_folder='../templates')
CORS(app)

# Route to serve the homepage
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/fact-check', methods=['POST'])
def fact_check():
    data = request.get_json()
    claim = data.get('claim')
    
    result = check_fact(claim)
    
    # Save to MySQL Database
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
    result = fact_check_website(url)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
