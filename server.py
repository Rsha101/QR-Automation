from flask import Flask, request, jsonify
from DNAKE_QR import generate_dnake_qr
import os

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    
    # מייק ישלח לנו את השם המלא ואת המזהה של השורה
    full_name = data.get('full_name')
    item_id = data.get('item_id')
    
    if not full_name or not item_id:
        return jsonify({"error": "Missing full_name or item_id"}), 400
        
    print(f"Received request from Make for: {full_name} (Item: {item_id})")
    
    # הפעלת קוד יצירת ה-QR
    result_path = generate_dnake_qr(full_name, int(item_id))
    
    if result_path:
        return jsonify({"status": "success", "message": "QR uploaded perfectly"}), 200
    else:
        return jsonify({"status": "error", "message": "Failed to generate or upload"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
