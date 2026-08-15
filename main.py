"""
OTCR Email Bot - Interactive CLI for sending personalized emails via Gmail

Features:
  - Send single personalized emails
  - Batch send to CSV recipients
  - Select from multiple email templates
  - Support multiple recipient lists

Usage:
  python3 main.py
"""

import os
import json
import glob
from gmail_sender import GmailSender
from template_manager import TemplateManager
from recipient_manager import RecipientManager
from batch_sender import BatchEmailSender


def print_header(title: str) -> None:
    """
    Print a formatted header section.
    
    Args:
        title: Header text to display
    """
    print("\n" + "="*60)
    print(title.center(60))
    print("="*60 + "\n")


def main_menu() -> str:
    """
    Display main menu and get user choice.
    
    Returns:
        User's menu choice (1-4)
    """
    print_header("EMAIL BOT - MAIN MENU")
    
    print("What would you like to do?\n")
    print("  1. Send Single Email (personalized)")
    print("  2. Batch Send (to CSV recipients)")
    print("  3. View Recipients")
    print("  4. Exit\n")
    print("(Press Ctrl+C anytime to quit)\n")
    
    return input("Enter choice (1-4): ").strip()


def select_template_file() -> str | None:
    """
    Display available templates and let user select one.
    
    Returns:
        Selected template name without .html extension, or None if cancelled
    """
    templates_dir = 'templates'
    
    if not os.path.exists(templates_dir):
        print(f"\n❌ Templates directory not found!\n")
        return None
    
    template_files = glob.glob(os.path.join(templates_dir, "*.html"))
    
    if not template_files:
        print(f"\n❌ No HTML templates found in '{templates_dir}/' directory!\n")
        return None
    
    template_names = [os.path.basename(f).replace('.html', '') for f in template_files]
    
    print("\nAvailable Templates:\n")
    for i, name in enumerate(template_names, 1):
        print(f"  {i}. {name}")
    
    print(f"  q. Cancel\n")
    
    try:
        choice = input(f"Select template (1-{len(template_names)}, q to cancel): ").strip().lower()
        
        if choice == 'q':
            return None
        
        choice_num = int(choice)
        
        if 1 <= choice_num <= len(template_names):
            return template_names[choice_num - 1]
        
        print("\n❌ Invalid choice!\n")
        return None
    
    except ValueError:
        print("\n❌ Invalid input!\n")
        return None


def select_csv_file() -> str | None:
    """
    Display available CSV files from recipients/ folder and let user select one.
    
    Returns:
        Selected CSV filename with path, or None if cancelled
    """
    recipients_dir = 'recipients'
    csv_files = glob.glob(os.path.join(recipients_dir, "*.csv"))
    
    if not csv_files:
        print(f"\n❌ No CSV files found in '{recipients_dir}/' folder!\n")
        return None
    
    print("\nAvailable CSV files:\n")
    for i, csv_file in enumerate(csv_files, 1):
        filename = os.path.basename(csv_file)
        size = os.path.getsize(csv_file)
        print(f"  {i}. {filename} ({size} bytes)")
    
    print(f"  {len(csv_files) + 1}. Enter custom filename")
    print(f"  q. Back to Main Menu\n")
    
    try:
        choice = input(f"Select CSV file (1-{len(csv_files) + 1}, q to quit): ").strip().lower()
        
        if choice == 'q':
            return None
        
        choice_num = int(choice)
        
        if choice_num == len(csv_files) + 1:
            custom_file = input("Enter CSV filename (or 'q' to cancel): ").strip()
            if custom_file.lower() == 'q':
                return None
            custom_path = os.path.join(recipients_dir, custom_file)
            if os.path.exists(custom_path):
                return custom_path
            print(f"\n❌ File not found: {custom_path}\n")
            return None
        
        if 1 <= choice_num <= len(csv_files):
            return csv_files[choice_num - 1]
        
        print("\n❌ Invalid choice!\n")
        return None
    
    except ValueError:
        print("\n❌ Invalid input!\n")
        return None


