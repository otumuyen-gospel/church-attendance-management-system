import os
import base64
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

class EmailService:
    """Service for handling email operations with embedded images and templates."""

    @staticmethod
    def get_image_as_base64(image_path):
        """Convert image file to base64 string for embedding in email."""
        try:
            with open(image_path, 'rb') as img:
                return base64.b64encode(img.read()).decode('utf-8')
        except FileNotFoundError:
            return None

    @staticmethod
    def get_image_url(image_name):
        """Get full URL for image (for external URL method)."""
        return f"{settings.SITE_URL}/static/images/{image_name}"

    @staticmethod
    def send_email(
        subject,
        template_name,
        context,
        recipient_list,
        from_email=None,
        embed_images=False,
        attachments=None
    ):
        """
        Send HTML email with optional embedded images.
        
        Args:
            subject: Email subject
            template_name: Template path (e.g., 'emails/welcome.html')
            context: Dictionary of template context variables
            recipient_list: List of recipient email addresses
            from_email: Sender email (defaults to DEFAULT_FROM_EMAIL)
            embed_images: If True, convert static images to base64
            attachments: List of tuples (filename, content, mimetype)
        
        Returns:
            Number of messages sent
        """
        if from_email is None:
            from_email = settings.DEFAULT_FROM_EMAIL

        # Render template
        html_message = render_to_string(template_name, context)
        text_message = strip_tags(html_message)

        # Create email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_message,
            from_email=from_email,
            to=recipient_list
        )
        email.attach_alternative(html_message, "text/html")

        # Add attachments if provided
        if attachments:
            for filename, content, mimetype in attachments:
                email.attach(filename, content, mimetype)

        return email.send()

    @staticmethod
    def send_welcome_email(user_email, user_name, church_name, roles):
        """Send welcome email to new user."""
        context = {
            'user_name': user_name,
            'church_name': church_name,
            'roles':roles,
            'site_url': settings.SITE_URL,
            'logo_url': EmailService.get_image_url('logo.jpg'),
        }
        
        return EmailService.send_email(
            subject=f"Welcome to {church_name} Attendance System",
            template_name='emails/welcome.html',
            context=context,
            recipient_list=[user_email]
        )

    @staticmethod
    def send_verification_email(user_email, user_name, verification_code):
        """Send email verification link."""
        context = {
            'user_name': user_name,
            'verification_code': verification_code,
            'logo_url': EmailService.get_image_url('logo.jpg'),
        }
        
        return EmailService.send_email(
            subject="Verify Your Email Address",
            template_name='emails/verification.html',
            context=context,
            recipient_list=[user_email]
        )

    @staticmethod
    def send_generic_email(user_email, user_name, title, detail, church_name,):
        """Send welcome email to new user."""
        context = {
            'user_name': user_name,
            'church_name': church_name,
            'detail': detail,
            'title':title,
            'site_url': settings.SITE_URL,
            'logo_url': EmailService.get_image_url('logo.jpg'),
        }
        
        return EmailService.send_email(
            subject=title,
            template_name='emails/generic.html',
            context=context,
            recipient_list=[user_email]
        ) 
  
