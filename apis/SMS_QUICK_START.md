# Quick Start: Twilio SMS in Django

## 1. Install Package
```bash
pip install twilio==9.4.0
```

## 2. Set Environment Variables
```bash
# Windows PowerShell
$env:TWILIO_ACCOUNT_SID = "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
$env:TWILIO_AUTH_TOKEN = "your_auth_token_here"
$env:TWILIO_PHONE_NUMBER = "+1234567890"
```

## 3. Quick Test

### Using cURL
```bash
curl -X POST http://localhost:8000/message/send-sms/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "phone_number": "+1234567890",
    "message_title": "Test",
    "message_body": "Hello from Django!"
  }'
```

### Using Python
```python
from message.sms_service import SMSService

sms = SMSService()
result = sms.send_sms(
    to_number="+1234567890",
    message_body="Hello from Church System!"
)
print(result)
```

## 4. API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/message/send-sms/` | Send SMS to one person |
| POST | `/message/send-bulk-sms/` | Send SMS to multiple people |
| POST | `/message/send-verification-sms/` | Send verification code |

## 5. Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| "TWILIO_ACCOUNT_SID must be set" | Set environment variables or update settings.py |
| "Invalid 'To' phone number" | Use E.164 format: +1234567890 |
| Can't send to non-verified numbers | Upgrade Twilio trial account |
| SMSService import error | Make sure you're in the `apis/` directory |

## 6. Get Twilio Credentials
1. Go to https://www.twilio.com/console
2. Get Account SID from the dashboard
3. Get Auth Token from the dashboard
4. Create or use your Twilio phone number

## 7. File Reference
- **Service:** `message/sms_service.py`
- **Views:** `message/views.py`
- **URLs:** `message/urls.py`
- **Config:** `apis/settings.py`

## Documentation
Full guide: See `TWILIO_SMS_SETUP.md`
