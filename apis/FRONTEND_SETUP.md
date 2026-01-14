# Face Recognition Frontend Setup

## Quick Start (Recommended)

### For Multi-Device Access with HTTPS:

**Windows (PowerShell):**
```powershell
cd apis
.\run_https_server.ps1
```

**Windows (Command Prompt):**
```cmd
cd apis
run_https_server.bat
```

**Linux/Mac:**
```bash
cd apis
python manage.py runserver_plus 0.0.0.0:8000
```

Then access from any device:
```
https://YOUR_SERVER_IP:8000/user_faces/frontend/
```

Example: `https://192.168.1.100:8000/user_faces/frontend/`

## Why HTTPS is Required

Modern web browsers restrict camera access for security reasons. Camera access (WebRTC getUserMedia API) only works over:

1. **HTTPS** - Secure connections
2. **localhost/127.0.0.1** - Local machine only

If you try to access from another device using `http://192.168.x.x:8000`, the browser will block camera access.

## Setup Steps

### 1. Generate SSL Certificate (Already Done)
```bash
python generate_cert.py
```
This creates:
- `certs/localhost.crt` - SSL Certificate
- `certs/localhost.key` - Private Key

### 2. Install Required Packages
```bash
pip install django-extensions pyopenssl
```

### 3. Add to Django Settings
Already added to `apis/settings.py`:
```python
INSTALLED_APPS = [
    'django_extensions',
    ...
]
```

### 4. Run the Server
```bash
# With HTTPS support
python manage.py runserver_plus 0.0.0.0:8000

# Or with specific cert files
python manage.py runserver_plus --cert-file certs/localhost.crt --key-file certs/localhost.key 0.0.0.0:8000
```

### 5. Access from Browser

**Same Device:**
```
https://localhost:8000/user_faces/frontend/
```

**Another Device (on same network):**
```
https://192.168.1.100:8000/user_faces/frontend/
```
(Replace 192.168.1.100 with your server's IP)

### 6. Accept the Security Warning

When you first access the URL, your browser will show a warning:

**Chrome/Edge:**
1. You'll see "Your connection is not private"
2. Click "Advanced"
3. Click "Proceed to [IP address]" at the bottom

**Firefox:**
1. Click "Advanced..."
2. Click "Accept the Risk and Continue"

**Safari:**
1. Click "Show Details"
2. Click "Visit this website"

This warning appears because we're using a self-signed certificate. In production, you would use a real certificate from a Certificate Authority.

## Usage

1. **Enter Server IP Address:** In the API URL field, enter your server's IP (e.g., `https://192.168.1.100:8000`)
2. **Start Camera:** Click "Start Camera" button
3. **Grant Permissions:** Allow camera access when the browser prompts
4. **Auto-Capture:** Enable to automatically send frames to the server
5. **Monitor Results:** View recognition results in real-time

## Troubleshooting

### Camera Access Still Blocked
- ✓ Make sure you're using HTTPS (URL starts with `https://`)
- ✓ Check that `runserver_plus` is running (not regular `runserver`)
- ✓ Verify django-extensions is installed: `pip list | grep django-extensions`
- ✓ Try clearing browser cache and cookies for the site

### "Certificate is not valid" / "Connection is not private"
- This is normal for self-signed certificates
- Click "Advanced" and "Proceed anyway"
- The certificate is valid, just not from a trusted authority

### Server won't start
- Check that port 8000 is not in use
- Try a different port: `python manage.py runserver_plus 0.0.0.0:8001`
- Make sure pyopenssl is installed: `pip install pyopenssl`

### Camera still not working on another device
- Ensure both devices are on the same network
- Check firewall allows port 8000
- Use the correct server IP address
- Try accessing the frontend first: `https://192.168.1.100:8000/user_faces/frontend/`

## API Integration

The frontend sends frames to the API endpoint:
```
POST /user_faces/recognition/
```

With multipart form data:
- `image`: JPEG image file
- `serviceId`: (optional) Service identifier for attendance tracking

The API expects this endpoint to be available and returns:
```json
{
  "success": true
}
```

or

```json
{
  "success": false,
  "error": "No face detected"
}
```

## Security Notes

### For Development
- Self-signed certificates are fine
- `ALLOWED_HOSTS = ['*']` allows any host
- `DEBUG = True` shows detailed error pages
- `CORS_ALLOW_ALL_ORIGINS = True` allows all origins

### For Production
- Use real SSL certificates from Let's Encrypt or similar
- Restrict `ALLOWED_HOSTS` to your domain
- Set `DEBUG = False`
- Configure specific `CORS_ALLOWED_ORIGINS`
- Use a production WSGI server (Gunicorn, uWSGI, etc.)
- Use a reverse proxy (Nginx, Apache) for HTTPS termination
- Enable HTTPS strict transport security headers

## Files Reference

- **face_frontend.html** - Main frontend interface
- **CAMERA_SETUP.md** - Detailed camera setup guide
- **generate_cert.py** - SSL certificate generator
- **run_https_server.bat** - Windows batch startup script
- **run_https_server.ps1** - Windows PowerShell startup script
- **certs/localhost.crt** - SSL certificate (generated)
- **certs/localhost.key** - SSL private key (generated)

## Next Steps

1. Run the HTTPS server using the startup scripts
2. Access the frontend from your device
3. Grant camera permissions
4. Test face recognition functionality
5. Configure the API URL if on different network

For any issues, check the browser's developer console (F12) for detailed error messages.
