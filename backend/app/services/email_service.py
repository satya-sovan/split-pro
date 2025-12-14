"""
Email service for sending transactional emails
"""
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from jinja2 import Environment, FileSystemLoader
import os

from app.core.config import settings
from app.models.models import User


class EmailService:
    """Service for sending emails via SMTP"""

    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT or 587
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.SMTP_FROM_EMAIL or "noreply@splitpro.app"

        # Setup Jinja2 for email templates
        template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates', 'emails')
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """
        Send an email

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML body
            text_content: Plain text body (optional)

        Returns:
            True if sent successfully
        """
        if not self.smtp_host:
            print("SMTP not configured, skipping email")
            return False

        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email

            if text_content:
                msg.attach(MIMEText(text_content, 'plain'))
            msg.attach(MIMEText(html_content, 'html'))

            await aiosmtplib.send(
                msg,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_user,
                password=self.smtp_password,
                start_tls=True
            )

            return True

        except Exception as e:
            print(f"Error sending email: {e}")
            return False

    async def send_invite_email(
        self,
        to_email: str,
        from_name: str
    ) -> bool:
        """
        Send invitation email to join SplitPro

        Args:
            to_email: Email of person being invited
            from_name: Name of person sending invite

        Returns:
            True if sent successfully
        """
        subject = f"{from_name} invited you to SplitPro"

        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2>You're invited to SplitPro!</h2>
                <p><strong>{from_name}</strong> has invited you to join SplitPro to split expenses together.</p>
                
                <p>SplitPro makes it easy to:</p>
                <ul>
                    <li>Track shared expenses</li>
                    <li>Split bills fairly</li>
                    <li>Settle up with friends</li>
                </ul>
                
                <p style="margin-top: 30px;">
                    <a href="{settings.CORS_ORIGINS[0]}/auth/register?email={to_email}" 
                       style="background-color: #4CAF50; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; display: inline-block;">
                        Join SplitPro
                    </a>
                </p>
                
                <p style="color: #666; margin-top: 30px;">
                    If the button doesn't work, copy and paste this link:<br>
                    {settings.CORS_ORIGINS[0]}/auth/register?email={to_email}
                </p>
            </body>
        </html>
        """

        text_content = f"""
        You're invited to SplitPro!
        
        {from_name} has invited you to join SplitPro to split expenses together.
        
        Visit: {settings.CORS_ORIGINS[0]}/auth/register?email={to_email}
        """

        return await self.send_email(to_email, subject, html_content, text_content)

    async def send_feedback_email(
        self,
        feedback: str,
        user: User
    ) -> bool:
        """
        Send user feedback to support email

        Args:
            feedback: User's feedback text
            user: User who submitted feedback

        Returns:
            True if sent successfully
        """
        support_email = settings.SUPPORT_EMAIL or self.from_email
        subject = f"Feedback from {user.name or user.email}"

        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>New Feedback Received</h2>
                <p><strong>From:</strong> {user.name} ({user.email})</p>
                <p><strong>User ID:</strong> {user.id}</p>
                <p><strong>Feedback:</strong></p>
                <div style="background-color: #f5f5f5; padding: 15px; border-radius: 4px; margin-top: 10px;">
                    {feedback}
                </div>
            </body>
        </html>
        """

        text_content = f"""
        New Feedback Received
        
        From: {user.name} ({user.email})
        User ID: {user.id}
        
        Feedback:
        {feedback}
        """

        return await self.send_email(support_email, subject, html_content, text_content)

    async def send_magic_link_email(
        self,
        to_email: str,
        magic_link: str
    ) -> bool:
        """
        Send magic link for passwordless login

        Args:
            to_email: User's email
            magic_link: Magic link URL

        Returns:
            True if sent successfully
        """
        subject = "Your SplitPro Login Link"

        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2>Login to SplitPro</h2>
                <p>Click the button below to log in to your SplitPro account:</p>
                
                <p style="margin-top: 30px;">
                    <a href="{magic_link}" 
                       style="background-color: #4CAF50; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; display: inline-block;">
                        Log In to SplitPro
                    </a>
                </p>
                
                <p style="color: #666; margin-top: 30px;">
                    This link will expire in 1 hour.
                </p>
                
                <p style="color: #666;">
                    If you didn't request this link, you can safely ignore this email.
                </p>
            </body>
        </html>
        """

        text_content = f"""
        Login to SplitPro
        
        Click this link to log in: {magic_link}
        
        This link will expire in 1 hour.
        
        If you didn't request this link, you can safely ignore this email.
        """

        return await self.send_email(to_email, subject, html_content, text_content)


# Global service instance
email_service = EmailService()

