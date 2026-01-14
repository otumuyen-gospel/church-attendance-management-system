# Camera Access Fix - Summary

## The Problem
❌ Camera access was blocked when accessing from another device using HTTP.

Reason: Browsers restrict camera access to HTTPS or localhost for security.

## The Solution
✅ Set up HTTPS with a self-signed SSL certificate.

## What Was Done

### 1. Generated SSL Certificate
- Location: `apis/certs/localhost.crt` and `apis/certs/localhost.key`
- Valid for 365 days
- Covers: localhost, 127.0.0.1, and *.local

### 2. Installed Required Packages
- `django-extensions` - Enables `runserver_plus` command with HTTPS support
- `pyopenssl` - Provides SSL/TLS support
- `cryptography` - Used for certificate generation

### 3. Updated Django Settings
- Added `'django_extensions'` to `INSTALLED_APPS`

### 4. Created Startup Scripts
- `run_https_server.bat` - Windows Command Prompt
- `run_https_server.ps1` - Windows PowerShell
- Scripts automatically generate certs if missing

### 5. Created Documentation
- `CAMERA_SETUP.md` - Detailed camera setup guide
- `FRONTEND_SETUP.md` - Complete setup and usage guide

## How to Use Now

### Option 1: Use Startup Script (Easiest)
**Windows:**
```
cd apis
.\run_https_server.ps1
```

### Option 2: Manual Command
```bash
cd apis
python manage.py runserver_plus 0.0.0.0:8000
```

### Option 3: With Specific Certs
```bash
cd apis
python manage.py runserver_plus --cert-file certs/localhost.crt --key-file certs/localhost.key 0.0.0.0:8000
```

## Access the App

### From Same Device
```
https://localhost:8000/user_faces/frontend/
```

### From Another Device (on same network)
```
https://192.168.1.100:8000/user_faces/frontend/
```
Replace `192.168.1.100` with your server's actual IP address.

## Browser Security Warning

When you access the HTTPS URL for the first time, your browser will show a security warning because the certificate is self-signed (not from a trusted authority).

**This is expected and normal for development.**

Simply click:
- **Chrome/Edge:** "Advanced" → "Proceed to [IP address]"
- **Firefox:** "Advanced..." → "Accept the Risk and Continue"
- **Safari:** "Show Details" → "Visit this website"

## Key Features of This Setup

✅ **Multi-device:** Access from any device on the network
✅ **No external certificates:** Self-signed cert included
✅ **Simple startup:** Just run the script
✅ **Auto-generation:** Certs are generated if missing
✅ **Secure:** Uses HTTPS like production servers
✅ **Development-friendly:** Self-signed cert warnings are expected

## Testing Checklist

- [ ] Run `.\run_https_server.ps1` (or the startup script for your OS)
- [ ] Server starts successfully
- [ ] Browser shows HTTPS in the URL bar
- [ ] Accept the certificate warning
- [ ] Click "Start Camera"
- [ ] Allow camera access when prompted
- [ ] Camera feed appears in the video element
- [ ] Enable "Auto-capture" to test sending frames to the API

## Next Steps

1. **Test locally first:** Open `https://localhost:8000/user_faces/frontend/` on the same machine
2. **Test on another device:** Use the server's IP address
3. **Configure API URL:** Make sure to set the correct server IP in the settings
4. **Monitor the API:** Check server logs for incoming requests

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Cannot read properties of undefined" | Reload the page and check browser console |
| "Camera access not accepted on this browser" | Make sure you're using HTTPS (check URL starts with `https://`) |
| "Connection is not private" | This is normal - click "Advanced" then "Proceed" |
| Camera still blocked after HTTPS | Clear browser cache, try in incognito mode, or restart browser |
| Port 8000 already in use | Kill the process or use different port: `python manage.py runserver_plus 0.0.0.0:8001` |

## Files Modified/Created

### Created Files:
- `apis/generate_cert.py` - Certificate generator
- `apis/run_https_server.bat` - Windows startup script
- `apis/run_https_server.ps1` - PowerShell startup script
- `apis/certs/localhost.crt` - SSL certificate
- `apis/certs/localhost.key` - SSL private key
- `faces/CAMERA_SETUP.md` - Detailed setup guide
- `FRONTEND_SETUP.md` - Complete documentation

### Modified Files:
- `apis/settings.py` - Added django_extensions
- `faces/face_frontend.html` - Better error handling

## Production Considerations

For production deployment, you'll want to:
1. Use a real SSL certificate from Let's Encrypt or similar
2. Restrict `ALLOWED_HOSTS` to your domain
3. Set `DEBUG = False`
4. Use a production WSGI server (Gunicorn, uWSGI)
5. Configure a reverse proxy (Nginx, Apache)
6. Set up proper CORS configuration

See `FRONTEND_SETUP.md` for production setup details.

---

**You're all set!** The camera access issue is now resolved. Simply run the startup script and access the app over HTTPS.
