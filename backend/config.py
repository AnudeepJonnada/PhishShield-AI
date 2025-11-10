import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # MongoDB Configuration
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
    MONGODB_DB = os.getenv('MONGODB_DB', 'phishshield')
    
    # Gmail API Configuration
    GMAIL_CREDENTIALS_PATH = os.getenv('GMAIL_CREDENTIALS_PATH', 'config/gmail_credentials.json')
    GMAIL_TOKEN_PATH = os.getenv('GMAIL_TOKEN_PATH', 'config/token.json')
    GMAIL_SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Model Configuration
    MODEL_PATH = os.getenv('MODEL_PATH', 'models/phishing_model.pkl')
    BERT_MODEL_NAME = os.getenv('BERT_MODEL_NAME', 'distilbert-base-uncased')
    
    # API Configuration
    MAX_EMAILS_PER_SCAN = int(os.getenv('MAX_EMAILS_PER_SCAN', '100'))

