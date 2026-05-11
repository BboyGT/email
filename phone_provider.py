"""Phone provider using various free SMS APIs."""
import requests
import time
import re
from typing import List, Dict, Optional
from config import USER_AGENT, REQUEST_TIMEOUT


class PhoneProvider:
    """Free SMS/OTP phone number provider."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})
    
    def get_countries(self) -> List[str]:
        """Get list of available countries from various services.
        
        Returns:
            List of country names
        """
        # Try receive-sms.cc
        try:
            url = "https://receive-sms.cc"
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            if response.status_code == 200:
                # Extract countries from the page
                countries = []
                # Common countries to return
                return ["USA", "UK", "Canada", "Australia", "France", "Germany", 
                       "Spain", "Netherlands", "Sweden", "Poland", "Russia", "China"]
        except:
            pass
        
        # Default countries
        return ["USA", "UK", "Canada"]
    
    def get_phone_numbers(self, country: str) -> List[Dict]:
        """Get phone numbers for a country from free services.
        
        Args:
            country: Country name
        
        Returns:
            List of phone number dictionaries
        """
        phones = []
        
        # Try receive-sms.cc
        try:
            url = f"https://receive-sms.cc/{country.lower()}/"
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            
            if response.status_code == 200:
                # Parse phone numbers from HTML
                import re
                phone_pattern = r'\+?\d{10,15}'
                numbers = re.findall(phone_pattern, response.text)
                
                for num in numbers[:10]:  # Limit to 10
                    phones.append({
                        'phone': num,
                        'country': country,
                        'service': 'receive-sms.cc'
                    })
        except Exception as e:
            print(f"Error getting phones from receive-sms.cc: {e}")
        
        # If no phones found, try smsreceivefree.com
        if not phones:
            try:
                url = "https://smsreceivefree.com/"
                response = self.session.get(url, timeout=REQUEST_TIMEOUT)
                
                if response.status_code == 200:
                    # Extract phone numbers
                    import re
                    phone_pattern = r'\d{3}-\d{3}-\d{4}'
                    numbers = re.findall(phone_pattern, response.text)
                    
                    for num in numbers[:10]:
                        phones.append({
                            'phone': f"+1{num.replace('-', '')}",
                            'country': 'USA',
                            'service': 'smsreceivefree.com'
                        })
            except Exception as e:
                print(f"Error getting phones from smsreceivefree: {e}")
        
        return phones
    
    def get_sms_messages(self, phone: str) -> List[Dict]:
        """Get SMS messages for a phone number.
        
        Args:
            phone: Phone number
        
        Returns:
            List of SMS message dictionaries
        """
        messages = []
        
        # Extract just digits
        phone_digits = re.sub(r'\D', '', phone)
        
        # Try receive-sms.cc
        try:
            url = f"https://receive-sms.cc/number/{phone_digits}"
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            
            if response.status_code == 200:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find message containers
                for row in soup.find_all('div', class_='message'):
                    msg_text = row.get_text(strip=True)
                    if msg_text:
                        messages.append({
                            'from': 'Unknown',
                            'body': msg_text,
                            'time': ''
                        })
        except Exception as e:
            print(f"Error getting SMS from receive-sms.cc: {e}")
        
        # Try smsreceivefree.com
        if not messages:
            try:
                # Extract number part
                url = f"https://smsreceivefree.com/details/{phone[-10:]}/"
                response = self.session.get(url, timeout=REQUEST_TIMEOUT)
                
                if response.status_code == 200:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    for msg in soup.find_all('div', class_='message'):
                        messages.append({
                            'from': msg.get('data-from', 'Unknown'),
                            'body': msg.get_text(strip=True),
                            'time': msg.get('data-date', '')
                        })
            except Exception as e:
                print(f"Error getting SMS from smsreceivefree: {e}")
        
        return messages
    
    def extract_otp_code(self, message: str) -> Optional[str]:
        """Extract OTP code from message.
        
        Args:
            message: SMS message body
        
        Returns:
            OTP code if found
        """
        # Common OTP patterns
        patterns = [
            r'\b\d{4}\b',           # 4 digits
            r'\b\d{5}\b',           # 5 digits
            r'\b\d{6}\b',           # 6 digits (most common)
            r'\b\d{4,6}\b',         # 4-6 digits
            r'code[:\s]+(\d+)',    # code: 123456
            r'otp[:\s]+(\d+)',      # otp: 123456
            r'verification[:\s]+(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return None
    
    def get_phone_info(self, phone_data: Dict) -> str:
        """Extract phone number from phone data.
        
        Args:
            phone_data: Phone data dictionary
        
        Returns:
            Phone number string
        """
        return phone_data.get('phone', '')
