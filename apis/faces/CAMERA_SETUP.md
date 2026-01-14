# Face Recognition Frontend - Setup Guide

## Camera Access Issue

Camera access in web browsers is restricted for security reasons. You can only use it via:
1. **HTTPS** (secure connection)
2. **localhost/127.0.0.1** (local machine only)

If you're accessing from another device on the network using an IP address (e.g., 192.168.1.100), the browser will block camera access in HTTP mode.

## Solutions

### Solution 1: Use HTTPS (Recommended for Multi-Device)

#### Prerequisites
- SSL certificate already generated (see below)

#### Step 1: Generate SSL Certificate
A certificate has already been generated at:
```
apis/certs/localhost.crt
apis/certs/localhost.key
```

If not present, run:
```bash
python generate_cert.py
```

#### Step 2: Run Server with HTTPS
```bash
cd apis
python manage.py runserver_plus --cert-file certs/localhost.crt --key-file certs/localhost.key 0.0.0.0:8000
```

Or simpler (if django-extensions is installed):
```bash
cd apis
python manage.py runserver_plus
```

#### Step 3: Access the Frontend
- From same device: `https://localhost:8000/user_faces/frontend/`
- From another device: `https://YOUR_SERVER_IP:8000/user_faces/frontend/`
  - Example: `https://192.168.1.100:8000/user_faces/frontend/`

#### Step 4: Accept the Security Warning
1. You'll see a browser warning about an untrusted certificate
2. Click "Advanced"
3. Click "Proceed to [IP]" or "Accept the risk and continue"
4. This is normal for self-signed certificates in development

### Solution 2: Use localhost Only (Single Device)

If you're testing on the same device:

```bash
cd apis
python manage.py runserver localhost:8000
```

Then access:
```
http://localhost:8000/user_faces/frontend/
```

This works in HTTP mode but only from the same machine.

### Solution 3: Add to HTTPS Exceptions (Edge/Chrome)

For Chrome/Edge, you can temporarily allow insecure localhost:

1. Open `chrome://flags/#unsafely-treat-insecure-origin-as-secure` in Chrome
2. Or `edge://flags/#unsafely-treat-insecure-origin-as-secure` in Edge
3. Add your IP: `http://YOUR_IP:8000`
4. Relaunch the browser

**Note:** This is NOT recommended for production and only works in certain browsers.

## Troubleshooting

### Still Getting "Camera access not supported"
1. Ensure you're using HTTPS (check the URL starts with `https://`)
2. Make sure django-extensions is installed: `pip install django-extensions`
3. Check that the server started successfully with HTTPS

### Browser Still Shows Warning
- This is normal with self-signed certificates
- Click "Advanced" then "Proceed" to continue
- The warning appears only once per certificate

### Camera Permission Denied
1. Check browser settings - allow camera access for the site
2. Some browsers show a popup - make sure to click "Allow"
3. Restart the browser if it still doesn't work

### Different Error: "No camera found"
- Your device doesn't have a camera
- Or the camera is in use by another application
- Or the camera driver is not installed

## Installation Verification

Check if everything is set up correctly:

```bash
# Check if certs exist
ls apis/certs/
# Should show: localhost.crt  localhost.key

# Check if django-extensions is installed
pip list | grep django-extensions
# Should show: django-extensions

# Check if pyopenssl is installed
pip list | grep pyopenssl
# Should show: pyopenssl
```

## Running in Production

For production, you should:

1. **Use a real SSL certificate** from a Certificate Authority (Let's Encrypt, etc.)
2. **Update ALLOWED_HOSTS** in settings.py to only allow your domain
3. **Set DEBUG = False** in settings.py
4. **Use a production WSGI server** (Gunicorn, uWSGI, etc.) with HTTPS
5. **Use a reverse proxy** (Nginx, Apache) to handle HTTPS

Example with Gunicorn + HTTPS:
```bash
gunicorn --certfile=/path/to/cert.pem --keyfile=/path/to/key.pem apis.wsgi:application
```

## Quick Start

### For Development (Multi-Device with HTTPS):
```bash
cd apis
python manage.py runserver_plus 0.0.0.0:8000
```

Then access from any device:
```
https://YOUR_SERVER_IP:8000/user_faces/frontend/
```

### For Testing (Single Device with HTTP):
```bash
cd apis
python manage.py runserver localhost:8000
```

Then access:
```
http://localhost:8000/user_faces/frontend/
```
