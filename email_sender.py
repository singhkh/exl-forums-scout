#!/usr/bin/env python3
"""
Email sender module for AEM Forms Question Scraper
Sends email reports with scraped questions
"""

import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

class EmailSender:
    """Email sender class for the AEM Forms Question Scraper"""
    
    def __init__(self, smtp_server=None, smtp_port=None, sender_email=None, sender_name=None, password=None, use_ssl=False):
        """Initialize the email sender with SMTP settings."""
        self.smtp_server = smtp_server or os.environ.get("AEM_SMTP_SERVER")
        
        # Get SMTP port from args, env, or default to standard ports (465 for SSL, 587 for TLS)
        if smtp_port:
            self.smtp_port = smtp_port
        elif os.environ.get("AEM_SMTP_PORT"):
            self.smtp_port = int(os.environ.get("AEM_SMTP_PORT"))
        else:
            self.smtp_port = 465 if use_ssl else 587
            
        self.sender_email = sender_email or os.environ.get("AEM_SENDER_EMAIL")
        self.sender_name = sender_name or os.environ.get("AEM_SENDER_NAME", "AEM Forms Scraper")
        self.password = password or os.environ.get("AEM_EMAIL_PASSWORD")
        self.use_ssl = use_ssl or os.environ.get("AEM_USE_SSL", "").lower() == "true"
        
        # Get recipients (comma-separated lists in env vars)
        self._parse_recipients()
        
        # Validate required settings
        self._validate_settings()
            
    def _parse_recipients(self):
        """Parse recipients from environment variables."""
        # Default recipients
        self.default_recipients = os.environ.get("AEM_DEFAULT_RECIPIENTS", "").split(",")
        self.default_recipients = [email.strip() for email in self.default_recipients if email.strip()]
        
        # CC recipients
        self.cc_recipients = os.environ.get("AEM_CC_RECIPIENTS", "").split(",")
        self.cc_recipients = [email.strip() for email in self.cc_recipients if email.strip()]
        
        # BCC recipients
        self.bcc_recipients = os.environ.get("AEM_BCC_RECIPIENTS", "").split(",")
        self.bcc_recipients = [email.strip() for email in self.bcc_recipients if email.strip()]
        
    def _validate_settings(self):
        """Validate email settings and log warnings for missing settings."""
        missing = []
        if not self.smtp_server:
            missing.append("SMTP server")
        if not self.smtp_port:
            missing.append("SMTP port")
        if not self.sender_email:
            missing.append("Sender email")
        if not self.password:
            missing.append("Email password")
                
        if missing:
            logging.warning(f"Missing email settings: {', '.join(missing)}")
            
    def create_email_html(self, questions, start_date):
        """Create HTML email content with the list of questions."""
        # Get current date and time for the report
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Create email HTML content
        html = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
                    h1 {{ color: #1473E6; }} /* Adobe blue */
                    h2 {{ color: #505050; border-bottom: 1px solid #ddd; padding-bottom: 5px; }}
                    .question {{ margin-bottom: 20px; padding: 15px; border: 1px solid #eee; border-radius: 5px; }}
                    .question h3 {{ margin-top: 0; margin-bottom: 10px; }}
                    .question-link {{ color: #1473E6; text-decoration: none; }}
                    .question-link:hover {{ text-decoration: underline; }}
                    .meta {{ color: #777; font-size: 0.9em; margin-bottom: 10px; }}
                    .topics {{ margin-top: 10px; }}
                    .topic {{ display: inline-block; background: #F5F5F5; padding: 3px 8px; margin-right: 5px; 
                             border-radius: 3px; font-size: 0.8em; color: #555; }}
                    .stats {{ color: #777; font-size: 0.9em; margin-top: 10px; }}
                    .footer {{ margin-top: 30px; padding-top: 10px; border-top: 1px solid #ddd; font-size: 0.8em; color: #777; }}
                    .summary {{ background: #f9f9f9; padding: 10px; border-radius: 5px; margin-bottom: 20px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>AEM Forms Unanswered Questions Report</h1>
                    <p>Report generated on: {now}</p>
                    
                    <div class="summary">
                        <h2>Summary</h2>
                        <p>Found {len(questions)} unanswered questions since {start_date}</p>
                    </div>
        """
        
        if not questions:
            html += """
                    <p>No unanswered questions found in the specified time period.</p>
            """
        else:
            html += """
                    <h2>Questions</h2>
            """
            
            # Add each question to the email
            for question in questions:
                title = question.get("title", "Untitled Question")
                url = question.get("url", "#")
                author = question.get("author", "Unknown Author")
                date = question.get("date", "Unknown Date")
                content = question.get("content", "No content available")
                topics = question.get("topics", [])
                views = question.get("views", 0)
                likes = question.get("likes", 0)
                replies = question.get("replies", 0)
                
                html += f"""
                    <div class="question">
                        <h3><a class="question-link" href="{url}">{title}</a></h3>
                        <div class="meta">
                            Posted by: {author} | Date: {date}
                        </div>
                        <div>
                            {content[:300]}{'...' if len(content) > 300 else ''}
                        </div>
                """
                
                if topics:
                    html += """
                        <div class="topics">
                    """
                    for topic in topics:
                        html += f"""
                            <span class="topic">{topic}</span>
                        """
                    html += """
                        </div>
                    """
                
                html += f"""
                        <div class="stats">
                            Views: {views} | Likes: {likes} | Replies: {replies}
                        </div>
                    </div>
                """
        
        # Add footer
        html += """
                    <div class="footer">
                        <p>This is an automated report from the AEM Forms Question Scraper.</p>
                        <p>For questions or issues, please contact the administrator.</p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        return html
        
    def send_email(self, recipient_email=None, questions=None, start_date=None):
        """Send an email with the list of questions."""
        if not questions:
            logging.warning("No questions to send in the email report")
            return False
            
        if not start_date:
            start_date = "unknown date"
            
        # Determine TO recipients - use specified, fall back to default
        to_recipients = []
        if recipient_email:
            to_recipients.append(recipient_email)
        if not to_recipients and self.default_recipients:
            to_recipients.extend(self.default_recipients)
            
        if not to_recipients and not self.cc_recipients and not self.bcc_recipients:
            logging.error("No recipients specified for email report")
            return False
            
        # Validate required email settings
        if not self.smtp_server or not self.smtp_port or not self.sender_email or not self.password:
            logging.error("Missing required email settings")
            return False
            
        # Create the email
        msg = MIMEMultipart()
        msg["Subject"] = f"AEM Forms Unanswered Questions Report ({len(questions)} questions)"
        
        # Format sender with name if available
        if self.sender_name:
            msg["From"] = f"{self.sender_name} <{self.sender_email}>"
        else:
            msg["From"] = self.sender_email
        
        # Add recipients
        if to_recipients:
            msg["To"] = ", ".join(to_recipients)
        if self.cc_recipients:
            msg["Cc"] = ", ".join(self.cc_recipients)
        # Note: BCC is not added to headers but to the recipients list when sending
        
        # Create HTML email content
        html_content = self.create_email_html(questions, start_date)
        msg.attach(MIMEText(html_content, "html"))
        
        try:
            # Combine all recipients for sending
            all_recipients = to_recipients + self.cc_recipients + self.bcc_recipients
            
            # Create SMTP connection using SSL or TLS based on configuration
            if self.use_ssl:
                logging.info(f"Connecting to SMTP server {self.smtp_server}:{self.smtp_port} using SSL")
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            else:
                logging.info(f"Connecting to SMTP server {self.smtp_server}:{self.smtp_port} using TLS")
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.ehlo()
                server.starttls()
                server.ehlo()
                
            # Login and send email
            server.login(self.sender_email, self.password)
            server.send_message(msg, from_addr=self.sender_email, to_addrs=all_recipients)
            server.quit()
            
            # Log which types of recipients were used
            recipient_info = []
            if to_recipients:
                recipient_info.append(f"{len(to_recipients)} TO recipients")
            if self.cc_recipients:
                recipient_info.append(f"{len(self.cc_recipients)} CC recipients")
            if self.bcc_recipients:
                recipient_info.append(f"{len(self.bcc_recipients)} BCC recipients")
                
            logging.info(f"Email sent successfully to {', '.join(recipient_info)}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to send email: {str(e)}")
            return False 