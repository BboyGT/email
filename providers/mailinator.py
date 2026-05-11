"""Mailinator provider implementation."""
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
from providers.base import BaseProvider
from utils.helpers import generate_username


class MailinatorProvider(BaseProvider):
    """Mailinator disposable email service."""
    
    @property
    def name(self) -> str:
        return "Mailinator"
    
    @property
    def domain(self) -> str:
        return "mailinator.com"
    
    @property
    def requires_password(self) -> bool:
        return False
    
    def generate_email(self) -> str:
        """Generate a new Mailinator email address.
        
        Returns:
            Generated email address
        """
        username = generate_username()
        return f"{username}@{self.domain}"
    
    def get_inbox(self, email: str, password: Optional[str] = None) -> List[Dict]:
        """Get emails from Mailinator inbox.
        
        Args:
            email: Email address to check
        
        Returns:
            List of email dictionaries
        """
        # Extract username from email
        username = email.split("@")[0]
        
        url = f"https://www.mailinator.com/v4/public/inboxes.jsp?to={username}"
        
        response = self._make_request("GET", url)
        
        if response is None:
            return []
        
        # Check if blocked by Cloudflare
        if response.status_code == 403:
            return []
        
        try:
            data = response.json()
        except Exception:
            # API may be blocked - return empty
            return []
        
        emails = []
            
        for msg in data.get("msgs", []):
            emails.append({
                "from": msg.get("from", ""),
                "subject": msg.get("subject", ""),
                "body": msg.get("body", ""),
                "date": msg.get("seconds_ago", 0),
                "id": msg.get("id", "")
            })
        
        return emails
    
    def get_email_body(self, email: str, email_id: str) -> Optional[str]:
        """Get full email body.
        
        Args:
            email: Email address
            email_id: Email ID to retrieve
        
        Returns:
            Email body text
        """
        username = email.split("@")[0]
        url = f"https://www.mailinator.com/v4/public/inboxes.jsp?to={username}"
        
        response = self._make_request("GET", url)
        
        if response is None:
            return None
        
        try:
            data = response.json()
            
            for msg in data.get("msgs", []):
                if msg.get("id") == email_id:
                    return msg.get("body", "")
            
            return None
        except Exception as e:
            print(f"Error getting email body: {e}")
            return None
