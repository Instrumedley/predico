"""
Email service with support for local development, AWS SES, and SendGrid.

For local development, emails are logged to console and optionally saved to files.
For Heroku production, emails are sent via SendGrid (SendGrid add-on).
For AWS deployments, emails can be sent via AWS SES.
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
    """Service for sending emails via SendGrid, AWS SES, or local development."""
    
    def __init__(self):
        """Initialize email service."""
        self.environment = settings.ENVIRONMENT
        self.email_enabled = settings.EMAIL_ENABLED
        self.email_backend = settings.EMAIL_BACKEND
        self.from_email = settings.SES_FROM_EMAIL
        self.frontend_url = settings.FRONTEND_URL
        self.sendgrid_api_key = settings.SENDGRID_API_KEY or os.getenv("SENDGRID_API_KEY")

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

        self._log_configuration()

    def _log_configuration(self) -> None:
        """Log how email is configured for this process (startup diagnostics)."""
        delivery_mode = (
            "inbox (SendGrid)"
            if settings.EMAIL_ENABLED and settings.EMAIL_BACKEND == "sendgrid"
            else "inbox (AWS SES)"
            if settings.delivers_email_to_inbox
            else "local only (console + email_logs/)"
        )
        logger.info(
            "Email service configured",
            environment=self.environment,
            email_backend=self.email_backend,
            email_enabled=self.email_enabled,
            delivery_mode=delivery_mode,
            from_email=self.from_email,
            frontend_url=self.frontend_url,
        )
        if self.environment in ("staging", "production") and self.email_backend == "local":
            logger.warning(
                "ENVIRONMENT is staging/production but EMAIL_BACKEND=local; "
                "verification and reset emails will not reach user inboxes. "
                "Set EMAIL_BACKEND=sendgrid (Heroku) or ses (AWS).",
                environment=self.environment,
            )
        if self.email_backend == "sendgrid" and self.email_enabled and not self.sendgrid_api_key:
            logger.warning(
                "EMAIL_BACKEND=sendgrid but SENDGRID_API_KEY is not set; "
                "add the SendGrid add-on or set the config var.",
            )
        if self.email_backend == "ses" and self.email_enabled and not self.ses_client:
            logger.warning(
                "EMAIL_BACKEND=ses but SES client is not initialized; "
                "check AWS credentials and region.",
            )
    
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
        if self.email_backend == "sendgrid":
            return await self._send_via_sendgrid(to_email, subject, body_text, body_html)
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
    
    async def _send_via_sendgrid(
        self,
        to_email: str,
        subject: str,
        body_text: str,
        body_html: str
    ) -> bool:
        """Send email via SendGrid API."""
        if not self.sendgrid_api_key:
            logger.error("SendGrid API key not configured")
            return False

        try:
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail
        except ImportError:
            logger.error("sendgrid package is not installed")
            return False

        message = Mail(
            from_email=self.from_email,
            to_emails=to_email,
            subject=subject,
            plain_text_content=body_text,
            html_content=body_html,
        )

        try:
            client = SendGridAPIClient(self.sendgrid_api_key)
            response = await asyncio.to_thread(client.send, message)
            logger.info(
                "Email sent via SendGrid",
                email=to_email,
                status_code=response.status_code,
            )
            return 200 <= response.status_code < 300
        except Exception as e:
            logger.error("Failed to send email via SendGrid", email=to_email, error=str(e))
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

    async def send_league_invite_email(
        self,
        email: str,
        league_name: str,
        league_id: int,
        inviter_name: str,
        is_private: bool,
        invite_token: str,
        league_description: Optional[str] = None,
        recipient_name: Optional[str] = None,
    ) -> bool:
        """Send a league invitation email with a link to accept the invite."""
        join_url = f"{self.frontend_url.rstrip('/')}/leagues/{league_id}?invite={invite_token}"
        context = {
            "league_name": league_name,
            "league_description": league_description,
            "inviter_name": inviter_name,
            "join_url": join_url,
            "is_private": is_private,
            "recipient_name": recipient_name,
        }
        html_content, text_content = self._render_template("league_invite", context)
        return await self._send_email(
            to_email=email,
            subject=f"{inviter_name} invited you to join {league_name} on Predico",
            body_text=text_content,
            body_html=html_content,
        )


# Singleton instance
email_service = EmailService()
