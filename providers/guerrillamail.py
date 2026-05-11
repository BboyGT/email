"""Guerrilla Mail provider implementation."""
import re
from typing import Dict, List, Optional
from providers.base import BaseProvider
from utils.helpers import generate_username, generate_password


class GuerrillaMailProvider(BaseProvider):
    """Guerrilla Mail disposable email service."""
    
    def __init__(self):
        super().__init__()
        self._sid_token = None
    
    @property
    def name(self) -> str:
        return "Guerrilla Mail"
    
    @property
    def domain(self) -> str:
        return "guerrillamail.com"
    
    @property
    def requires_password(self) -> bool:
        return False
    
    def _get_session(self) -> Optional[str]:
        """Get a session token from Guerrilla Mail.
        
        Returns:
            Session token or None
        """
        url = "https://www.guerrillamail.com/ajax.php"
        params = {"f": "get_session"}
        
        response = self._make_request("GET", url, params=params)
        
        if response is None:
            return None
        
        try:
            data = response.json()
            return data.get("sid_token")
        except Exception:
            return None
    
    def generate_email(self) -> str:
        """Generate a new Guerrilla Mail email address.
        
        Returns:
            Generated email address
        """
        username = generate_username()
        return f"{username}@{self.domain}"
    
    def get_inbox(self, email: str, password: Optional[str] = None) -> List[Dict]:
        """Get emails from Guerrilla Mail inbox.
        
        Args:
            email: Email address to check
        
        Returns:
            List of email dictionaries
        """
        # Extract username from email
        username = email.split("@")[0]
        
        # Get session for this username
        url = "https://www.guerrillamail.com/ajax.php"
        params = {
            "f": "get_email_list",
            "email": username,
            "domain": "guerrillamail.com"
        }
        
        response = self._make_request("GET", url, params=params)
        
        if response is None:
            return []
        
        try:
            data = response.json()
            emails = []
            
            for msg in data.get("list", []):
                emails.append({
                    "from": msg.get("mail_from", ""),
                    "subject": msg.get("mail_subject", ""),
                    "body": "",  # Body needs separate request
                    "date": msg.get("mail_timestamp", 0),
                    "id": msg.get("mail_id", "")
                })
            
            return emails
        except Exception as e:
            print(f"Error parsing inbox: {e}")
            return []
    
    def get_email_body(self, email: str, email_id: str) -> Optional[str]:
        """Get full email body.
        
        Args:
            email: Email address
            email_id: Email ID to retrieve
        
        Returns:
            Email body text
        """
        username = email.split("@")[0]
        
        url = "https://www.guerrillamail.com/ajax.php"
        params = {
            "f": "fetch_email",
            "email": username,
            "domain": "guerrillamail.com",
            "mid": email_id
        }
        
        response = self._make_request("GET", url, params=params)
        
        if response is None:
            return None
        
        try:
            data = response.json()
            return data.get("mail_body", "")
        except Exception as e:
            print(f"Error getting email body: {e}")
            return None
