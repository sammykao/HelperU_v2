
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional, List
from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailUtils:
    """Service for sending emails"""
    
    def __init__(self):
        self.sender = settings.EMAIL_SENDER
        self.password = settings.EMAIL_PASSWORD
        self.server = settings.SMTP_SERVER
        self.port = settings.SMTP_PORT
    

    def send_email(
        self,
        to_email: str, 
        subject: str, 
        body: str, 
        is_html: bool = False,
        cc_emails: Optional[List[str]] = None,
        bcc_emails: Optional[List[str]] = None,
        attachments: Optional[List[str]] = None
    ) -> bool:
        """
        Send email via Gmail SMTP
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body content
            is_html: Whether the body is HTML format
            cc_emails: List of CC email addresses
            bcc_emails: List of BCC email addresses
            attachments: List of file paths to attach
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.sender
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add CC and BCC if provided
            if cc_emails:
                msg['Cc'] = ', '.join(cc_emails)
            if bcc_emails:
                msg['Bcc'] = ', '.join(bcc_emails)
            
            # Add body
            if is_html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))
            
            # Add attachments if provided
            if attachments:
                for file_path in attachments:
                    try:
                        with open(file_path, "rb") as attachment:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(attachment.read())
                        
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {file_path.split("/")[-1]}'
                        )
                        msg.attach(part)
                    except Exception as e:
                        logger.error(f"Failed to attach file {file_path}: {e}")
                        continue
            
            # Create SMTP session
            server = smtplib.SMTP(self.server, self.port)
            server.starttls()  # Enable security
            server.login(self.sender, self.password)
            
            # Prepare recipient list
            recipients = [to_email]
            if cc_emails:
                recipients.extend(cc_emails)
            if bcc_emails:
                recipients.extend(bcc_emails)
            
            # Send email
            text = msg.as_string()
            server.sendmail(self.sender, recipients, text)
            server.quit()
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False


    async def send_contact_form_email(
        self,
        name: str,
        email: str,
        subject: str,
        category: str,
        message: str
    ) -> bool:
        """
        Send contact form submission email
        
        Args:
            name: Sender's name
            email: Sender's email
            subject: Email subject
            category: Contact category
            message: Contact message
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Email to HelperU team
            team_subject = f"Contact Form: {subject}"
            team_body = f"""
    New contact form submission received:

    Name: {name}
    Email: {email}
    Category: {category}
    Subject: {subject}

    Message:
    {message}

    ---
    This email was sent from the HelperU contact form.
            """
            
            # Send to team
            team_success = self.send_email(
                to_email=self.sender,
                subject=team_subject,
                body=team_body.strip()
            )
            
            # Confirmation email to user
            user_subject = "Thank you for contacting HelperU"
            user_body = f"""
    Dear {name},

    Thank you for contacting HelperU! We have received your message and will get back to you within 4 hours.

    Your message details:
    - Subject: {subject}
    - Category: {category}

    We appreciate your interest in HelperU and look forward to helping you.

    Best regards,
    The HelperU Team

    ---
    This is an automated response. Please do not reply to this email.
            """
            
            # Send confirmation to user
            user_success = self.send_email(
                to_email=email,
                subject=user_subject,
                body=user_body.strip()
            )
            
            return team_success and user_success
            
        except Exception as e:
            logger.error(f"Failed to send contact form email: {e}")
            return False


    async def send_welcome_email(self, email: str, name: str, user_type: str) -> bool:
        """
        Send welcome email to new users
        
        Args:
            email: User's email
            name: User's name
            user_type: Type of user (client or helper)
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            subject = "Welcome to HelperU!"
            
            if user_type.lower() == "client":
                body = f"""
    Dear {name},

    Welcome to HelperU! We're excited to have you join our community of clients who are connecting with talented student helpers.

    Here's what you can do next:
    1. Complete your profile to get better matches
    2. Post your first task
    3. Browse available helpers in your area
    4. Use our AI assistant to optimize your posts

    Need help getting started? Check out our FAQ page or contact our support team.

    Best regards,
    The HelperU Team
                """
            else:  # helper
                body = f"""
    Dear {name},

    Welcome to HelperU! We're thrilled to have you join our community of student helpers.

    Here's what you can do next:
    1. Complete your profile with skills and availability
    2. Browse available tasks in your area
    3. Apply for tasks that match your skills
    4. Use our AI assistant to optimize your applications

    Need help getting started? Check out our FAQ page or contact our support team.

    Best regards,
    The HelperU Team
                """
            
            return self.send_email(
                to_email=email,
                subject=subject,
                body=body.strip()
            )
            
        except Exception as e:
            logger.error(f"Failed to send welcome email to {email}: {e}")
            return False


    async def send_task_notification_email(
        self,
        email: str,
        name: str,
        task_title: str,
        notification_type: str,
        additional_info: Optional[str] = None
    ) -> bool:
        """
        Send task-related notification emails
        
        Args:
            email: Recipient's email
            name: Recipient's name
            task_title: Title of the task
            notification_type: Type of notification (application, hired, completed, etc.)
            additional_info: Additional information to include
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            if notification_type == "application_received":
                subject = f"New Application for: {task_title}"
                body = f"""
    Dear {name},

You have received a new application for your task: "{task_title}"

{additional_info or "Please log in to your HelperU account to view the application details."}

Best regards,
The HelperU Team
                """
            elif notification_type == "application_accepted":
                subject = f"Application Accepted: {task_title}"
                body = f"""
    Dear {name},

Great news! Your application for "{task_title}" has been accepted.

{additional_info or "Please log in to your HelperU account to view the next steps."}

Best regards,
The HelperU Team
                """
            elif notification_type == "task_completed":
                subject = f"Task Completed: {task_title}"
                body = f"""
    Dear {name},

The task "{task_title}" has been marked as completed.

{additional_info or "Thank you for using HelperU!"}

Best regards,
The HelperU Team
                """
            elif notification_type == "task_created":
                subject = f"Task Created: {task_title}"
                body = f"""
    Dear {name},

Your task "{task_title}" has been created.

{additional_info or "Please log in to your HelperU account to view the task details."}

Best regards,
The HelperU Team"""
            else:
                subject = f"Task Update: {task_title}"
                body = f"""
Dear {name},

There's an update regarding your task: "{task_title}"

{additional_info or "Please log in to your HelperU account for more details."}

Best regards,
The HelperU Team"""
                
            
            return self.send_email(
                to_email=email,
                subject=subject,
                body=body.strip()
            )
            

        except Exception as e:
            logger.error(f"Failed to send task notification email to {email}: {e}")
            return False

        