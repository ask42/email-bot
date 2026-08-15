# Email Bot

A simple yet useful Python email bot. Automates personalized email outreach through Gmail API with HTML templates, CSV recipient management, and batch sending. 

NOTE: Several features present in the private version (lead web scraping, email analytics) have been removed in this version.

## Features

**OAuth 2.0 Gmail** - Secure authentication with token caching  
**HTML Templates** - Personalize emails with `{{first_name}}`, `{{company}}`, etc.  
**CSV Recipients** - Load from simple CSV files with validation  
**Batch Sending** - Send to multiple recipients with automatic delays  
**Interactive CLI** - User-friendly menu for sending emails  
**Modular Design** - Easy to extend and use 

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Gmail API Credentials

#### Step 1: Create a Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (name it something like "Gmail Bot")
3. Enable the **Gmail API**:
   - Click "Enable APIs and Services"
   - Search for "Gmail API"
   - Click "Enable"

#### Step 2: Create OAuth 2.0 Credentials
1. Go to **Credentials** in the left sidebar
2. Click **Create Credentials** -> **OAuth 2.0 Client ID**
3. If prompted, configure OAuth consent screen first:
   - Choose **External** as the user type
   - Fill in app name, user support email, and developer contact
   - Add scope: `https://www.googleapis.com/auth/gmail.send`
   - Save and continue
   - **Important:** Go to **Test users** section and click **Add Users**
   - Add your Gmail address (the one you'll send emails from) as a test user
   - Save and continue
4. Back to credentials creation:
   - Select **Desktop application** as application type
   - Click **Create**
5. Download the JSON file and save it as `credentials.json` in this directory

### 3. Run the Bot

```bash
python3 main.py
```

**First run:**
- Opens browser for Gmail authorization
- Asks you to log in with your Google account
- Requests permission to send emails
- Saves credentials locally in `token.pickle`

**All subsequent runs:**
- Uses cached credentials automatically
- No browser prompt needed

## Configuration

### Sender Email Address

The **sender email address** is automatically set to the Gmail account you authenticated with. You don't need to configure it manually:

**How it works:**
1. On the first run, you'll be directed to log in with your Gmail account
2. That account becomes your sender email for all emails
3. Emails are sent from that Gmail address automatically

**To use a different sender email:**
1. Delete `token.pickle` from the project folder
2. Run `python3 main.py` again
3. Log in with a different Gmail account when prompted

### Sender Information

Edit `config.json` to customize sender details that appear in email signatures:

```json
{
  "sender": {
    "name": "Your Name",
    "title": "Your Title",
    "organization": "Your Organization"
  }
}
```

These variables are automatically inserted into email templates:
- `{{sender_name}}`
- `{{sender_title}}`
- `{{sender_organization}}`

### Email Templates

Email templates are HTML files stored in the `templates/` directory with metadata embedded at the top:

```html
<!--
subject: [MockCompany] Exploring a {{company}} x MockCompany Event This Semester
description: MockCompany partnership outreach email
-->
<html>
  <body>
    <p>Hi {{first_name}},</p>
    <!-- Email content with {{variables}} -->
  </body>
</html>
```

**Adding a new template:**
1. Create a new `.html` file in the `templates/` folder
2. Add metadata comments at the very top with `subject:` and `description:`
3. Include your email content with `{{variable}}` placeholders
4. The template will automatically appear in the template selection menu

**Available variables in templates:**
- Recipient data: `{{first_name}}`, `{{last_name}}`, `{{email}}`, `{{company}}`
- Sender info: `{{sender_name}}`, `{{sender_title}}`, `{{sender_organization}}`

### Recipient Lists

Recipient lists are CSV files stored in the `recipients/` folder with the following columns:

```csv
first_name,last_name,email,company
John,Doe,john@example.com,Acme Corp
Jane,Smith,jane@example.com,Tech Inc
```

**Adding a new recipient list:**
1. Create a new `.csv` file in the `recipients/` folder
2. Include columns: `first_name`, `last_name`, `email`, `company`
3. File will automatically appear in the recipient selection menu

**CSV Format:**
- **Required columns:** first_name, last_name, email, company
- Emails with invalid format or missing required fields will be skipped with warnings
- Whitespace is automatically trimmed from values

### Attachments

Add files to the `attachments/` folder to send them with emails. Files can be any type: PDFs, documents, images, etc.

**For Single and Batch Emails:**
1. When prompted "Select attachments:", choose from available files
2. Type numbers separated by commas (e.g., `1,3,5`)
3. Type `a` to attach all files
4. Type `n` to skip attachments

**Same attachments are sent to all recipients in batch mode** - select once and all emails will include them.

## Tips

- **Test first** - Send a test email to yourself before doing batch sends
- **Add delay** - Use `delay_between=2` or more to avoid Gmail rate limits
- **Validate CSV** - Use "View Recipients" menu option to check for errors before sending
- **Custom variables** - Add any custom columns to your CSV and use them as `{{column_name}}` in templates
- **Multiple lists** - Keep separate CSV files for different campaigns or audience segments
- **Version control** - Add `credentials.json` and `token.pickle` to `.gitignore`

## File Structure

```
email-bot/
├── main.py                 # Interactive CLI menu
├── gmail_sender.py         # Gmail API client
├── template_manager.py     # Template management & rendering
├── recipient_manager.py    # CSV loading & validation
├── batch_sender.py         # Batch email sending
├── config.json             # Sender configuration (name, title, org)
├── credentials.json        # Gmail API credentials (download from Google Cloud)
├── token.pickle            # Cached authentication token (auto-generated)
├── requirements.txt        # Python dependencies
├── templates/              # Email templates directory
│   └── professional_event_invitation.html  # Sample template
├── recipients/             # CSV recipient lists directory
│   └── recipients.csv      # Sample recipient list
├── attachments/            # Email attachments directory
│   └── (add PDFs, documents here for mass outreach)
└── README.md
```

## Usage

### Interactive CLI

The easiest way to use the bot is through the interactive menu:

```bash
python3 main.py
```

**Main Menu Options:**
1. **Send Single Email** - Send a personalized email to one recipient
2. **Batch Send** - Send to multiple recipients from a CSV file
3. **View Recipients** - View and validate your recipient list
4. **Exit** - Close the application

### Working with Multiple Recipient Lists

Store different recipient lists in the `recipients/` folder:

```
recipients/
├── recipients.csv           # Main list
├── spring_outreach.csv      # Spring event outreach
├── partners.csv             # Active partners
└── follow_up.csv            # Follow-up contacts
```

When you run batch send, you'll be prompted to choose which CSV file to use.

### Programmatic Usage

You can also use the bot as a library in your own Python scripts:

#### Send Single Personalized Email

```python
from gmail_sender import GmailSender
from template_manager import TemplateManager
import json

# Initialize
bot = GmailSender('credentials.json')
manager = TemplateManager('templates')

# Load sender info
with open('config.json', 'r') as f:
    config = json.load(f)
    sender_info = config.get('sender', {})

# Prepare recipient data
recipient = {
    'first_name': 'John',
    'last_name': 'Doe',
    'company': 'Acme Corp',
    'email': 'john@example.com'
}

# Merge recipient and sender data
template_vars = {**recipient, **sender_info}

# Render template
html_body = manager.render('professional_event_invitation', template_vars)

# Get and render subject
subject_template = manager.get_template_subject('professional_event_invitation')
subject = subject_template
for key, value in template_vars.items():
    subject = subject.replace(f'{{{{{key}}}}}', str(value))

# Send email
bot.send_email(
    recipient_email=recipient['email'],
    subject=subject,
    body=html_body,
    is_html=True
)
```

#### Batch Send to CSV Recipients

```python
from gmail_sender import GmailSender
from recipient_manager import RecipientManager
from batch_sender import BatchEmailSender

# Initialize
bot = GmailSender('credentials.json')
recipients_mgr = RecipientManager('recipients/recipients.csv')
batch = BatchEmailSender(bot)

# Load & validate
recipients = recipients_mgr.load_recipients()
valid, errors = recipients_mgr.validate_recipients(recipients)

if errors:
    print(f"Found {len(errors)} validation errors")
    for error in errors:
        print(error)

# Send to all valid recipients
results = batch.send_batch(
    recipients=valid,
    template_name='professional_event_invitation',
    subject='[MockCompany] Exploring a {{company}} x MockCompany Event This Semester',
    delay_between=1  # 1 second between emails
)

print(f"Sent: {results['sent']}, Failed: {results['failed']}")
```

## API Reference

### GmailSender

```python
from gmail_sender import GmailSender

bot = GmailSender('credentials.json')

# Send email (plain text or HTML)
bot.send_email(
    recipient_email='jane@example.com',
    subject='Hello!',
    body='<html><body><h1>Welcome!</h1></body></html>',
    is_html=True
)
```

### TemplateManager

```python
from template_manager import TemplateManager

manager = TemplateManager('templates')

# Get variables used in a template
vars = manager.get_template_variables('professional_event_invitation')
# Returns: ['first_name', 'company', 'sender_name', ...]

# Render template with data
html = manager.render('professional_event_invitation', {
    'first_name': 'Jane',
    'company': 'ACME',
    'sender_name': 'John',
    'sender_title': 'MockPosition',
    'sender_organization': 'MockCompany'
})

# Get template subject line (from metadata)
subject = manager.get_template_subject('professional_event_invitation')
# Returns: "[MockCompany] Exploring a {{company}} x MockCompany Event This Semester"

# Save new template
manager.save_template('custom_template', '<html>...</html>')

# List all templates
templates = manager.list_templates()
```

### RecipientManager

```python
from recipient_manager import RecipientManager

rm = RecipientManager('recipients/recipients.csv')

# Load recipients from CSV
recipients = rm.load_recipients()
# Returns: [{'first_name': 'John', 'last_name': 'Doe', 'email': '...', 'company': '...'}, ...]

# Validate recipients (returns valid list + error list)
valid, errors = rm.validate_recipients(recipients)

# Check validation errors
if errors:
    print(f"Found {len(errors)} invalid records")
    for error in errors:
        print(error)

# Get recipient count
count = rm.get_recipient_count()
```

### BatchEmailSender

```python
from batch_sender import BatchEmailSender

bot = GmailSender('credentials.json')
sender = BatchEmailSender(bot)

# Send batch emails
results = sender.send_batch(
    recipients=valid_recipients,
    template_name='professional_event_invitation',
    subject='[MockCompany] Exploring a {{company}} x MockCompany Event This Semester',
    delay_between=1  # seconds between each email
)

# Results dictionary:
# {'total': 5, 'sent': 5, 'failed': 0, 'template': 'professional_event_invitation'}
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "credentials.json not found" | Download OAuth credentials from Google Cloud Console and save as `credentials.json` |
| "Access blocked" or "App not verified" | Add your Gmail address as a test user in OAuth consent screen (Google Cloud Console) |
| "Template not found" | Ensure template file exists in `templates/` folder with `.html` extension |
| "CSV file not found" | Check file exists in `recipients/` folder and filename is correct |
| "No CSV files found" | Create at least one `.csv` file in the `recipients/` folder |
| `{{variable}}` not replaced | Ensure variable name matches CSV column name exactly and uses `{{}}` syntax |
| "Invalid email error" | Ensure CSV email field contains `@` symbol |
| OAuth/Authentication error | Delete `token.pickle` and re-run to re-authenticate with Gmail |
| "Permission denied" | Ensure Gmail API is enabled in Google Cloud Console |
| Rate limit errors | Increase `delay_between` parameter to 2-3 seconds |
| "Invalid credentials" | Verify `credentials.json` is in the correct project directory |

## Security & Best Practices

- **Never commit** `credentials.json` or `token.pickle` to version control
- **Rate Limits**: Gmail API has limits (quotas vary by account type)
- **Sender Email**: Emails are sent from the Gmail account you authenticate with (OAuth login)
- **Sender Info**: `config.json` controls name/title/organization in signatures, NOT the email address
- **Token Refresh**: The bot automatically refreshes expired credentials

## Next Steps

- Implement email scheduling