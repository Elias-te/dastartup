from flask import Flask, request, jsonify, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os  # <--- Make sure this line exists!
from flask import Flask, request, jsonify, session, send_from_directory
# ... the rest of your imports

# 1. INITIALIZE THE APP
# We tell Flask that the current folder ('.') contains our HTML files
app = Flask(__name__, static_url_path='', static_folder='.')

# 2. CONFIGURE THE APP
CORS(app, supports_credentials=True) 
app.secret_key = 'das_super_secret_key_2026' 

# This creates a reliable path for your database on Render
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'das_leads.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 3. INITIALIZE THE DATABASE
db = SQLAlchemy(app)

# 4. DEFINE THE DATA MODEL
class Lead(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100))
    email = db.Column(db.String(120), nullable=False)
    service = db.Column(db.String(100))
    challenge = db.Column(db.Text)

# Create the database file automatically
with app.app_context():
    db.create_all()

# 5. ROUTES (The "Doors")

# --- NEW: THIS ROUTE SERVES YOUR WEBSITE SAFELY ---
@app.route('/')
def home():
    # This finds the exact folder where app.py is saved
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return send_from_directory(base_dir, 'index.html')

@app.route('/api/contact', methods=['POST'])
def contact():
    data = request.json
    try:
        new_lead = Lead(
            name=data.get('name'),
            company=data.get('company'),
            email=data.get('email'),
            service=data.get('service'),
            challenge=data.get('challenge')
        )
        db.session.add(new_lead)
        db.session.commit()
        return jsonify({"message": "Lead saved successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    if data.get('username') == 'admin' and data.get('password') == 'das2025':
        session['logged_in'] = True
        return jsonify({"message": "Login successful"}), 200
    return jsonify({"message": "Invalid credentials"}), 401

@app.route('/api/admin/leads', methods=['GET'])
def get_leads():
    if not session.get('logged_in'):
        return jsonify({"message": "Unauthorized"}), 401
    
    leads = Lead.query.all()
    output = []
    for lead in leads:
        output.append({
            "id": lead.id,
            "name": lead.name,
            "company": lead.company,
            "email": lead.email,
            "service": lead.service,
            "challenge": lead.challenge
        })
    return jsonify(output)
@app.route('/api/admin/leads/<int:lead_id>', methods=['DELETE'])
def delete_lead(lead_id):
    if not session.get('logged_in'):
        return jsonify({"message": "Unauthorized"}), 401
    
    lead = Lead.query.get(lead_id)
    if lead:
        db.session.delete(lead)
        db.session.commit()
        return jsonify({"message": "Lead deleted successfully"}), 200
    return jsonify({"message": "Lead not found"}), 404
# --- ROUTE TO SHOW THE LOGIN PAGE ---
@app.route('/admin')
def admin_page():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # This serves your admin login/dashboard HTML file
    return send_from_directory(base_dir, 'admin.html')

# --- ROUTE TO SHOW THE DASHBOARD (jdas.html) ---
@app.route('/dashboard')
def dashboard_page():
    if not session.get('logged_in'):
        # If not logged in, send them back to the login page
        base_dir = os.path.dirname(os.path.abspath(__file__))
        return send_from_directory(base_dir, 'admin.html')
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return send_from_directory(base_dir, 'jdas.html')

# ... all your routes (home, contact, login, etc.) are above this ...

if __name__ == '__main__':
    # We remove 'debug=True' for the real internet and use the 'PORT' variable
    # This lets the Cloud Host (like Render) decide which "door" to open.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)