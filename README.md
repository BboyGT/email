# 📧 EmailGen - Disposable Email Generator

A Python CLI application for generating disposable email addresses for testing purposes.

## ⚠️ Important Notice

This tool is designed for **legitimate testing purposes only**:
- Automation testing for your applications
- Testing email-related functionality
- Receiving verification codes during development

**Do not use for:**
- Creating spam accounts
- Bypassing authentication on services you don't own
- Any illegal or unethical activities

---

## 📋 Features

- **Multiple Providers**: Support for Mailinator, Guerrilla Mail, and TempMail
- **Bulk Generation**: Generate up to 50 emails at once
- **Inbox Checking**: Check inbox for received emails
- **Verification Code Extraction**: Automatically extract verification codes
- **Password Tracking**: View passwords for generated emails
- **Colored CLI**: Clean, colorful terminal interface

---

## 🚀 Installation

1. **Clone or download this repository**

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Run the application**:
```bash
python main.py
```

---

## 💻 Usage

### Main Menu Options

| Option | Description |
|--------|-------------|
| `[1]` Generate single email | Create one disposable email |
| `[2]` Generate multiple emails | Create 1-50 emails at once |
| `[3]` Check inbox | View received emails |
| `[4]` Extract verification codes | Find verification codes in inbox |
| `[5]` View history | See all generated emails |
| `[6]` Clear history | Remove all generated emails |
| `[0]` Exit | Quit the application |

### Example Workflow

1. **Generate emails**: Choose option 2 and enter how many emails you need
2. **Use email**: Use the generated email in your test application
3. **Check inbox**: Choose option 3 to see received emails
4. **Extract code**: Choose option 4 to find verification codes

---

## 🔧 Technical Details

### Project Structure

```
email/
├── main.py              # CLI interface
├── email_generator.py   # Email generation logic
├── inbox_reader.py       # Email fetching and parsing
├── config.py            # Configuration settings
├── providers/           # Email provider implementations
│   ├── base.py
│   ├── mailinator.py
│   ├── guerrillamail.py
│   └── tempmail.py
├── utils/               # Utility functions
│   ├── helpers.py
│   └── __init__.py
├── requirements.txt     # Python dependencies
├── SPEC.md             # Specification document
└── README.md           # This file
```

### Dependencies

- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing
- `colorama` - Terminal colors

---

## ⚠️ Limitations

- **Public inboxes**: Most disposable email services use public inboxes - anyone who knows the email address can read the emails
- **Temporary nature**: Emails may be deleted after a few hours
- **Rate limits**: Some services may have rate limits
- **Not for production**: This tool is for testing only

---

## 📝 License

This project is for educational and testing purposes. Use responsibly.

---

## 🔄 Updates

- **v1.0.0**: Initial release with Mailinator, Guerrilla Mail, and TempMail support
