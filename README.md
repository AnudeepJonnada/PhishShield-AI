# PhishShield AI – Intelligent Phishing Email Detector

An AI-powered system that detects phishing emails using BERT and scikit-learn, integrated with Gmail API and MongoDB.

## Features
- Real-time phishing email detection
- Gmail API integration for email scanning
- BERT-based NLP model for advanced detection
- MongoDB for storing email analysis results
- React frontend for user interface
- Flask REST API backend

## Tech Stack
- **Backend**: Python (Flask), scikit-learn, BERT
- **Database**: MongoDB
- **APIs**: Gmail API
- **Frontend**: React
- **ML Models**: BERT, scikit-learn

## 🎥 Demo Video


## Setup

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

## Configuration
1. Set up Gmail API credentials in `backend/config/gmail_credentials.json`
2. Configure MongoDB connection in `backend/config.py`
3. Set environment variables in `.env` file

## Usage
1. Authenticate with Gmail API
2. Scan emails for phishing attempts
3. View detailed analysis and threat scores
4. Review historical detection data in MongoDB

