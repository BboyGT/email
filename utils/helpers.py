"""Helper utilities for EmailGen."""
import random
import string
import re
from typing import List, Optional
from config import Colors, VERIFICATION_PATTERNS

# Fake data for profile generation
FIRST_NAMES = ['James', 'Mary', 'John', 'Patricia', 'Robert', 'Jennifer', 'Michael', 'Linda', 'William', 'Elizabeth', 'David', 'Barbara', 'Richard', 'Susan', 'Joseph', 'Jessica', 'Thomas', 'Sarah', 'Charles', 'Karen']
LAST_NAMES = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin']
DOMAINS = ['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com', 'mail.com', 'protonmail.com', 'icloud.com']


def generate_random_string(length: int = 10, include_digits: bool = True, include_upper: bool = True) -> str:
    """Generate a random string for email username.
    
    Args:
        length: Length of the string to generate
        include_digits: Include digits in the string
        include_upper: Include uppercase letters
    
    Returns:
        Randomly generated string
    """
    chars = string.ascii_lowercase
    if include_digits:
        chars += string.digits
    if include_upper:
        chars += string.ascii_uppercase
    
    return ''.join(random.choice(chars) for _ in range(length))


def generate_username(prefix: str = "", suffix: str = "") -> str:
    """Generate a random username.
    
    Args:
        prefix: Optional prefix to add
        suffix: Optional suffix to add
    
    Returns:
        Generated username
    """
    username = generate_random_string(10, include_digits=True, include_upper=False)
    
    if prefix:
        username = f"{prefix}{username}"
    if suffix:
        username = f"{username}{suffix}"
    
    return username


def extract_verification_codes(text: str) -> List[str]:
    """Extract potential verification codes from text.
    
    Args:
        text: Text to search for verification codes
    
    Returns:
        List of found verification codes
    """
    codes = set()
    
    for pattern in VERIFICATION_PATTERNS:
        matches = re.findall(pattern, text)
        for match in matches:
            # Filter out common false positives
            if len(match) >= 4:
                codes.add(match)
    
    return sorted(list(codes))


def print_header(title: str) -> None:
    """Print a formatted header.
    
    Args:
        title: Header title
    """
    width = 60
    border = "═" * width
    print(f"\n{Colors.CYAN}{Colors.BOLD}╔{border}╗{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}║ {title:^{width-2}} ║{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}╚{border}╝{Colors.RESET}\n")


def print_success(message: str) -> None:
    """Print a success message.
    
    Args:
        message: Message to print
    """
    print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")


def print_error(message: str) -> None:
    """Print an error message.
    
    Args:
        message: Message to print
    """
    print(f"{Colors.RED}✗ {message}{Colors.RESET}")


def print_warning(message: str) -> None:
    """Print a warning message.
    
    Args:
        message: Message to print
    """
    print(f"{Colors.YELLOW}⚠ {message}{Colors.RESET}")


def print_info(message: str) -> None:
    """Print an info message.
    
    Args:
        message: Message to print
    """
    print(f"{Colors.CYAN}ℹ {message}{Colors.RESET}")


def print_table_row(cols: List[str], widths: Optional[List[int]] = None) -> None:
    """Print a formatted table row.
    
    Args:
        cols: Column values
        widths: Column widths (auto-calculated if not provided)
    """
    if widths is None:
        widths = [20, 35, 20]
    
    row = "│ " + " │ ".join(
        str(col).ljust(width) for col, width in zip(cols, widths)
    ) + " │"
    print(row)


def generate_fake_profile() -> dict:
    """Generate a fake profile with email and password.
    
    Returns:
        Dictionary with fake profile data
    """
    first_name = random.choice(FIRST_NAMES).lower()
    last_name = random.choice(LAST_NAMES).lower()
    username = f"{first_name}{last_name}{random.randint(1, 999)}"
    domain = random.choice(DOMAINS)
    email = f"{username}@{domain}"
    password = generate_random_string(12, include_digits=True, include_upper=True)
    
    return {
        'email': email,
        'password': password,
        'first_name': first_name.title(),
        'last_name': last_name.title(),
        'username': username
    }


def truncate_text(text: str, max_length: int = 50) -> str:
    """Truncate text to maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
    
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def generate_password(length: int = 12) -> str:
    """Generate a random password.
    
    Args:
        length: Password length
    
    Returns:
        Generated password
    """
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choice(chars) for _ in range(length))
