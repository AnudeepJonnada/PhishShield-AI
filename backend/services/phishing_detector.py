import re
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
import pickle
import os

class PhishingDetector:
    def __init__(self, config):
        self.config = config
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Initialize BERT model
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(config.BERT_MODEL_NAME)
            self.bert_model = AutoModelForSequenceClassification.from_pretrained(
                config.BERT_MODEL_NAME,
                num_labels=2
            )
            self.bert_model.to(self.device)
            self.bert_model.eval()
        except Exception as e:
            print(f"Warning: Could not load BERT model: {e}")
            self.bert_model = None
        
        # Initialize scikit-learn model (if available)
        self.sklearn_model = None
        if os.path.exists(config.MODEL_PATH):
            try:
                with open(config.MODEL_PATH, 'rb') as f:
                    self.sklearn_model = pickle.load(f)
            except Exception as e:
                print(f"Warning: Could not load sklearn model: {e}")
    
    def extract_features(self, email_data):
        """Extract features from email for analysis"""
        subject = email_data.get('subject', '')
        body = email_data.get('body', '')
        from_email = email_data.get('from', '')
        full_text = f"{subject} {body}".lower()
        
        features = {
            'suspicious_words': self._count_suspicious_words(full_text),
            'urls_count': len(self._extract_urls(full_text)),
            'suspicious_urls': self._check_suspicious_urls(full_text),
            'has_urgent_language': self._check_urgent_language(full_text),
            'spelling_errors': self._count_spelling_errors(full_text),
            'sender_reputation': self._check_sender_reputation(from_email),
            'domain_age_check': self._check_domain_suspicious(from_email),
            'has_attachments': bool(email_data.get('attachments', [])),
            'html_content': bool(email_data.get('html_body')),
            'suspicious_subject': self._check_suspicious_subject(subject)
        }
        
        return features
    
    def _count_suspicious_words(self, text):
        """Count suspicious words in email"""
        suspicious_words = [
            'urgent', 'verify', 'account', 'suspended', 'click here',
            'confirm', 'limited time', 'prize', 'winner', 'free',
            'act now', 'expire', 'security', 'update', 'login'
        ]
        count = sum(1 for word in suspicious_words if word in text)
        return count
    
    def _extract_urls(self, text):
        """Extract URLs from text"""
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        return re.findall(url_pattern, text)
    
    def _check_suspicious_urls(self, text):
        """Check for suspicious URL patterns"""
        urls = self._extract_urls(text)
        suspicious_patterns = [
            'bit.ly', 'tinyurl', 'goo.gl', 't.co', 'short.link',
            'ip address', 'localhost', '127.0.0.1'
        ]
        return any(pattern in url.lower() for url in urls for pattern in suspicious_patterns)
    
    def _check_urgent_language(self, text):
        """Check for urgent language"""
        urgent_words = ['urgent', 'immediate', 'asap', 'hurry', 'expire', 'limited time']
        return any(word in text for word in urgent_words)
    
    def _count_spelling_errors(self, text):
        """Simple spelling error detection (basic implementation)"""
        # This is a simplified version - in production, use a proper spell checker
        common_words = ['the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i']
        words = re.findall(r'\b\w+\b', text)
        errors = sum(1 for word in words if len(word) > 3 and word not in common_words and len(set(word)) < len(word) * 0.5)
        return min(errors, 10)  # Cap at 10
    
    def _check_sender_reputation(self, email):
        """Check sender email reputation"""
        if not email:
            return 0
        
        # Check for suspicious patterns
        suspicious_patterns = [
            'noreply', 'no-reply', 'support', 'security', 'admin',
            'service', 'account', 'notification'
        ]
        
        email_lower = email.lower()
        score = 0
        for pattern in suspicious_patterns:
            if pattern in email_lower:
                score += 1
        
        return min(score, 5)
    
    def _check_domain_suspicious(self, email):
        """Check if domain is suspicious"""
        if not email or '@' not in email:
            return 0
        
        domain = email.split('@')[1].lower()
        
        # Check for suspicious TLDs
        suspicious_tlds = ['.tk', '.ml', '.ga', '.cf', '.gq']
        if any(domain.endswith(tld) for tld in suspicious_tlds):
            return 1
        
        # Check for numbers in domain (often suspicious)
        if any(char.isdigit() for char in domain.split('.')[0]):
            return 1
        
        return 0
    
    def _check_suspicious_subject(self, subject):
        """Check if subject line is suspicious"""
        if not subject:
            return 0
        
        subject_lower = subject.lower()
        suspicious_indicators = [
            'urgent', 'action required', 'verify', 'suspended',
            'security alert', 'account', 'limited time'
        ]
        
        return 1 if any(indicator in subject_lower for indicator in suspicious_indicators) else 0
    
    def predict_with_bert(self, text):
        """Predict using BERT model"""
        if self.bert_model is None:
            return None
        
        try:
            inputs = self.tokenizer(text, return_tensors='pt', truncation=True, 
                                   max_length=512, padding=True)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self.bert_model(**inputs)
                predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
                phishing_prob = predictions[0][1].item()
            
            return phishing_prob
        except Exception as e:
            print(f"Error in BERT prediction: {e}")
            return None
    
    def calculate_threat_score(self, features, bert_score=None):
        """Calculate overall threat score"""
        score = 0
        
        # Feature-based scoring
        score += features['suspicious_words'] * 5
        score += features['urls_count'] * 3
        score += features['suspicious_urls'] * 15
        score += features['has_urgent_language'] * 10
        score += features['spelling_errors'] * 2
        score += features['sender_reputation'] * 5
        score += features['domain_age_check'] * 10
        score += features['has_attachments'] * 5
        score += features['html_content'] * 3
        score += features['suspicious_subject'] * 8
        
        # Normalize to 0-100
        base_score = min(score, 100)
        
        # Combine with BERT score if available
        if bert_score is not None:
            combined_score = (base_score * 0.4) + (bert_score * 100 * 0.6)
            return min(combined_score, 100)
        
        return base_score
    
    def analyze_email(self, email_data):
        """Analyze email and return comprehensive results"""
        # Extract features
        features = self.extract_features(email_data)
        
        # Get full text for BERT
        subject = email_data.get('subject', '')
        body = email_data.get('body', '')
        full_text = f"{subject} {body}"
        
        # Predict with BERT
        bert_score = self.predict_with_bert(full_text)
        
        # Calculate threat score
        threat_score = self.calculate_threat_score(features, bert_score)
        
        # Determine if phishing
        is_phishing = threat_score >= 50
        
        return {
            'is_phishing': is_phishing,
            'threat_score': round(threat_score, 2),
            'confidence': round(abs(threat_score - 50) * 2, 2),
            'features': features,
            'bert_score': round(bert_score, 4) if bert_score else None,
            'recommendations': self._get_recommendations(features, threat_score)
        }
    
    def _get_recommendations(self, features, threat_score):
        """Get security recommendations based on analysis"""
        recommendations = []
        
        if threat_score >= 70:
            recommendations.append("⚠️ HIGH RISK: Do not click any links or download attachments")
            recommendations.append("Delete this email immediately")
            recommendations.append("Report as phishing to your email provider")
        
        elif threat_score >= 50:
            recommendations.append("⚠️ Moderate risk detected")
            recommendations.append("Verify sender identity before taking action")
            recommendations.append("Do not provide personal information")
        
        if features['suspicious_urls']:
            recommendations.append("Contains suspicious URLs - avoid clicking")
        
        if features['has_attachments']:
            recommendations.append("Be cautious of email attachments")
        
        return recommendations if recommendations else ["Email appears safe, but always verify sender identity"]

