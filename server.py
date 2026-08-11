from flask import Flask, request, jsonify
from DNAKE_QR import generate_dnake_qr
import os
import traceback

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.json
        full_name = data.get('full_name')
        item_id = data.get('item_id')
        
        if not full_name or not item_id:
            return jsonify({"error": "Missing full_name or item_id"}), 400
            
        print(f"Processing: {full_name}")
        result_path = generate_dnake_qr(full_name, int(item_id))
        
        return jsonify({"status": "success"}), 200
    except Exception as e:
        print("--- ERROR START ---")
        traceback.print_exc()
        print("--- ERROR END ---")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
