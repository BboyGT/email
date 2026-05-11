"""Enhanced auto signup module with fake profile data."""
import requests
import time
import random
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
from config import USER_AGENT, REQUEST_TIMEOUT


# Fake data for realistic profiles
FIRST_NAMES = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", 
               "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
               "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Lisa"]

LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
              "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
              "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Thompson", "White"]

STREET_NAMES = ["Main", "Oak", "Maple", "Cedar", "Pine", "Elm", "Washington", "Lake", "Hill",
                "Park", "Forest", "River", "Spring", "Valley", "Sunset", "Highland"]

STREET_TYPES = ["St", "Ave", "Blvd", "Rd", "Dr", "Ln", "Ct", "Way"]

CITIES = {
    "USA": ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", 
            "San Antonio", "San Diego", "Dallas", "San Jose"],
    "UK": ["London", "Birmingham", "Manchester", "Glasgow", "Liverpool", "Bristol", "Sheffield"],
    "CA": ["Toronto", "Vancouver", "Montreal", "Calgary", "Ottawa", "Edmonton"],
    "AU": ["Sydney", "Melbourne", "Brisbane", "Perth", "Adelaide"]
}

STATES = {
    "USA": ["NY", "CA", "TX", "FL", "IL", "PA", "OH", "GA", "NC", "MI"],
    "CA": ["ON", "BC", "QC", "AB", "MB"],
    "AU": ["NSW", "VIC", "QLD", "WA", "SA"]
}


class FakeProfile:
    """Generate fake profile data."""
    
    @staticmethod
    def generate(first_name: str = None, last_name: str = None) -> Dict:
        """Generate a complete fake profile.
        
        Args:
            first_name: Optional first name
            last_name: Optional last name
        
        Returns:
            Dictionary with profile data
        """
        first = first_name or random.choice(FIRST_NAMES)
        last = last_name or random.choice(LAST_NAMES)
        
        country = "USA"  # Default
        city = random.choice(CITIES.get(country, ["New York"]))
        state = random.choice(STATES.get(country, ["NY"]))
        
        # Generate random DOB (18-65 years old)
        year = random.randint(1959, 2006)
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        dob = f"{month:02d}/{day:02d}/{year}"
        
        # Generate phone
        phone = f"+1{random.randint(2000000000, 9999999999)}"
        
        # Generate username from email
        username = f"{first.lower()}{last.lower()}{random.randint(1, 999)}"
        
        return {
            "first_name": first,
            "last_name": last,
            "full_name": f"{first} {last}",
            "email": "",  # Will be set by caller
            "username": username,
            "phone": phone,
            "dob": dob,
            "year": str(year),
            "month": str(month),
            "day": str(day),
            "address": f"{random.randint(100, 9999)} {random.choice(STREET_NAMES)} {random.choice(STREET_TYPES)}",
            "city": city,
            "state": state,
            "country": country,
            "zip": str(random.randint(10000, 99999)),
        }


