"""
Email service using AWS SNS/SES for sending emails.
"""
import boto3
import os
from typing import Optional
from app.core.config import settings
import structlog

logger = structlog.get_logger()


class EmailService:
    """Service for sending emails via AWS SES."""
    
    def __init__(self):
        """Initialize AWS SES client."""
        self.ses_client = boto3.client(
            'ses',
            region_name=settings.AWS_REGION,
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        )
        self.from_email = os.getenv('SES_FROM_EMAIL', 'noreply@predico.com')
    
    def send_verification_email(self, email: str, token: str) -> bool:
        """
        Send email verification email.
        
        Args:
            email: Recipient email address
            token: Verification token
            
        Returns:
            True if email sent successfully, False otherwise
        """
        verification_url = f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/verify-email?token={token}"
        
        subject = "Verify your email address - Predico"
        body_html = f"""
        <html>
        <body>
            <h2>Welcome to Predico!</h2>
            <p>Please verify your email address by clicking the link below:</p>
            <p><a href="{verification_url}">Verify Email</a></p>
            <p>Or copy and paste this link into your browser:</p>
            <p>{verification_url}</p>
            <p>This link will expire in 24 hours.</p>
        </body>
        </html>
        """
        
        body_text = f"""
        Welcome to Predico!
        
        Please verify your email address by visiting this link:
        {verification_url}
        
        This link will expire in 24 hours.
        """
        
        return self._send_email(email, subject, body_text, body_html)
    
    def send_password_reset_email(self, email: str, token: str) -> bool:
        """
        Send password reset email.
        
        Args:
            email: Recipient email address
            token: Password reset token
            
        Returns:
            True if email sent successfully, False otherwise
        """
        reset_url = f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/reset-password?token={token}"
        
        subject = "Reset your password - Predico"
        body_html = f"""
        <html>
        <body>
            <h2>Password Reset Request</h2>
            <p>You requested to reset your password. Click the link below to reset it:</p>
            <p><a href="{reset_url}">Reset Password</a></p>
            <p>Or copy and paste this link into your browser:</p>
            <p>{reset_url}</p>
            <p>This link will expire in 1 hour.</p>
            <p>If you didn't request this, please ignore this email.</p>
        </body>
        </html>
        """
        
        body_text = f"""
        Password Reset Request
        
        You requested to reset your password. Visit this link to reset it:
        {reset_url}
        
        This link will expire in 1 hour.
        
        If you didn't request this, please ignore this email.
        """
        
        return self._send_email(email, subject, body_text, body_html)
    
    def _send_email(
        self,
        to_email: str,
        subject: str,
        body_text: str,
        body_html: str
    ) -> bool:
        """
        Send email via AWS SES.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body_text: Plain text body
            body_html: HTML body
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            response = self.ses_client.send_email(
                Source=self.from_email,
                Destination={'ToAddresses': [to_email]},
                Message={
                    'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                    'Body': {
                        'Text': {'Data': body_text, 'Charset': 'UTF-8'},
                        'Html': {'Data': body_html, 'Charset': 'UTF-8'},
                    }
                }
            )
            logger.info("Email sent successfully", email=to_email, message_id=response['MessageId'])
            return True
        except Exception as e:
            logger.error("Failed to send email", email=to_email, error=str(e))
            return False


# Singleton instance
email_service = EmailService()

