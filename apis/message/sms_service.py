from twilio.rest import Client
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
import threading

class SMSService(threading.Thread):
    """Service for handling SMS operations via Twilio."""

    def __init__(self, to_number=None, message_body=None, recipient_numbers=None, message_title=None, type=None):
        self.to_number = to_number
        self.message_body = message_body
        self.recipient_numbers = recipient_numbers
        self.message_title = message_title
        self.type = type
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

        threading.Thread.__init__(self)

    def run(self):
        try:
            if self.type == 'bulk': 
                result = self.send_bulk_sms()
            elif self.type == 'generic':
                result = self.send_generic_sms()
        except Exception as e:
            print(f"Error in SMSService thread: {str(e)}")

    def send_sms(self):
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
                body=self.message_body,
                from_=self.from_number,
                to=self.to_number
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

    def send_bulk_sms(self):
        """
        Send SMS to multiple recipients.
        
        Args:
            recipient_numbers: List of phone numbers (e.g., ['+1234567890', '+0987654321'])
            message_body: The SMS message content
            message_title: Title/subject of the message
        
        Returns:
            Dictionary with results for each recipient
        """
        results = {
            'total': len(self.recipient_numbers),
            'successful': 0,
            'failed': 0,
            'details': []
        }
        
        for to_number in self.recipient_numbers:
            self.to_number = to_number
            result = self.send_sms()
            results['details'].append(result)
            
            if result['success']:
                results['successful'] += 1
            else:
                results['failed'] += 1
        
        return results

    def send_generic_sms(self):
        """
        Send a generic SMS message.
        
        Args:
            phone_number: Recipient's phone number
            message_title: Title/subject of the message
            message_body: The message content
        
        Returns:
            Response from send_sms method
        """
        full_message = f"{self.message_title}: {self.message_body}"
        self.message_body = full_message
        return self.send_sms()
