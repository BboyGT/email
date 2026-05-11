"""TempMail provider implementation."""
from typing import Dict, List, Optional
from providers.base import BaseProvider
from utils.helpers import generate_username


class TempMailProvider(BaseProvider):
    """TempMail disposable email service."""
    
    def __init__(self):
        super().__init__()
        self._api_token = None
    
    @property
    def name(self) -> str:
        return "TempMail"
    
    @property
    def domain(self) -> str:
        return "temp-mail.io"
    
    @property
    def requires_password(self) -> bool:
        return False
    
    def generate_email(self) -> str:
        """Generate a new TempMail email address.
        
        Returns:
            Generated email address
        """
        # Use temp-mail.io API to generate email
        url = "https://temp-mail.io/en/api/v3/email/new"
        
        response = self._make_request("POST", url)
        
        if response is None:
            # Fallback to random email
            username = generate_username()
            return f"{username}@1secmail.com"
        
        try:
            data = response.json()
            return data.get("email", f"{generate_username()}@1secmail.com")
        except Exception:
            # Fallback
            username = generate_username()
            return f"{username}@1secmail.com"
    
    def get_inbox(self, email: str, password: Optional[str] = None) -> List[Dict]:
        """Get emails from TempMail inbox.
        
        Args:
            email: Email address to check
        
        Returns:
            List of email dictionaries
        """
        # TempMail API v3
        url = f"https://temp-mail.io/en/api/v3/email/{email}/messages"
        
        response = self._make_request("GET", url)
        
        if response is None:
            return []
        
        try:
            data = response.json()
            emails = []
            
            for msg in data:
                emails.append({
                    "from": msg.get("from", ""),
                    "subject": msg.get("subject", ""),
                    "body": msg.get("body_text", ""),
                    "date": msg.get("created_at", ""),
                    "id": msg.get("id", "")
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
        url = f"https://temp-mail.io/en/api/v3/message/{email_id}"
        
        response = self._make_request("GET", url)
        
        if response is None:
            return None
        
        try:
            data = response.json()
            return data.get("body_text", "")
        except Exception as e:
            print(f"Error getting email body: {e}")
            return None
