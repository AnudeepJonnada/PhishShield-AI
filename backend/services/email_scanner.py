import os
import base64
import json
from email.utils import parsedate_to_datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from bs4 import BeautifulSoup
import re

class EmailScanner:
    def __init__(self, config):
        self.config = config
        self.credentials = None
        self.service = None
        self._load_credentials()
    
    def _load_credentials(self):
        """Load or create Gmail API credentials"""
        creds = None
        
        # Check if token exists
        if os.path.exists(self.config.GMAIL_TOKEN_PATH):
            try:
                creds = Credentials.from_authorized_user_file(
                    self.config.GMAIL_TOKEN_PATH,
                    self.config.GMAIL_SCOPES
                )
            except Exception as e:
                print(f"Error loading credentials: {e}")
        
        # If credentials are invalid, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.config.GMAIL_CREDENTIALS_PATH):
                    raise FileNotFoundError(
                        f"Gmail credentials file not found at {self.config.GMAIL_CREDENTIALS_PATH}. "
                        "Please download OAuth 2.0 credentials from Google Cloud Console."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.config.GMAIL_CREDENTIALS_PATH,
                    self.config.GMAIL_SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            os.makedirs(os.path.dirname(self.config.GMAIL_TOKEN_PATH), exist_ok=True)
            with open(self.config.GMAIL_TOKEN_PATH, 'w') as token:
                token.write(creds.to_json())
        
        self.credentials = creds
        self.service = build('gmail', 'v1', credentials=creds)
    
    def get_authorization_url(self):
        """Get authorization URL for OAuth flow"""
        if not os.path.exists(self.config.GMAIL_CREDENTIALS_PATH):
            raise FileNotFoundError("Gmail credentials file not found")
        
        flow = InstalledAppFlow.from_client_secrets_file(
            self.config.GMAIL_CREDENTIALS_PATH,
            self.config.GMAIL_SCOPES
        )
        auth_url, _ = flow.authorization_url(prompt='consent')
        return auth_url
    
    def handle_callback(self, auth_code):
        """Handle OAuth callback and store credentials"""
        flow = InstalledAppFlow.from_client_secrets_file(
            self.config.GMAIL_CREDENTIALS_PATH,
            self.config.GMAIL_SCOPES
        )
        flow.fetch_token(code=auth_code)
        creds = flow.credentials
        
        # Save credentials
        os.makedirs(os.path.dirname(self.config.GMAIL_TOKEN_PATH), exist_ok=True)
        with open(self.config.GMAIL_TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())
        
        self.credentials = creds
        self.service = build('gmail', 'v1', credentials=creds)
    
    def fetch_emails(self, max_results=10):
        """Fetch emails from Gmail"""
        try:
            results = self.service.users().messages().list(
                userId='me',
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            emails = []
            
            for msg in messages:
                email_data = self._get_email_details(msg['id'])
                if email_data:
                    emails.append(email_data)
            
            return emails
        except Exception as e:
            print(f"Error fetching emails: {e}")
            raise
    
    def _get_email_details(self, msg_id):
        """Get detailed information about an email"""
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=msg_id,
                format='full'
            ).execute()
            
            headers = message['payload'].get('headers', [])
            
            # Extract header information
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
            from_email = next((h['value'] for h in headers if h['name'] == 'From'), '')
            to_email = next((h['value'] for h in headers if h['name'] == 'To'), '')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
            
            # Parse date
            try:
                timestamp = parsedate_to_datetime(date).isoformat()
            except:
                timestamp = date
            
            # Extract body
            body, html_body = self._extract_body(message['payload'])
            
            # Extract attachments
            attachments = self._extract_attachments(message['payload'])
            
            return {
                'id': msg_id,
                'subject': subject,
                'from': from_email,
                'to': to_email,
                'timestamp': timestamp,
                'body': body,
                'html_body': html_body,
                'attachments': attachments,
                'snippet': message.get('snippet', '')
            }
        except Exception as e:
            print(f"Error getting email details: {e}")
            return None
    
    def _extract_body(self, payload):
        """Extract email body from payload"""
        body = ''
        html_body = ''
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body']['data']
                    body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                elif part['mimeType'] == 'text/html':
                    data = part['body']['data']
                    html_body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                    # Extract text from HTML
                    soup = BeautifulSoup(html_body, 'html.parser')
                    body = soup.get_text()
        else:
            if payload['mimeType'] == 'text/plain':
                data = payload['body']['data']
                body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
            elif payload['mimeType'] == 'text/html':
                data = payload['body']['data']
                html_body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                soup = BeautifulSoup(html_body, 'html.parser')
                body = soup.get_text()
        
        return body, html_body
    
    def _extract_attachments(self, payload):
        """Extract attachment information"""
        attachments = []
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part.get('filename') and part['body'].get('attachmentId'):
                    attachments.append({
                        'filename': part['filename'],
                        'mimeType': part['mimeType'],
                        'size': part['body'].get('size', 0)
                    })
        
        return attachments

