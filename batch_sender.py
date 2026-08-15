"""
Batch email sender for sending emails to multiple recipients.

Features:
  - Send emails to multiple recipients
  - Personalize each email with recipient data
  - Automatic delays to avoid rate limiting
  - Detailed logging of send results
"""

import time
import logging
import json
from gmail_sender import GmailSender
from template_manager import TemplateManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BatchEmailSender:
    """Sends batch emails to multiple recipients."""
    
    def __init__(self, bot: GmailSender) -> None:
        """Initialize batch email sender."""
        self.bot = bot
        self.template_manager = TemplateManager()
        self.sender_info = self._load_sender_info()
    
    def _load_sender_info(self) -> dict:
        """Load sender information from config.json."""
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
                sender_config = config.get('sender', {})
                # Transform config keys to template variable names
                return {
                    'sender_name': sender_config.get('name', ''),
                    'sender_title': sender_config.get('title', ''),
                    'sender_organization': sender_config.get('organization', '')
                }
        except FileNotFoundError:
            logger.warning("config.json not found, using empty sender info")
            return {}
    
    def send_batch(self, recipients, template_name, subject, delay_between=0, attachments=None):
        """
        Send batch emails to multiple recipients
        
        Args:
            recipients (list): List of recipient dictionaries
            template_name (str): Name of template to use
            subject (str): Email subject line (can use {{variables}})
            delay_between (int): Delay in seconds between each email (default: 0)
            attachments (list): List of file paths to attach to all emails (default: None)
        
        Returns:
            dict: Send results with counts
        """
        sent_count = 0
        failed_count = 0
        
        logger.info(f"Starting batch send: {len(recipients)} recipients")
        logger.info(f"Template: {template_name}")
        logger.info(f"Delay between emails: {delay_between}s\n")
        
        for idx, recipient in enumerate(recipients, 1):
            try:
                # Merge recipient data with sender info for template rendering
                template_vars = {**recipient, **self.sender_info}
                
                # Render subject with variables
                rendered_subject = subject
                for key, value in template_vars.items():
                    placeholder = '{{' + key + '}}'
                    rendered_subject = rendered_subject.replace(placeholder, str(value))
                
                # Render email body from template
                rendered_body = self.template_manager.render(template_name, template_vars)
                
                # Send email with attachments (same for all recipients)
                self.bot.send_email(
                    recipient_email=recipient['email'],
                    subject=rendered_subject,
                    body=rendered_body,
                    is_html=True,
                    attachments=attachments
                )
                
                sent_count += 1
                logger.info(f"[{idx}/{len(recipients)}] ✓ Sent to {recipient['email']}")
                
                # Delay between sends to avoid rate limiting
                if delay_between > 0 and idx < len(recipients):
                    time.sleep(delay_between)
            
            except Exception as e:
                failed_count += 1
                logger.error(f"[{idx}/{len(recipients)}] ✗ Failed to send to {recipient['email']}: {str(e)}")
        
        results = {
            'total': len(recipients),
            'sent': sent_count,
            'failed': failed_count,
            'template': template_name
        }
        
        logger.info(f"{'='*50}")
        logger.info(f"Batch Complete - Sent: {sent_count}, Failed: {failed_count}")
        logger.info(f"{'='*50}\n")
        
        return results
