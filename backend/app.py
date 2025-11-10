from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import os
from config import Config
from services.email_scanner import EmailScanner
from services.phishing_detector import PhishingDetector

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"], supports_credentials=True)
app.config.from_object(Config)

# Initialize MongoDB
client = MongoClient(Config.MONGODB_URI)
db = client[Config.MONGODB_DB]

# Initialize services
email_scanner = EmailScanner(Config)
phishing_detector = PhishingDetector(Config)

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'service': 'PhishShield AI'})

@app.route('/api/auth/gmail', methods=['POST'])
def authenticate_gmail():
    """Authenticate with Gmail API"""
    try:
        auth_url = email_scanner.get_authorization_url()
        return jsonify({'auth_url': auth_url}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/gmail/callback', methods=['POST'])
def gmail_callback():
    """Handle Gmail OAuth callback"""
    try:
        auth_code = request.json.get('code')
        email_scanner.handle_callback(auth_code)
        return jsonify({'status': 'authenticated'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/emails/scan', methods=['POST'])
def scan_emails():
    """Scan emails for phishing attempts"""
    try:
        max_emails = request.json.get('max_emails', 10)
        emails = email_scanner.fetch_emails(max_emails)
        
        results = []
        for email in emails:
            analysis = phishing_detector.analyze_email(email)
            
            # Combine email metadata with analysis
            result = {
                **analysis,
                'subject': email.get('subject', ''),
                'from': email.get('from', ''),
                'timestamp': email.get('timestamp', ''),
                'email_id': email.get('id', '')
            }
            results.append(result)
            
            # Store in MongoDB
            db.scans.insert_one({
                'email_id': email.get('id'),
                'subject': email.get('subject'),
                'from': email.get('from'),
                'timestamp': email.get('timestamp'),
                'threat_score': analysis['threat_score'],
                'is_phishing': analysis['is_phishing'],
                'features': analysis['features']
            })
        
        return jsonify({'results': results, 'total_scanned': len(results)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/emails/analyze', methods=['POST'])
def analyze_email():
    """Analyze a single email for phishing"""
    try:
        email_data = request.json
        analysis = phishing_detector.analyze_email(email_data)
        return jsonify(analysis), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/scans/history', methods=['GET'])
def get_scan_history():
    """Get scan history from MongoDB"""
    try:
        limit = int(request.args.get('limit', 50))
        scans = list(db.scans.find().sort('timestamp', -1).limit(limit))
        
        # Convert ObjectId to string
        for scan in scans:
            scan['_id'] = str(scan['_id'])
        
        return jsonify({'scans': scans}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get phishing detection statistics"""
    try:
        total_scans = db.scans.count_documents({})
        phishing_count = db.scans.count_documents({'is_phishing': True})
        safe_count = total_scans - phishing_count
        
        return jsonify({
            'total_scans': total_scans,
            'phishing_detected': phishing_count,
            'safe_emails': safe_count,
            'phishing_rate': (phishing_count / total_scans * 100) if total_scans > 0 else 0
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=Config.DEBUG, port=5000)