def select_attachments() -> list:
    """
    Allow user to select files from attachments folder.
    
    Returns:
        List of file paths to attach, or empty list if none
    """
    attachments_dir = 'attachments'
    
    if not os.path.exists(attachments_dir):
        print("\n❌ Attachments folder not found!\n")
        return []
    
    # Get all files in attachments folder
    attachment_files = [f for f in os.listdir(attachments_dir) 
                       if os.path.isfile(os.path.join(attachments_dir, f)) 
                       and not f.startswith('.')]
    
    if not attachment_files:
        print("\n⚠️  No files in attachments folder\n")
        return []
    
    print("\nAvailable attachments:\n")
    for i, filename in enumerate(attachment_files, 1):
        file_path = os.path.join(attachments_dir, filename)
        file_size = os.path.getsize(file_path)
        print(f"  {i}. {filename} ({file_size:,} bytes)")
    
    print(f"  a. All files")
    print(f"  n. No attachments\n")
    
    selected = []
    
    while True:
        choice = input("Select attachments (comma-separated numbers, 'a' for all, 'n' for none): ").strip().lower()
        
        if choice == 'n':
            return []
        
        elif choice == 'a':
            return [os.path.join(attachments_dir, f) for f in attachment_files]
        
        else:
            try:
                choices = [c.strip() for c in choice.split(',')]
                selected = []
                
                for c in choices:
                    choice_num = int(c)
                    if 1 <= choice_num <= len(attachment_files):
                        file_path = os.path.join(attachments_dir, attachment_files[choice_num - 1])
                        selected.append(file_path)
                    else:
                        print(f"❌ Invalid selection: {c}")
                        selected = []
                        break
                
                if selected:
                    print(f"\n✓ Selected {len(selected)} file(s):")
                    for f in selected:
                        print(f"  - {os.path.basename(f)}")
                    return selected
                else:
                    print("❌ Invalid selection. Try again.\n")
            
            except ValueError:
                print("❌ Invalid input. Use numbers separated by commas.\n")


def send_single_email(bot: GmailSender, template_manager: TemplateManager) -> None:
    """
    Send a personalized email to a single recipient.
    
    Args:
        bot: GmailSender instance
        template_manager: TemplateManager instance
    """
    print_header("SEND SINGLE EMAIL")
    
    template_name = select_template_file()
    if not template_name:
        return
    
    print("\nEnter recipient details (or type 'q' to cancel):\n")
    
    first_name = input("First Name: ").strip()
    if first_name.lower() == 'q':
        print("\n✗ Cancelled.\n")
        return
    
    last_name = input("Last Name: ").strip()
    email = input("Email: ").strip()
    company = input("Company: ").strip()
    
    recipient = {
        'first_name': first_name,
        'last_name': last_name,
        'email': email,
        'company': company
    }
    
    try:
        # Load sender info from config
        with open('config.json', 'r') as f:
            config = json.load(f)
            sender_config = config.get('sender', {})
        
        # Transform sender config keys to template variable names
        sender_info = {
            'sender_name': sender_config.get('name', ''),
            'sender_title': sender_config.get('title', ''),
            'sender_organization': sender_config.get('organization', '')
        }
        
        # Merge recipient data with sender info for template rendering
        template_vars = {**recipient, **sender_info}
        
        html_body = template_manager.render(template_name, template_vars)
        
        # Get subject from template metadata and render it with variables
        subject_template = template_manager.get_template_subject(template_name)
        subject = subject_template
        for key, value in template_vars.items():
            subject = subject.replace(f'{{{{{key}}}}}', str(value))
        
        print(f"\nPreview:")
        print(f"  To: {recipient['email']}")
        print(f"  Subject: {subject}")
        print(f"  Template: {template_name}")
        print(f"  Company: {recipient['company']}\n")
        
        # Get attachments
        attachments = select_attachments()
        
        if input("Send this email? (y/n): ").strip().lower() == 'y':
            bot.send_email(
                recipient_email=recipient['email'],
                subject=subject,
                body=html_body,
                is_html=True,
                attachments=attachments if attachments else None
            )
            print("\n✓ Email sent successfully!")
        else:
            print("\n✗ Email cancelled.")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")


