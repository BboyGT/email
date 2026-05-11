# EmailGen + Phone OTP - Specification Document

## Project Overview

**Project Name:** EmailGen  
**Project Type:** Python CLI Application  
**Core Functionality:** A command-line tool that generates disposable email addresses and temporary phone numbers for testing, with persistent storage and unique IDs for each entry.  
**Target Users:** Developers and QA engineers who need to test email and SMS/OTP-related functionality in their applications.

---

## New Features (v2.0)

### 1. Persistent Storage
- All generated emails and phone numbers are saved to a JSON file (`data.json`)
- Data persists between sessions
- New emails/phones are added to existing ones (cumulative)
- Data is automatically loaded on application start

### 2. Unique ID System
- Each email gets a unique sequential ID (1, 2, 3, ...)
- Each phone number gets a unique sequential ID
- Users can reference entries by ID for operations

### 3. Phone Number Integration (free-otp-api)
- Uses https://otp-api.shelex.dev for temporary phone numbers
- Get list of available countries
- Get phone numbers per country
- Retrieve SMS/OTP codes

### 4. Delete Functionality
- Delete individual email by ID
- Delete individual phone by ID
- Delete all emails
- Delete all phones
- Clear everything

---

## API Integration

### free-otp-api Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `https://otp-api.shelex.dev/api/countries` | GET | Get available countries |
| `https://otp-api.shelex.dev/api/list/{country}` | GET | Get phone numbers for country |
| `https://otp-api.shelex.dev/api/{country}/{phone}` | GET | Get SMS/OTP for phone |

### Query Parameters
- `match` - Substring to look for in SMS
- `ago` - Max time ago (e.g., 30s, 5m, 1h)
- `source` - SMS service provider

---

## Data Models

### Email Entry
```json
{
  "id": 1,
  "email": "test123@mailinator.com",
  "password": "abc123",
  "provider": "Mailinator",
  "created_at": "2024-01-01 12:00:00"
}
```

### Phone Entry
```json
{
  "id": 1,
  "phone": "+1234567890",
  "country": "USA",
  "source": "receive-sms-free.cc",
  "created_at": "2024-01-01 12:00:00"
}
```

---

## UI/UX Specification

### Main Menu
```
╔═══════════════════════════════════════════════════╗
║       📧 EmailGen - Disposable Email & Phone     ║
╠═══════════════════════════════════════════════════╣
║  [1] Generate email(s)                          ║
║  [2] Generate phone number(s)                   ║
║  [3] Check email inbox                          ║
║  [4] Check phone for OTP                        ║
║  [5] View all emails                            ║
║  [6] View all phones                            ║
║  [7] Delete entry                               ║
║  [8] Delete all                                 ║
║  [0] Exit                                       ║
╚═══════════════════════════════════════════════════╝
```

### Display Format (with IDs)
```
╔═══════════════════════════════════════════════════════════════════╗
║  #ID │ Email Address                    │ Password     │ Provider  ║
╠══════╪══════════════════════════════════╪══════════════╪═══════════╣
║  1   │ test123@mailinator.com           │ abc123       │ Mailinator║
║  2   │ johndoe@guerrillamail.com        │ xyz789       │ Guerrilla ║
╚══════╧══════════════════════════════════╧══════════════╧═══════════╝
```

---

## Implementation Plan

### Files to Create/Modify

1. **storage.py** (NEW) - Persistent JSON storage
2. **phone_provider.py** (NEW) - free-otp-api integration
3. **main.py** (MODIFY) - Update CLI with new features
4. **data.json** (AUTO) - Persistent data file

### Modules

1. `storage.py` - Handles loading/saving to JSON
2. `phone_provider.py` - API calls for phone numbers
3. `main.py` - Updated CLI with all features

---

## Acceptance Criteria

1. ✅ Emails persist after closing app
2. ✅ Phone numbers persist after closing app  
3. ✅ Can generate 100+ emails and they all stay saved
4. ✅ Each entry has unique ID
5. ✅ Can delete individual entries by ID
6. ✅ Can delete all entries
7. ✅ Can get phone numbers from free-otp-api
8. ✅ Can retrieve OTP codes from phone numbers
9. ✅ Can select country for phone numbers
10. ✅ All data displayed with IDs
