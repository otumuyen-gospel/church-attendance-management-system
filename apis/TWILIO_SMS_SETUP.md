# Twilio SMS Setup Guide

## Overview
This guide helps you set up Twilio SMS API integration for your Church Attendance Management System.

## Step 1: Install Twilio Package

The `twilio` package has been added to `requirements.txt`. Install it using:

```bash
pip install -r requirements.txt
```

Or install just Twilio:

```bash
pip install twilio==9.4.0
```

## Step 2: Get Twilio Credentials

1. Create a free Twilio account at https://www.twilio.com/console
2. Verify your phone number (for trial account)
3. Find your credentials:
   - **Account SID**: Available at https://www.twilio.com/console
   - **Auth Token**: Available at https://www.twilio.com/console
   - **Phone Number**: You'll get a Twilio phone number when you sign up (e.g., +1234567890)

## Step 3: Configure Environment Variables

You have two options to set your Twilio credentials:

### Option A: Environment Variables (Recommended)

Set these environment variables on your system or in a `.env` file:

```bash
# Windows PowerShell
$env:TWILIO_ACCOUNT_SID = "your_account_sid_here"
$env:TWILIO_AUTH_TOKEN = "your_auth_token_here"
$env:TWILIO_PHONE_NUMBER = "+1234567890"
```

Or create a `.env` file in the `apis/` directory:

```
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+1234567890
```

Then load it using `python-dotenv`:

```bash
pip install python-dotenv
```

Update your `settings.py`:

```python
import os
from dotenv import load_dotenv

load_dotenv()

TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', '')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN', '')
TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER', '')
```

### Option B: Direct Configuration (Development Only)

Edit `apis/settings.py` and add:

```python
TWILIO_ACCOUNT_SID = 'your_account_sid'
TWILIO_AUTH_TOKEN = 'your_auth_token'
TWILIO_PHONE_NUMBER = '+1234567890'
```

⚠️ **Never commit credentials to version control!**

## Step 4: SMS API Endpoints

### 1. Send Single SMS

**Endpoint:** `POST /message/send-sms/`

**Request:**
```json
{
    "phone_number": "+1234567890",
    "message_title": "Attendance Reminder",
    "message_body": "Please attend the service on Sunday at 10 AM"
}
```

**Response (Success):**
```json
{
    "success": true,
    "message_sid": "SM1234567890abcdef",
    "status": "queued",
    "to": "+1234567890",
    "message": "SMS sent successfully"
}
```

**Response (Error):**
```json
{
    "success": false,
    "error": "Error message details",
    "message": "Failed to send SMS"
}
```

### 2. Send Bulk SMS

**Endpoint:** `POST /message/send-bulk-sms/`

**Request:**
```json
{
    "phone_numbers": ["+1234567890", "+0987654321", "+5555555555"],
    "message_title": "Service Reminder",
    "message_body": "Sunday service at 10 AM. Please plan to attend!"
}
```

**Response:**
```json
{
    "total": 3,
    "successful": 3,
    "failed": 0,
    "details": [
        {
            "success": true,
            "message_sid": "SM...",
            "status": "queued",
            "to": "+1234567890",
            "message": "SMS sent successfully"
        },
        {
            "success": true,
            "message_sid": "SM...",
            "status": "queued",
            "to": "+0987654321",
            "message": "SMS sent successfully"
        },
        {
            "success": true,
            "message_sid": "SM...",
            "status": "queued",
            "to": "+5555555555",
            "message": "SMS sent successfully"
        }
    ]
}
```

### 3. Send Verification SMS

**Endpoint:** `POST /message/send-verification-sms/`

**Request:**
```json
{
    "phone_number": "+1234567890",
    "verification_code": "123456"
}
```

**Response:**
```json
{
    "success": true,
    "message_sid": "SM1234567890abcdef",
    "status": "queued",
    "to": "+1234567890",
    "message": "SMS sent successfully"
}
```

The message sent will be:
`Your Church Attendance Management System verification code is: 123456. This code expires in 10 minutes.`

## Step 5: Using SMS Service Programmatically

You can use the `SMSService` class directly in your Python code:

```python
from message.sms_service import SMSService

# Initialize the service
sms_service = SMSService()

# Send a single SMS
result = sms_service.send_sms(
    to_number="+1234567890",
    message_body="Hello, this is a test message!"
)

# Send bulk SMS
results = sms_service.send_bulk_sms(
    recipient_numbers=["+1234567890", "+0987654321"],
    message_body="Bulk message to all members"
)

# Send verification code
result = sms_service.send_verification_sms(
    phone_number="+1234567890",
    verification_code="123456"
)

# Send attendance reminder
result = sms_service.send_attendance_reminder_sms(
    phone_number="+1234567890",
    event_name="Sunday Service",
    event_time="10:00 AM"
)

# Send generic SMS
result = sms_service.send_generic_sms(
    phone_number="+1234567890",
    message_title="Welcome",
    message_body="Welcome to our church!"
)
```

## Files Created/Modified

1. **Created:** `message/sms_service.py` - SMS service class with all SMS sending logic
2. **Modified:** `apis/settings.py` - Added Twilio configuration
3. **Modified:** `message/views.py` - Added SMS sending views
4. **Modified:** `message/urls.py` - Added SMS endpoints
5. **Modified:** `requirements.txt` - Added twilio package

## Troubleshooting

### "TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN must be set"

**Solution:** Make sure you've set the environment variables or configured them in `settings.py`.

### "Invalid 'To' phone number provided"

**Solution:** Phone numbers must be in E.164 format (e.g., `+1234567890`).

### "Account does not have API access"

**Solution:** Upgrade your Twilio trial account or add funds.

### Test with Trial Accounts

If using a trial account, you can only send SMS to verified phone numbers. Verify your phone number in the Twilio console first.

## Production Considerations

1. **Security:** Use environment variables or a secrets manager (e.g., AWS Secrets Manager, HashiCorp Vault)
2. **Rate Limiting:** Implement rate limiting to prevent abuse
3. **Logging:** Add logging for SMS delivery status
4. **Error Handling:** Implement retry logic for failed messages
5. **Cost Monitoring:** Monitor Twilio usage to avoid unexpected charges

## Additional Resources

- [Twilio Python Documentation](https://www.twilio.com/docs/libraries/python)
- [Twilio SMS API Reference](https://www.twilio.com/docs/sms/api)
- [Twilio Console](https://www.twilio.com/console)
- [Phone Number Formatting](https://www.twilio.com/docs/glossary/what-e-164-phone-number)
