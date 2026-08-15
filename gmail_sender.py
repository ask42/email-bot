import base64
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import pickle

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

class GmailSender:
    def __init__(self, credentials_file='credentials.json'):
        """Initialize Gmail Sender with credentials"""
        self.credentials_file = credentials_file
        self.service = None
        self.authenticate()
    
    def authenticate(self):
        """Authenticate with Gmail API using OAuth 2.0"""
        creds = None
        
        # Check if token.pickle exists (cached credentials)
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        
        # If no valid credentials, request authorization
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('gmail', 'v1', credentials=creds)
        print("✓ Successfully authenticated with Gmail API")
    
    def send_email(self, recipient_email, subject, body, is_html=False, attachments=None):
        """
        Send an email via Gmail with optional attachments
        
        Args:
            recipient_email (str): Email address of recipient
            subject (str): Email subject
            body (str): Email body content
            is_html (bool): Whether body is HTML content
            attachments (list): List of file paths to attach
                Example: ['/path/to/file.pdf', 'documents/brochure.pdf']
        
        Returns:
            dict: Message send response
        """
        try:
            message = MIMEMultipart()
            message['to'] = recipient_email
            message['subject'] = subject
            
            msg_type = 'html' if is_html else 'plain'
            message.attach(MIMEText(body, msg_type))
            
            # Add attachments
            if attachments:
                for file_path in attachments:
                    if not self._attach_file(message, file_path):
                        print(f"⚠️  Skipping attachment: {file_path}")
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            # Send message
            send_message = {'raw': raw_message}
            result = self.service.users().messages().send(
                userId='me',
                body=send_message
            ).execute()
            
            attachment_count = len(attachments) if attachments else 0
            if attachment_count > 0:
                print(f"✓ Email sent with {attachment_count} attachment(s)! Message ID: {result['id']}")
            else:
                print(f"✓ Email sent successfully! Message ID: {result['id']}")
            return result
        
        except Exception as e:
            print(f"✗ Failed to send email: {str(e)}")
            raise
    
    def _attach_file(self, message, file_path):
        """
        Attach a file to an email message
        
        Args:
            message: MIMEMultipart message object
            file_path (str): Path to file to attach
        
        Returns:
            bool: True if attachment successful, False otherwise
        """
        try:
            # Handle both absolute and relative paths
            if not os.path.isabs(file_path):
                file_path = os.path.abspath(file_path)
            
            if not os.path.exists(file_path):
                print(f"❌ Attachment not found: {file_path}")
                return False
            
            if not os.path.isfile(file_path):
                print(f"❌ Not a file: {file_path}")
                return False
            
            # Read and attach file
            with open(file_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                
                filename = os.path.basename(file_path)
                part.add_header('Content-Disposition', 'attachment', filename=filename)
                message.attach(part)
            
            print(f"  ✓ Attached: {os.path.basename(file_path)}")
            return True
        
        except Exception as e:
            print(f"❌ Error attaching {file_path}: {str(e)}")
            return False

def main():
    """Test the email sender functionality"""
    
    # Initialize sender
    sender = GmailSender('credentials.json')
    
    # Test email
    recipient = "johndoe@gmail.com"  # Change to your test email
    subject = "Test Email from Email Bot"
    body = """
    Hello,
    
    This is a test email from the Email Bot automation system.
    
    Best regards,
    Email Bot
    """
    
    # Send email
    sender.send_email(recipient, subject, body)

if __name__ == '__main__':
    main()
