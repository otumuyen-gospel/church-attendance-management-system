# Email Templates Setup Guide

## Overview

This document explains how to use the email template system with static images in your church attendance management system.

## Directory Structure

```
apis/
├── templates/
│   └── emails/
│       ├── base_email.html                 # Base template for all emails
│       ├── welcome.html                    # Welcome email
│       ├── verification.html               # Email verification template
│       ├── attendance_confirmation.html    # Attendance confirmation
│       └── attendance_report.html          # Attendance report
└── message/
    ├── __init__.py
    └── email_service.py                    # Email service utilities
```

## Configuration

### 1. Environment Setup

Update `apis/settings.py` with your email provider credentials:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.your-provider.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@example.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'noreply@churchattendance.com'

# Site configuration for email links
SITE_URL = 'https://yourdomain.com'  # Production domain
SITE_NAME = 'Church Attendance System'
```

### 2. Email Providers

#### Gmail
```python
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'  # Use app password, not main password
```

#### Mailtrap (Testing)
```python
EMAIL_HOST = 'sandbox.smtp.mailtrap.io'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'your-mailtrap-username'
EMAIL_HOST_PASSWORD = 'your-mailtrap-password'
```

#### SendGrid
```python
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = 'SG.your-sendgrid-key'
```

## Usage Examples

### 1. Send Welcome Email

```python
from message import EmailService

# In your user registration view
user = request.user
EmailService.send_welcome_email(
    user_email=user.email,
    user_name=user.get_full_name(),
    church_name='My Church'
)
```

### 2. Send Verification Email

```python
from django.urls import reverse
from message import EmailService

# Generate verification token (use your auth system)
verification_url = request.build_absolute_uri(
    reverse('verify-email', kwargs={'token': verification_token})
)

EmailService.send_verification_email(
    user_email=user.email,
    user_name=user.first_name,
    verification_url=verification_url
)
```

### 3. Send Attendance Confirmation

```python
from datetime import datetime
from message import EmailService

attendance = Attendance.objects.get(id=attendance_id)
EmailService.send_attendance_notification(
    user_email=attendance.person.contact.email,
    user_name=attendance.person.first_name,
    attendance_date=attendance.attendance_date.strftime('%B %d, %Y'),
    attendance_time=attendance.time_in.strftime('%I:%M %p')
)
```

### 4. Send Attendance Report

```python
from message import EmailService

# Generate report HTML
report_html = """
<table style="width: 100%; border-collapse: collapse;">
    <tr style="background: #f0f0f0;">
        <th style="border: 1px solid #ddd; padding: 10px;">Date</th>
        <th style="border: 1px solid #ddd; padding: 10px;">Status</th>
    </tr>
    <tr>
        <td style="border: 1px solid #ddd; padding: 10px;">2024-01-07</td>
        <td style="border: 1px solid #ddd; padding: 10px;">Present</td>
    </tr>
</table>
"""

EmailService.send_attendance_report(
    user_email=person.contact.email,
    user_name=person.first_name,
    report_html=report_html,
    church_name='My Church'
)
```

### 5. Custom Email with Attachments

```python
from message import EmailService

context = {
    'user_name': 'John',
    'church_name': 'My Church',
    'logo_url': 'https://yourdomain.com/static/images/logo.png',
    'custom_data': 'Your custom data here'
}

