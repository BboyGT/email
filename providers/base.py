"""Base provider class for email services."""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import requests
from config import USER_AGENT, REQUEST_TIMEOUT


class BaseProvider(ABC):
    """Base class for disposable email providers."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name."""
        pass
    
    @property
    @abstractmethod
    def domain(self) -> str:
        """Provider domain."""
        pass
    
    @property
    def requires_password(self) -> bool:
        """Whether provider requires password for inbox access."""
        return False
    
    @abstractmethod
    def generate_email(self) -> str:
        """Generate a new email address.
        
        Returns:
            Generated email address
        """
        pass
    
    @abstractmethod
    def get_inbox(self, email: str, password: Optional[str] = None) -> List[Dict]:
        """Get emails from inbox.
        
        Args:
            email: Email address
            password: Optional password for providers that require it
        
        Returns:
            List of email dictionaries with 'from', 'subject', 'body', 'date'
        """
        pass
    
    def _make_request(self, method: str, url: str, **kwargs) -> Optional[requests.Response]:
        """Make HTTP request with error handling.
        
        Args:
            method: HTTP method
            url: Request URL
            **kwargs: Additional request parameters
        
        Returns:
            Response object or None on failure
        """
        kwargs.setdefault("timeout", REQUEST_TIMEOUT)
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None
