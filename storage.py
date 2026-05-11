"""Persistent storage module for saving emails and phone numbers."""
import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict


DATA_FILE = "data.json"


@dataclass
class EmailEntry:
    """Email entry with unique ID."""
    id: int
    email: str
    password: str
    provider: str
    created_at: str


@dataclass
class PhoneEntry:
    """Phone entry with unique ID."""
    id: int
    phone: str
    country: str
    source: str
    created_at: str


class Storage:
    """Persistent storage handler."""
    
    def __init__(self, data_file: str = DATA_FILE):
        self.data_file = data_file
        self.emails: List[EmailEntry] = []
        self.phones: List[PhoneEntry] = []
        self._next_email_id = 1
        self._next_phone_id = 1
        self.load()
    
    def load(self) -> None:
        """Load data from JSON file."""
        if not os.path.exists(self.data_file):
            self.emails = []
            self.phones = []
            self._next_email_id = 1
            self._next_phone_id = 1
            return
        
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
            
            # Load emails
            self.emails = [EmailEntry(**e) for e in data.get('emails', [])]
            
            # Load phones
            self.phones = [PhoneEntry(**p) for p in data.get('phones', [])]
            
            # Set next IDs
            if self.emails:
                self._next_email_id = max(e.id for e in self.emails) + 1
            else:
                self._next_email_id = 1
            
            if self.phones:
                self._next_phone_id = max(p.id for p in self.phones) + 1
            else:
                self._next_phone_id = 1
                
        except Exception as e:
            print(f"Error loading data: {e}")
            self.emails = []
            self.phones = []
            self._next_email_id = 1
            self._next_phone_id = 1
    
    def save(self) -> None:
        """Save data to JSON file."""
        data = {
            'emails': [asdict(e) for e in self.emails],
            'phones': [asdict(p) for p in self.phones]
        }
        
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def add_email(self, email: str, password: str, provider: str) -> EmailEntry:
        """Add a new email entry."""
        entry = EmailEntry(
            id=self._next_email_id,
            email=email,
            password=password,
            provider=provider,
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        self.emails.append(entry)
        self._next_email_id += 1
        self.save()
        return entry
    
    def add_phone(self, phone: str, country: str, source: str = "") -> PhoneEntry:
        """Add a new phone entry."""
        entry = PhoneEntry(
            id=self._next_phone_id,
            phone=phone,
            country=country,
            source=source,
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        self.phones.append(entry)
        self._next_phone_id += 1
        self.save()
        return entry
    
    def get_email_by_id(self, email_id: int) -> Optional[EmailEntry]:
        """Get email by ID."""
        for email in self.emails:
            if email.id == email_id:
                return email
        return None
    
    def get_phone_by_id(self, phone_id: int) -> Optional[PhoneEntry]:
        """Get phone by ID."""
        for phone in self.phones:
            if phone.id == phone_id:
                return phone
        return None
    
    def delete_email_by_id(self, email_id: int) -> bool:
        """Delete email by ID."""
        for i, email in enumerate(self.emails):
            if email.id == email_id:
                self.emails.pop(i)
                self.save()
                return True
        return False
    
    def delete_phone_by_id(self, phone_id: int) -> bool:
        """Delete phone by ID."""
        for i, phone in enumerate(self.phones):
            if phone.id == phone_id:
                self.phones.pop(i)
                self.save()
                return True
        return False
    
    def delete_all_emails(self) -> None:
        """Delete all emails."""
        self.emails = []
        self._next_email_id = 1
        self.save()
    
    def delete_all_phones(self) -> None:
        """Delete all phones."""
        self.phones = []
        self._next_phone_id = 1
        self.save()
    
    def clear_all(self) -> None:
        """Clear all data."""
        self.emails = []
        self.phones = []
        self._next_email_id = 1
        self._next_phone_id = 1
        self.save()
    
    def get_all_emails(self) -> List[EmailEntry]:
        """Get all emails."""
        return self.emails
    
    def get_all_phones(self) -> List[PhoneEntry]:
        """Get all phones."""
        return self.phones
    
    def get_email_count(self) -> int:
        """Get total email count."""
        return len(self.emails)
    
    def get_phone_count(self) -> int:
        """Get total phone count."""
        return len(self.phones)