# Add attachments (filename, content, mimetype)
attachments = [
    ('report.pdf', pdf_content, 'application/pdf'),
    ('document.docx', docx_content, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
]

EmailService.send_email(
    subject='Custom Email Subject',
    template_name='emails/custom_template.html',  # Your custom template
    context=context,
    recipient_list=['recipient@example.com'],
    attachments=attachments
)
```

## Static Images Setup

### Option 1: External URLs (Recommended)

Store your images in `/static/images/` directory and reference them by full URL:

```html
<!-- In your email template -->
<img src="https://yourdomain.com/static/images/logo.png" alt="Logo" style="max-width: 150px;">
```

This method works best because:
- No file size limits
- Images render reliably in all email clients
- Easy to update images without code changes

### Option 2: Base64 Embedding

For images that must be embedded:

```python
from message import EmailService

image_path = os.path.join(settings.BASE_DIR, 'static/images/logo.png')
logo_base64 = EmailService.get_image_as_base64(image_path)

context = {
    'user_name': 'John',
    'logo_base64': logo_base64
}

EmailService.send_email(
    subject='Email with Embedded Image',
    template_name='emails/welcome.html',
    context=context,
    recipient_list=['user@example.com']
)
```

In your template:
```html
<img src="data:image/png;base64,{{ logo_base64 }}" alt="Logo" style="max-width: 150px;">
```

### Option 3: MIME Multipart (Advanced)

For maximum compatibility with older email clients:

```python
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
import os

context = {
    'user_name': 'John',
    'church_name': 'My Church'
}

html_message = render_to_string('emails/welcome.html', context)

email = EmailMultiAlternatives(
    subject='Welcome',
    body='Welcome to our church',
    from_email='noreply@churchattendance.com',
    to=['user@example.com']
)
email.attach_alternative(html_message, "text/html")

# Attach image
image_path = os.path.join(settings.BASE_DIR, 'static/images/logo.png')
with open(image_path, 'rb') as img:
    email.attach('logo.png', img.read(), mimetype='image/png')

email.send()
```

In your template:
```html
<img src="cid:logo.png" alt="Logo" style="max-width: 150px;">
```

## Creating Custom Email Templates

### Template Inheritance

All email templates should extend `base_email.html`:

```html
{% extends "emails/base_email.html" %}

{% block header_title %}Your Email Title{% endblock %}

{% block content %}
<h2>Hello, {{ user_name }}!</h2>
<p>Your email content here...</p>

<a href="{{ link_url }}" class="cta-button">Call to Action</a>

<div class="divider"></div>

<p>More content here...</p>
{% endblock %}
```

### Available CSS Classes

- `.email-container` - Main container
- `.email-header` - Header section with logo
- `.email-content` - Main content area
- `.cta-button` - Call-to-action button
- `.divider` - Horizontal divider
- `.highlight-box` - Highlighted information box
- `.email-footer` - Footer section

### Template Context Variables

Standard variables available in all templates:
- `{{ logo_url }}` - Church logo URL
- `{{ site_url }}` - Site URL
- `{{ current_year }}` - Current year (via `{% now "Y" %}`)

## Best Practices

1. **Use External URLs for Images**: Store images in static files and reference by URL
2. **Responsive Design**: Use inline styles and mobile-friendly layouts
3. **ALT Text**: Always include alt text for images
4. **Text Fallback**: Provide text content along with HTML emails
5. **Testing**: Test emails in multiple email clients (Gmail, Outlook, Apple Mail, etc.)
6. **Avoid Large Files**: Keep email size under 100KB
7. **Security**: Never expose sensitive data in emails
8. **Unsubscribe**: Include unsubscribe information in footer for marketing emails

## Testing

### Console Backend (Development)

```python
# In settings.py for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

Emails will print to console instead of sending.

### File Backend (Testing)

```python
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = os.path.join(BASE_DIR, 'sent_emails')
```

Emails are saved to files in the `sent_emails` directory.

### With Django Shell

```bash
python manage.py shell
```

```python
from message import EmailService

EmailService.send_welcome_email(
    user_email='test@example.com',
    user_name='Test User',
    church_name='Test Church'
)
```

## Troubleshooting

### Emails not sending

1. Check email credentials in settings.py
2. Verify SMTP host and port
3. Check firewall/network settings
4. Use console backend to verify email generation
5. Check email provider's security settings (allow less secure apps, etc.)

### Images not loading in email client

1. Ensure full HTTPS URL is used
2. Check image file exists at specified path
3. Verify CORS settings if serving from different domain
4. Test in multiple email clients
5. Consider using embedding or base64 encoding

### Template not found error

1. Verify template directory is in TEMPLATES['DIRS'] in settings.py
2. Check template path is correct
3. Ensure `APP_DIRS: True` is set in TEMPLATES configuration
4. Run `python manage.py collectstatic` if using static files

## Integration with Your Existing Code

### In User Registration (auth app)

```python
# auth/views.py
from message import EmailService

class UserRegistrationView(APIView):
    def post(self, request):
        # ... registration logic ...
        user = User.objects.create_user(...)
        
        # Send welcome email
        EmailService.send_welcome_email(
            user_email=user.email,
            user_name=user.get_full_name(),
            church_name='Your Church Name'
        )
        
        return Response({'message': 'User registered successfully'})
```

### In Attendance Tracking (attendance app)

```python
# attendance/views.py
from message import EmailService
from datetime import datetime

class AttendanceCheckInView(APIView):
    def post(self, request):
        # ... check-in logic ...
        attendance = Attendance.objects.create(...)
        
        # Send confirmation
        person = attendance.person
        EmailService.send_attendance_notification(
            user_email=person.contact.email,
            user_name=person.first_name,
            attendance_date=attendance.attendance_date.strftime('%B %d, %Y'),
            attendance_time=attendance.time_in.strftime('%I:%M %p')
        )
        
        return Response({'message': 'Attendance recorded'})
```

### In Reports (report app)

```python
# report/views.py
from message import EmailService

class AttendanceReportView(APIView):
    def get(self, request):
        # ... generate report ...
        report_html = generate_report_html(person)
        
        EmailService.send_attendance_report(
            user_email=person.contact.email,
            user_name=person.first_name,
            report_html=report_html,
            church_name='Your Church Name'
        )
        
        return Response({'message': 'Report sent'})
```

## Next Steps

1. Create `/static/images/` directory and add your church logo
2. Update `SITE_URL` in settings.py to your production domain
3. Configure your email provider credentials
4. Test email functionality using Django shell
5. Integrate EmailService into your existing views
6. Customize email templates with your branding
