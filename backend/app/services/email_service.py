"""
Email service with support for local development and AWS SES.

For local development, emails are logged to console and optionally saved to files.
For production, emails are sent via AWS SES.
"""
import asyncio
import boto3
import os
from pathlib import Path
from typing import Optional, Dict, Any
from jinja2 import Environment, FileSystemLoader, select_autoescape
from botocore.exceptions import ClientError
from app.core.config import settings
import structlog

logger = structlog.get_logger(__name__)


class EmailService:
    """Service for sending emails via AWS SES or local development."""
    
    def __init__(self):
        """Initialize email service."""
        self.email_enabled = settings.EMAIL_ENABLED
        self.email_backend = settings.EMAIL_BACKEND
        self.from_email = settings.SES_FROM_EMAIL
        self.frontend_url = settings.FRONTEND_URL
        
        # Initialize Jinja2 template environment
        template_dir = Path(__file__).parent.parent / "templates" / "emails"
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=select_autoescape(['html', 'xml'])
        )
        
        # Initialize AWS SES client if using SES backend
        if self.email_backend == "ses" and self.email_enabled:
            self.ses_client = boto3.client(
                'ses',
                region_name=settings.AWS_REGION
            )
        else:
            self.ses_client = None
        
        # Create email logs directory for local development
        if self.email_backend == "local":
            self.email_log_dir = Path(__file__).parent.parent.parent / "email_logs"
            self.email_log_dir.mkdir(exist_ok=True)
    
    def _render_template(self, template_name: str, context: Dict[str, Any]) -> tuple[str, str]:
        """
        Render email template with context variables.
        
        Args:
            template_name: Name of the template (without extension)
            context: Dictionary of variables to inject into template
            
        Returns:
            Tuple of (html_content, text_content)
        """
        html_template = self.jinja_env.get_template(f"{template_name}.html")
        text_template = self.jinja_env.get_template(f"{template_name}.txt")
        
        html_content = html_template.render(**context)
        text_content = text_template.render(**context)
        
        return html_content, text_content
    
    async def _send_email(
        self,
        to_email: str,
        subject: str,
        body_text: str,
        body_html: str
    ) -> bool:
        """
        Send email via configured backend.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body_text: Plain text body
            body_html: HTML body
            
        Returns:
            True if email sent successfully, False otherwise
        """
        if not self.email_enabled:
            logger.info("Email sending is disabled", email=to_email)
            return False
        
        if self.email_backend == "ses":
            return await self._send_via_ses(to_email, subject, body_text, body_html)
        else:
            return self._send_via_local(to_email, subject, body_text, body_html)
    
    async def _send_via_ses(
        self,
        to_email: str,
        subject: str,
        body_text: str,
        body_html: str
    ) -> bool:
        """Send email via AWS SES."""
        if not self.ses_client:
            logger.error("SES client not initialized")
            return False
        
        try:
            response = await asyncio.to_thread(
                self.ses_client.send_email,
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
            logger.info("Email sent via SES", email=to_email, message_id=response.get('MessageId'))
            return True
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "")
            error_message = e.response.get("Error", {}).get("Message", "")
            logger.error(
                "Failed to send email via SES",
                email=to_email,
                error_code=error_code,
                error_message=error_message
            )
            return False
        except Exception as e:
            logger.error("Failed to send email via SES", email=to_email, error=str(e))
            return False
    
    def _send_via_local(
        self,
        to_email: str,
        subject: str,
        body_text: str,
        body_html: str
    ) -> bool:
        """Send email via local development (console + file)."""
        # Log to console
        logger.info(
            "📧 EMAIL (Local Development)",
            to=to_email,
            subject=subject
        )
        print("\n" + "="*80)
        print(f"📧 EMAIL (Local Development)")
        print(f"To: {to_email}")
        print(f"Subject: {subject}")
        print("-"*80)
        print("HTML Content:")
        print(body_html)
        print("-"*80)
        print("Text Content:")
        print(body_text)
        print("="*80 + "\n")
        
        # Save to file for easy viewing
        try:
            email_file = self.email_log_dir / f"email_{to_email.replace('@', '_at_')}_{subject.replace(' ', '_')}.html"
            with open(email_file, 'w', encoding='utf-8') as f:
                f.write(f"<h2>To: {to_email}</h2>\n")
                f.write(f"<h3>Subject: {subject}</h3>\n")
                f.write("<hr>\n")
                f.write(body_html)
            logger.info("Email saved to file", file=str(email_file))
        except Exception as e:
            logger.warning("Failed to save email to file", error=str(e))
        
        return True
    
    async def send_verification_email(self, email: str, token: str, username: Optional[str] = None) -> bool:
        """
        Send email verification email.
        
        Args:
            email: Recipient email address
            token: Verification token
            username: Optional username for personalization
            
        Returns:
            True if email sent successfully, False otherwise
        """
        verification_url = f"{self.frontend_url}/verify-email?token={token}"
        
        context = {
            "verification_url": verification_url,
            "username": username,
        }
        
        html_content, text_content = self._render_template("verify_email", context)
        
        return await self._send_email(
            to_email=email,
            subject="Verify your email address - Predico",
            body_text=text_content,
            body_html=html_content
        )
    
    async def send_password_reset_email(self, email: str, token: str, username: Optional[str] = None) -> bool:
        """
        Send password reset email.
        
        Args:
            email: Recipient email address
            token: Password reset token
            username: Optional username for personalization
            
        Returns:
            True if email sent successfully, False otherwise
        """
        reset_url = f"{self.frontend_url}/reset-password?token={token}"
        
        context = {
            "reset_url": reset_url,
            "username": username,
        }
        
        html_content, text_content = self._render_template("reset_password", context)
        
        return await self._send_email(
            to_email=email,
            subject="Reset your password - Predico",
            body_text=text_content,
            body_html=html_content
        )


# Singleton instance
email_service = EmailService()