def send_batch_email(bot: GmailSender, batch_sender, template_manager: TemplateManager) -> None:
    """
    Send batch emails to multiple recipients from CSV.
    
    Args:
        bot: GmailSender instance
        batch_sender: BatchEmailSender instance
        template_manager: TemplateManager instance
    """
    print_header("BATCH SEND EMAIL")
    
    template_name = select_template_file()
    if not template_name:
        return
    
    csv_file = select_csv_file()
    if not csv_file:
        return
    
    try:
        recipient_manager = RecipientManager(csv_file)
        recipients = recipient_manager.load_recipients()
        valid_recipients, errors = recipient_manager.validate_recipients(recipients)
        
        if errors:
            print(f"⚠️  {len(errors)} validation error(s):")
            for error in errors:
                print(f"   - {error}\n")
        
        if not valid_recipients:
            print("❌ No valid recipients found!\n")
            return
        
        print(f"Found {len(valid_recipients)} valid recipients:")
        for i, r in enumerate(valid_recipients, 1):
            print(f"  {i}. {r['first_name']} ({r['company']}) - {r['email']}")
        
        delay = input("\nDelay between emails in seconds (default 1): ").strip()
        delay_between = int(delay) if delay else 1
        
        print(f"\nTemplate: {template_name}")
        print(f"CSV File: {csv_file}")
        
        # Get subject from template metadata
        subject_template = template_manager.get_template_subject(template_name)
        print(f"Subject: {subject_template}")
        print(f"Delay: {delay_between} second(s)")
        
        # Get attachments
        attachments = select_attachments()
        
        if input("\nSend to all recipients? (y/n): ").strip().lower() == 'y':
            batch_sender.send_batch(
                recipients=valid_recipients,
                template_name=template_name,
                subject=subject_template,
                delay_between=delay_between,
                attachments=attachments if attachments else None
            )
        else:
            print("\n✗ Batch send cancelled.")
    
    except FileNotFoundError:
        print("❌ CSV file not found!\n")
    except ValueError:
        print("❌ Invalid delay value!\n")
    except Exception as e:
        print(f"\n❌ Error: {e}")


def view_recipients(recipient_manager: RecipientManager) -> None:
    """
    View and validate recipients from CSV file.
    
    Args:
        recipient_manager: RecipientManager instance
    """
    print_header("VIEW RECIPIENTS")
    
    try:
        recipients = recipient_manager.load_recipients()
        valid_recipients, errors = recipient_manager.validate_recipients(recipients)
        
        print(f"Total records: {len(recipients)}")
        print(f"Valid: {len(valid_recipients)}")
        print(f"Invalid: {len(errors)}\n")
        
        if valid_recipients:
            print("Valid Recipients:")
            for i, r in enumerate(valid_recipients, 1):
                print(f"\n  {i}. {r['first_name']} {r['last_name']}")
                print(f"     Email: {r['email']}")
                print(f"     Company: {r['company']}")
        
        if errors:
            print("\n⚠️  Errors:")
            for error in errors:
                print(f"   - {error}")
        
        print()
    
    except FileNotFoundError:
        print("❌ recipients.csv not found!\n")


def main() -> None:
    """Main application loop."""
    bot = GmailSender('credentials.json')
    template_manager = TemplateManager('templates')
    batch_sender = BatchEmailSender(bot)
    
    print("\n" + "="*60)
    print("WELCOME TO EMAIL BOT".center(60))
    print("="*60)
    
    while True:
        choice = main_menu()
        
        if choice == '1':
            send_single_email(bot, template_manager)
        elif choice == '2':
            send_batch_email(bot, batch_sender, template_manager)
        elif choice == '3':
            recipient_manager = RecipientManager('recipients/recipients.csv')
            view_recipients(recipient_manager)
        elif choice == '4':
            print("\nGoodbye! ✓\n")
            break
        else:
            print("\n❌ Invalid choice. Please try again.\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting... ✓\n")
