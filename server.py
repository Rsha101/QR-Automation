from flask import Flask, request, jsonify
from DNAKE_QR import generate_dnake_qr
import os
import sys
import logging

app = Flask(__name__)
# הגדרת לוגים שיודפסו ל-stdout ש-Render קורא
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.INFO)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    app.logger.info(f"Received data: {data}")
    
    full_name = data.get('full_name')
    item_id = data.get('item_id')
    
    # הפעלה
    result = generate_dnake_qr(full_name, int(item_id))
    app.logger.info(f"Process finished with result: {result}")
    
    return jsonify({"status": "done"}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
