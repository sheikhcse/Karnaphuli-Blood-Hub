
import os
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, db

# ১. পাথ সেটআপ (যাতে এইচটিএমএল ফাইল খুঁজে পায়)
base_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(base_dir, '..', 'frontend_web', 'templates')
static_dir = os.path.join(base_dir, '..', 'frontend_web', 'static')

# ২. ফায়ারবেস ইনিশিয়ালাইজেশন
cred_path = os.path.join(base_dir, 'firebase-key.json')
if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://karnaphuli-blood-hub-default-rtdb.firebaseio.com/'
    })

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
CORS(app)

@app.route('/')
def home():
    return render_template('index.html')

# ৩. নতুন ইউজার রেজিস্ট্রেশন
@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.json
        # শুরুতে লাস্ট ডোনেশন ডেট "Available" বা খালি থাকবে
        data['last_donation'] = "Never"
        
        ref = db.reference('donors')
        new_donor_ref = ref.push(data) # ফায়ারবেসে ডাটা পুশ
        
        return jsonify({
            "status": "success", 
            "message": "Registration Successful",
            "donor_id": new_donor_ref.key # এই আইডিটি পরে আপডেট করতে লাগবে
        }), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

# ৪. ডোনেশন ডেট আপডেট করা
@app.route('/api/update_date/<donor_id>', methods=['PATCH'])
def update_date(donor_id):
    try:
        new_date = request.json.get('date')
        ref = db.reference(f'donors/{donor_id}')
        ref.update({"last_donation": new_date})
        return jsonify({"status": "success", "message": "Date Updated"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