class EnhancedAutoSignup:
    """Enhanced automated signup bot with fake profiles."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        })
    
    def get_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch a webpage and parse it."""
        try:
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            print(f"Error fetching page: {e}")
            return None
    
    def find_all_inputs(self, soup: BeautifulSoup) -> List[Dict]:
        """Find all input fields on the page."""
        inputs = []
        
        for inp in soup.find_all(['input', 'textarea', 'select']):
            inp_type = inp.get('type', 'text').lower()
            name = inp.get('name', '').lower()
            id_val = inp.get('id', '').lower()
            placeholder = inp.get('placeholder', '').lower()
            label = inp.get('aria-label', '').lower()
            
            # Skip hidden fields and buttons
            if inp_type in ['hidden', 'submit', 'button', 'image', 'reset']:
                continue
            
            inputs.append({
                'type': inp_type,
                'name': inp.get('name', ''),
                'id': inp.get('id', ''),
                'placeholder': inp.get('placeholder', ''),
                'label': label,
                'tag': inp,
                'required': inp.get('required', False)
            })
        
        return inputs
    
    def categorize_field(self, field: Dict) -> str:
        """Categorize a form field based on its attributes."""
        name = field.get('name', '')
        id_val = field.get('id', '')
        placeholder = field.get('placeholder', '')
        label = field.get('label', '')
        
        combined = f"{name} {id_val} {placeholder} {label}".lower()
        
        # Email
        if 'email' in combined:
            return 'email'
        
        # Password
        if 'pass' in combined:
            return 'password'
        
        # First name
        if 'first' in combined and 'name' in combined:
            return 'first_name'
        
        # Last name
        if 'last' in combined and 'name' in combined:
            return 'last_name'
        
        # Full name
        if 'name' in combined and 'full' in combined:
            return 'full_name'
        
        # Username
        if 'user' in combined and 'name' in combined:
            return 'username'
        
        # Phone
        if 'phone' in combined or 'tel' in combined or 'mobile' in combined:
            return 'phone'
        
        # Address
        if 'address' in combined or 'street' in combined:
            return 'address'
        
        # City
        if 'city' in combined or 'town' in combined:
            return 'city'
        
        # State
        if 'state' in combined or 'province' in combined:
            return 'state'
        
        # Country
        if 'country' in combined:
            return 'country'
        
        # Zip
        if 'zip' in combined or 'postal' in combined:
            return 'zip'
        
        # DOB - various formats
        if 'dob' in combined or 'birth' in combined:
            if 'year' in combined:
                return 'year'
            if 'month' in combined:
                return 'month'
            if 'day' in combined:
                return 'day'
            return 'dob'
        
        # Gender
        if 'gender' in combined or 'sex' in combined:
            return 'gender'
        
        # Generic text field
        if field.get('type') == 'text' or not field.get('type'):
            return 'text'
        
        return 'other'
    
    def fill_form(self, soup: BeautifulSoup, profile: Dict) -> Dict:
        """Fill form with profile data."""
        inputs = self.find_all_inputs(soup)
        
        form_data = {}
        
        for field in inputs:
            category = self.categorize_field(field)
            field_name = field.get('name', '')
            
            if not field_name:
                continue
            
            # Map profile fields to form fields
            if category == 'email':
                form_data[field_name] = profile.get('email', '')
            elif category == 'password':
                form_data[field_name] = f"{profile.get('first_name', 'Pass')}@123"
            elif category == 'first_name':
                form_data[field_name] = profile.get('first_name', '')
            elif category == 'last_name':
                form_data[field_name] = profile.get('last_name', '')
            elif category == 'full_name':
                form_data[field_name] = profile.get('full_name', '')
            elif category == 'username':
                form_data[field_name] = profile.get('username', profile.get('email', '').split('@')[0])
            elif category == 'phone':
                form_data[field_name] = profile.get('phone', '')
            elif category == 'address':
                form_data[field_name] = profile.get('address', '')
            elif category == 'city':
                form_data[field_name] = profile.get('city', '')
            elif category == 'state':
                form_data[field_name] = profile.get('state', '')
            elif category == 'country':
                form_data[field_name] = profile.get('country', 'US')
            elif category == 'zip':
                form_data[field_name] = profile.get('zip', '')
            elif category == 'year':
                form_data[field_name] = profile.get('year', '1990')
            elif category == 'month':
                form_data[field_name] = profile.get('month', '01')
            elif category == 'day':
                form_data[field_name] = profile.get('day', '01')
            elif category == 'dob':
                form_data[field_name] = profile.get('dob', '01/01/1990')
            elif category == 'gender':
                form_data[field_name] = random.choice(['male', 'female', 'other'])
            elif category == 'text':
                # For generic text fields, use name or username
                if 'company' in field_name:
                    form_data[field_name] = f"{profile.get('last_name', 'Company')} Inc"
                elif 'company' in field_name:
                    form_data[field_name] = f"{profile.get('last_name', 'Company')} Inc"
        
        return form_data
    
    def find_form(self, soup: BeautifulSoup) -> Optional[Dict]:
        """Find the best form to use."""
        forms = []
        
        for form in soup.find_all('form'):
            # Count input fields
            inputs = form.find_all(['input', 'textarea'])
            
            if len(inputs) >= 2:  # At least email + another field
                forms.append({
                    'action': form.get('action', ''),
                    'method': form.get('method', 'get').upper(),
                    'inputs': inputs,
                    'tag': form
                })
        
        # Return first form with most inputs
        forms.sort(key=lambda x: len(x['inputs']), reverse=True)
        
        return forms[0] if forms else None
    
    def signup(self, url: str, email: str, profile: Dict = None) -> Dict:
        """Attempt to signup with profile data.
        
        Args:
            url: Signup URL
            email: Email to use
            profile: Optional profile data
        
        Returns:
            Result dictionary
        """
        result = {
            'success': False,
            'email': email,
            'message': '',
            'form_found': False,
            'fields_filled': 0
        }
        
        # Generate profile if not provided
        if not profile:
            profile = FakeProfile.generate()
        
        profile['email'] = email
        
        # Get the page
        soup = self.get_page(url)
        if not soup:
            result['message'] = "Failed to fetch page"
            return result
        
        # Find form
        form = self.find_form(soup)
        
        if not form:
            result['message'] = "No signup form found"
            return result
        
        result['form_found'] = True
        
        # Fill form
        form_data = self.fill_form(soup, profile)
        result['fields_filled'] = len(form_data)
        
        # Submit form
        try:
            action = form['action']
            if not action.startswith('http'):
                from urllib.parse import urljoin
                action = urljoin(url, action)
            
            method = form.get('method', 'POST')
            
            if method == 'POST':
                response = self.session.post(action, data=form_data, timeout=REQUEST_TIMEOUT)
            else:
                response = self.session.get(action, params=form_data, timeout=REQUEST_TIMEOUT)
            
            result['submitted'] = True
            
            if response.status_code in [200, 201, 302]:
                result['success'] = True
                result['message'] = f"Form submitted! ({result['fields_filled']} fields)"
            else:
                result['message'] = f"Got status: {response.status_code}"
                
        except Exception as e:
            result['message'] = f"Error: {str(e)[:50]}"
        
        return result
    
    def bulk_signup(self, url: str, emails: List[str], delay: int = 2) -> List[Dict]:
        """Signup with multiple emails and profiles.
        
        Args:
            url: Signup URL
            emails: List of emails
            delay: Delay between requests
        
        Returns:
            List of results
        """
        results = []
        
        for i, email in enumerate(emails):
            print(f"\n[{i+1}/{len(emails)}] Signing up with {email}...")
            
            # Generate unique profile for each email
            profile = FakeProfile.generate()
            profile['email'] = email
            
            result = self.signup(url, email, profile)
            results.append({
                'email': email,
                'profile': profile,
                **result
            })
            
            if result['success']:
                print(f"  ✓ {result['message']}")
            else:
                print(f"  ✗ {result['message']}")
            
            if i < len(emails) - 1:
                time.sleep(delay)
        
        return results
