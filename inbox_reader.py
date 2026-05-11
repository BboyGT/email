"""Inbox reader module for fetching and parsing emails."""
from typing import List, Dict, Optional
from dataclasses import dataclass
import time

from providers import MailinatorProvider, GuerrillaMailProvider, TempMailProvider
from utils import print_info, print_error, print_warning, extract_verification_codes


@dataclass
class Email:
    """Represents an email message."""
    email_id: str
    from_addr: str
    subject: str
    body: str
    date: str
    
    def __str__(self) -> str:
        return f"From: {self.from_addr}\nSubject: {self.subject}\n\n{self.body[:200]}..."


class InboxReader:
    """Inbox reader for checking emails across providers."""
    
    def __init__(self):
        """Initialize inbox reader with providers."""
        self.providers = {
            "mailinator.com": MailinatorProvider(),
            "guerrillamail.com": GuerrillaMailProvider(),
            "temp-mail.io": TempMailProvider(),
            "1secmail.com": TempMailProvider()  # TempMail fallback domain
        }
    
    def _get_provider(self, email: str):
        """Get the appropriate provider for an email address.
        
        Args:
            email: Email address
        
        Returns:
            Provider instance or None
        """
        domain = email.split("@")[1].lower()
        
        for key, provider in self.providers.items():
            if key in domain:
                return provider
        
        # Default to Mailinator
        return MailinatorProvider()
    
    def check_inbox(self, email: str, password: Optional[str] = None) -> List[Email]:
        """Check the inbox for an email address.
        
        Args:
            email: Email address to check
            password: Optional password for providers that require it
        
        Returns:
            List of Email objects
        """
        provider = self._get_provider(email)
        
        try:
            raw_emails = provider.get_inbox(email, password)
            
            emails = []
            for raw in raw_emails:
                email_obj = Email(
                    email_id=raw.get("id", ""),
                    from_addr=raw.get("from", ""),
                    subject=raw.get("subject", ""),
                    body=raw.get("body", ""),
                    date=str(raw.get("date", ""))
                )
                emails.append(email_obj)
            
            return emails
        
        except Exception as e:
            # Silently handle errors - API may be blocked
            return []
    
    def wait_for_email(self, email: str, timeout: int = 60, interval: int = 5) -> Optional[Email]:
        """Wait for an email to arrive.
        
        Args:
            email: Email address to check
            timeout: Maximum time to wait in seconds
            interval: Time between checks in seconds
        
        Returns:
            Email object or None if timeout
        """
        print_info(f"Waiting for email at {email}...")
        
        elapsed = 0
        while elapsed < timeout:
            emails = self.check_inbox(email)
            
            if emails:
                print_info(f"Email received after {elapsed} seconds!")
                return emails[0]  # Return most recent
            
            time.sleep(interval)
            elapsed += interval
            print_info(f"Still waiting... ({elapsed}s/{timeout}s)")
        
        print_warning("Timeout reached - no email received")
        return None
    
    def extract_codes_from_inbox(self, email: str) -> Dict[str, List[str]]:
        """Extract verification codes from inbox.
        
        Args:
            email: Email address to check
        
        Returns:
            Dictionary mapping email ID to list of codes found
        """
        emails = self.check_inbox(email)
        
        results = {}
        
        for email_obj in emails:
            # Check both subject and body for codes
            search_text = f"{email_obj.subject} {email_obj.body}"
            codes = extract_verification_codes(search_text)
            
            if codes:
                results[email_obj.email_id] = codes
        
        return results
    
    def get_latest_verification_code(self, email: str) -> Optional[str]:
        """Get the most recent verification code from inbox.
        
        Args:
            email: Email address to check
        
        Returns:
            Verification code or None
        """
        codes_dict = self.extract_codes_from_inbox(email)
        
        if not codes_dict:
            return None
        
        # Get codes from the most recent email
        emails = self.check_inbox(email)
        
        if emails:
            latest_id = emails[0].email_id
            if latest_id in codes_dict:
                return codes_dict[latest_id][0]  # Return first code found
        
        return None
