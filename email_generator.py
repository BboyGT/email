"""Email generator module for creating disposable email addresses."""
import random
from typing import List, Optional
from dataclasses import dataclass

from providers import (
    MailinatorProvider,
    GuerrillaMailProvider,
    TempMailProvider,
    BaseProvider
)
from utils import print_success, print_error, generate_password


@dataclass
class GeneratedEmail:
    """Represents a generated email address."""
    email: str
    password: Optional[str]
    provider: str
    created_at: str
    
    def __str__(self) -> str:
        pwd_display = self.password if self.password else "N/A (Public)"
        return f"{self.email} | Password: {pwd_display} | Provider: {self.provider}"


class EmailGenerator:
    """Main email generator class."""
    
    def __init__(self):
        """Initialize the email generator with available providers."""
        self.providers: List[BaseProvider] = [
            MailinatorProvider(),
            GuerrillaMailProvider(),
            TempMailProvider()
        ]
        self.generated_emails: List[GeneratedEmail] = []
    
    def _get_random_provider(self) -> BaseProvider:
        """Get a random provider for email generation.
        
        Returns:
            Random provider instance
        """
        return random.choice(self.providers)
    
    def generate_single(self) -> GeneratedEmail:
        """Generate a single email address.
        
        Returns:
            Generated email with details
        """
        provider = self._get_random_provider()
        
        try:
            email = provider.generate_email()
            
            # Generate a password for tracking purposes
            password = generate_password(12)
            
            generated = GeneratedEmail(
                email=email,
                password=password,
                provider=provider.name,
                created_at="Now"
            )
            
            self.generated_emails.append(generated)
            return generated
            
        except Exception as e:
            print_error(f"Failed to generate email: {e}")
            # Fallback to Mailinator
            fallback_provider = MailinatorProvider()
            email = fallback_provider.generate_email()
            password = generate_password(12)
            
            generated = GeneratedEmail(
                email=email,
                password=password,
                provider=fallback_provider.name,
                created_at="Now"
            )
            
            self.generated_emails.append(generated)
            return generated
    
    def generate_multiple(self, count: int) -> List[GeneratedEmail]:
        """Generate multiple email addresses.
        
        Args:
            count: Number of emails to generate
        
        Returns:
            List of generated emails
        """
        if count < 1:
            count = 1
        if count > 1000:
            count = 1000  # Allow up to 1000
        
        results = []
        
        for i in range(count):
            email_obj = self.generate_single()
            results.append(email_obj)
        
        return results
    
    def get_email_by_index(self, index: int) -> Optional[GeneratedEmail]:
        """Get an email by its index in the list.
        
        Args:
            index: Index of the email (1-based)
        
        Returns:
            GeneratedEmail object or None
        """
        if 0 < index <= len(self.generated_emails):
            return self.generated_emails[index - 1]
        return None
    
    def get_all_emails(self) -> List[GeneratedEmail]:
        """Get all generated emails.
        
        Returns:
            List of all generated emails
        """
        return self.generated_emails
    
    def clear_history(self) -> None:
        """Clear the email history."""
        self.generated_emails.clear()
