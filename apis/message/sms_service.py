from twilio.rest import Client
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


class SMSService:
    """Service for handling SMS operations via Twilio."""

    def __init__(self):
        """Initialize Twilio client with credentials from settings."""
        if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
            raise ImproperlyConfigured(
                'TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN must be set in settings or environment variables.'
            )
        
        if not settings.TWILIO_PHONE_NUMBER:
            raise ImproperlyConfigured(
                'TWILIO_PHONE_NUMBER must be set in settings or environment variables.'
            )
        
        self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        self.from_number = settings.TWILIO_PHONE_NUMBER

    def send_sms(self, to_number, message_body):
        """
        Send a single SMS message.
        
        Args:
            to_number: Recipient's phone number (e.g., '+1234567890')
            message_body: The SMS message content
        
        Returns:
            SMS message object with details like SID, status, etc.
            
        Raises:
            Exception: If SMS fails to send
        """
        try:
            message = self.client.messages.create(
                body=message_body,
                from_=self.from_number,
                to=to_number
            )
            return {
                'success': True,
                'message_sid': message.sid,
                'status': message.status,
                'to': message.to,
                'message': 'SMS sent successfully'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to send SMS'
            }

    def send_bulk_sms(self, recipient_numbers, message_body):
        """
        Send SMS to multiple recipients.
        
        Args:
            recipient_numbers: List of phone numbers (e.g., ['+1234567890', '+0987654321'])
            message_body: The SMS message content
        
        Returns:
            Dictionary with results for each recipient
        """
        results = {
            'total': len(recipient_numbers),
            'successful': 0,
            'failed': 0,
            'details': []
        }
        
        for to_number in recipient_numbers:
            result = self.send_sms(to_number, message_body)
            results['details'].append(result)
            
            if result['success']:
                results['successful'] += 1
            else:
                results['failed'] += 1
        
        return results

    def send_generic_sms(self, phone_number, message_title, message_body):
        """
        Send a generic SMS message.
        
        Args:
            phone_number: Recipient's phone number
            message_title: Title/subject of the message
            message_body: The message content
        
        Returns:
            Response from send_sms method
        """
        full_message = f"{message_title}: {message_body}"
        return self.send_sms(phone_number, full_message)
