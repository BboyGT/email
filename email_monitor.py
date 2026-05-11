"""Email monitoring module for tracking verification codes from specific websites."""
import time
import re
from urllib.parse import urlparse
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

from inbox_reader import InboxReader
from storage import Storage
from utils import print_info, print_success, print_warning


@dataclass
class MonitoredSite:
    """Represents a website being monitored."""
    id: int
    url: str
    domain: str
    name: str
    created_at: str


@dataclass
class DetectedCode:
    """Represents a detected verification code."""
    email: str
    code: str
    from_addr: str
    subject: str
    detected_at: str


class EmailMonitor:
    """Monitor email inboxes for verification codes from specific websites."""
    
    # Common verification code patterns
    CODE_PATTERNS = [
        r'\b\d{4}\b',           # 4 digits
        r'\b\d{5}\b',           # 5 digits
        r'\b\d{6}\b',           # 6 digits (most common)
        r'\b\d{4,8}\b',         # 4-8 digits
        r'code[:\s]+(\d+)',    # code: 123456
        r'OTP[:\s]+(\d+)',     # OTP: 123456
        r'verification[:\s]+(\d+)',
        r'\b[A-Z0-9]{4,8}\b',   # Alphanumeric codes
    ]
    
    def __init__(self, storage: Storage, inbox_reader: InboxReader):
        self.storage = storage
        self.inbox_reader = inbox_reader
        self.monitored_sites: List[MonitoredSite] = []
        self.detected_codes: List[DetectedCode] = []
        self._load_sites()
    
    def _load_sites(self):
        """Load monitored sites from storage."""
        import json
        try:
            with open('data.json', 'r') as f:
                data = json.load(f)
                sites = data.get('monitored_sites', [])
                for site in sites:
                    self.monitored_sites.append(MonitoredSite(**site))
        except:
            pass
    
    def _save_sites(self):
        """Save monitored sites to storage."""
        data = {}
        if hasattr(self.storage, 'data_file') and hasattr(self.storage, '_load_data'):
            # Load existing data
            import json
            if hasattr(self.storage, 'data'):
                data = self.storage.data
            else:
                data = {'emails': [], 'phones': [], 'monitored_sites': [], 'detected_codes': []}
        
        data['monitored_sites'] = [
            {
                'id': s.id,
                'url': s.url,
                'domain': s.domain,
                'name': s.name,
                'created_at': s.created_at
            }
            for s in self.monitored_sites
        ]
        
        # Save
        import json
        with open('data.json', 'w') as f:
            json.dump(data, f, indent=2)
    
    def add_site(self, url: str, name: str = None) -> MonitoredSite:
        """Add a website to monitor.
        
        Args:
            url: The website URL (e.g., https://ticketmaster.com)
            name: Optional custom name
        
        Returns:
            MonitoredSite object
        """
        parsed = urlparse(url)
        domain = parsed.netloc or url
        
        # Remove www. prefix
        if domain.startswith('www.'):
            domain = domain[4:]
        
        if not name:
            name = domain
        
        # Check if already monitoring
        for site in self.monitored_sites:
            if site.domain == domain:
                print_warning(f"Already monitoring {domain}")
                return site
        
        site = MonitoredSite(
            id=len(self.monitored_sites) + 1,
            url=url,
            domain=domain,
            name=name,
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        self.monitored_sites.append(site)
        self._save_sites()
        
        return site
    
    def remove_site(self, site_id: int) -> bool:
        """Remove a monitored site.
        
        Args:
            site_id: Site ID to remove
        
        Returns:
            True if removed
        """
        for i, site in enumerate(self.monitored_sites):
            if site.id == site_id:
                self.monitored_sites.pop(i)
                self._save_sites()
                return True
        return False
    
    def get_monitored_sites(self) -> List[MonitoredSite]:
        """Get all monitored sites."""
        return self.monitored_sites
    
    def extract_codes(self, text: str) -> List[str]:
        """Extract verification codes from text.
        
        Args:
            text: Text to search
        
        Returns:
            List of found codes
        """
        codes = set()
        
        for pattern in self.CODE_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Filter out common false positives
                if len(str(match)) >= 4:
                    codes.add(str(match))
        
        return list(codes)
    
    def check_emails_for_site(self, site: MonitoredSite) -> List[DetectedCode]:
        """Check all emails for messages from a specific site.
        
        Args:
            site: Site to check for
        
        Returns:
            List of detected codes
        """
        detected = []
        emails = self.storage.get_all_emails()
        
        for email in emails:
            try:
                inbox_emails = self.inbox_reader.check_inbox(email.email)
                
                for msg in inbox_emails:
                    # Check if email is from the monitored domain
                    from_addr = msg.from_addr.lower()
                    domain = site.domain.lower()
                    
                    # Check if from domain or contains domain in body
                    if domain in from_addr or domain in msg.body.lower():
                        # Extract codes
                        search_text = f"{msg.subject} {msg.body}"
                        codes = self.extract_codes(search_text)
                        
                        for code in codes:
                            detected_code = DetectedCode(
                                email=email.email,
                                code=code,
                                from_addr=msg.from_addr,
                                subject=msg.subject,
                                detected_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            )
                            detected.append(detected_code)
                            
                            # Add to detected codes list
                            self.detected_codes.append(detected_code)
                            
            except Exception as e:
                print_warning(f"Error checking {email.email}: {e}")
                continue
        
        return detected
    
    def monitor_all(self, interval: int = 5, max_duration: int = 300) -> List[DetectedCode]:
        """Monitor all sites for verification codes.
        
        Args:
            interval: Seconds between checks
            max_duration: Maximum duration to monitor (seconds)
        
        Returns:
            List of all detected codes
        """
        if not self.monitored_sites:
            print_warning("No sites to monitor. Add a site first.")
            return []
        
        print_info(f"Monitoring {len(self.monitored_sites)} site(s) for {max_duration} seconds...")
        print_info(f"Checking every {interval} seconds\n")
        
        start_time = time.time()
        all_detected = []
        
        while time.time() - start_time < max_duration:
            for site in self.monitored_sites:
                print_info(f"Checking {site.name} ({site.domain})...")
                
                detected = self.check_emails_for_site(site)
                
                if detected:
                    print_success(f"Found {len(detected)} code(s)!")
                    for d in detected:
                        print(f"  {d.email} -> {d.code}")
                    all_detected.extend(detected)
                else:
                    print_info("No new codes found")
            
            if time.time() - start_time >= max_duration:
                break
                
            print_info(f"Waiting {interval}s before next check...\n")
            time.sleep(interval)
        
        return all_detected
    
    def display_results(self):
        """Display all detected codes in organized format."""
        if not self.detected_codes:
            print_warning("No verification codes detected yet.")
            return
        
        print("\n" + "="*70)
        print(" DETECTED VERIFICATION CODES ")
        print("="*70)
        
        for i, code in enumerate(self.detected_codes, 1):
            print(f"\n[{i}] Email: {code.email}")
            print(f"    Code: {code.code}")
            print(f"    From: {code.from_addr}")
            print(f"    Subject: {code.subject}")
            print(f"    Time: {code.detected_at}")
        
        print("\n" + "="*70)
        print(f" Total: {len(self.detected_codes)} code(s) detected ")
        print("="*70 + "\n")
    
    def clear_results(self):
        """Clear detected codes history."""
        self.detected_codes.clear()
