"""Configuration settings for EmailGen."""

import os

# Application settings
APP_NAME = "EmailGen"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Disposable Email Generator for Testing"

# Colors
class Colors:
    """ANSI color codes for terminal output."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    WHITE = "\033[97m"
    BG_CYAN = "\033[46m"

# Timeout settings
REQUEST_TIMEOUT = 30
RETRY_ATTEMPTS = 3

# Email provider settings
PROVIDERS = {
    "mailinator": {
        "name": "Mailinator",
        "domain": "mailinator.com",
        "requires_password": False,
        "inbox_url": "https://www.mailinator.com/v4/public/inboxes.jsp"
    },
    "guerrillamail": {
        "name": "Guerrilla Mail",
        "domain": "guerrillamail.com",
        "requires_password": False,
        "inbox_url": "https://www.guerrillamail.com/ajax.php"
    },
    "tempmail": {
        "name": "TempMail",
        "domain": "temp-mail.io",
        "requires_password": False,
        "inbox_url": "https://temp-mail.io/en/api/v3"
    },
    "33mail": {
        "name": "33Mail",
        "domain": "33mail.com",
        "requires_password": True,
        "inbox_url": "https://www.33mail.com"
    }
}

# Verification code patterns
VERIFICATION_PATTERNS = [
    r'\b\d{4}\b',           # 4 digits
    r'\b\d{5}\b',           # 5 digits
    r'\b\d{6}\b',           # 6 digits (most common)
    r'\b\d{8}\b',           # 8 digits
    r'[A-Z]{2,3}\d{3,6}',   # Letters + digits
    r'\d+\s+\d+\s+\d+',     # Spaced digits
]

# User agent
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
