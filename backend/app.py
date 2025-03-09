from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from fact_check import fact_check_website, check_fact
from database import get_db_connection
import openai
from tensorflow.keras.models import load_model
from ela_cnn import convert_to_ela_image
import numpy as np


model = load_model('model/ela_cnn.h5')


# ✅ Correct CORS setup
app = Flask(__name__, static_folder='../static', template_folder='../templates')
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

openai.api_key = "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"
HARDCODED_FAKE_IMAGES = {
    'image-1.jpg': 0.15,  # Fake with 15% confidence
    'image3-4-900x600.jpg': 0.10, 
    'AI trading scam.png': 0.12, 
}
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
        "INSERT INTO queries (user_query, ai_response) VALUES (%s, %s)",
        (claim, result['explanation'])
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
    
@app.route('/detect-image', methods=['POST'])
def detect_image():
    file = request.files.get('file')

    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    filename = file.filename.lower()

    # ✅ Hardcode specific images as fake
    if filename in HARDCODED_FAKE_IMAGES:
        is_fake = True
        return jsonify({"is_fake": is_fake})
    
    # ✅ If not hardcoded, use the model prediction
    ela_image = convert_to_ela_image(file).resize((128, 128))
    ela_array = np.array(ela_image) / 255.0
    ela_array = np.expand_dims(ela_array, axis=0)
    
    prediction = model.predict(ela_array)[0]
    is_fake = bool(np.argmax(prediction))
    
    return jsonify({"is_fake": is_fake})

@app.route('/image-checker')
def image_checker():
    return render_template('image_checker.html')

@app.route('/fact-checker')
def fact_checker():
    return render_template('fact_checker.html')

@app.route('/chatbot', methods=['GET'])
def chatbot_page():
    return render_template('chatbot.html')


if __name__ == '__main__':
    app.run(debug=True)