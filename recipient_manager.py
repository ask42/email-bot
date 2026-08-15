"""
CSV recipient manager for loading and validating email recipient lists.

Features:
  - Load recipients from CSV
  - Validate recipient data
  - Create sample CSV files
  - Get recipient count
"""

import csv
import os


class RecipientManager:
    """Manages CSV recipient lists."""
    
    def __init__(self, csv_file: str = 'recipients/recipients.csv') -> None:
        """Initialize recipient manager."""
        self.csv_file = csv_file
    
    def load_recipients(self):
        """
        Load recipients from CSV file
        
        CSV format:
        first_name,last_name,email,company
        John,Doe,john@example.com,Acme Corp
        Jane,Smith,jane@example.com,Tech Inc
        
        Returns:
            list: List of dictionaries with recipient data
        """
        if not os.path.exists(self.csv_file):
            raise FileNotFoundError(f"CSV file not found: {self.csv_file}")
        
        recipients = []
        with open(self.csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Strip whitespace from all values
                row = {k: v.strip() for k, v in row.items()}
                recipients.append(row)
        
        return recipients
    
    def validate_recipients(self, recipients=None):
        """
        Validate recipient data
        
        Args:
            recipients (list): List of recipient dicts. If None, loads from CSV.
        
        Returns:
            tuple: (valid_recipients, errors)
        """
        if recipients is None:
            recipients = self.load_recipients()
        
        valid_recipients = []
        errors = []
        
        required_fields = {'first_name', 'last_name', 'email', 'company'}
        
        for idx, recipient in enumerate(recipients, 1):
            missing_fields = required_fields - set(recipient.keys())
            
            if missing_fields:
                errors.append(f"Row {idx}: Missing fields {missing_fields}")
                continue
            
            # Validate email format
            if '@' not in recipient['email']:
                errors.append(f"Row {idx}: Invalid email '{recipient['email']}'")
                continue
            
            valid_recipients.append(recipient)
        
        return valid_recipients, errors
    
    def create_sample_csv(self):
        """
        Create a sample CSV file for reference
        """
        sample_data = [
            ['first_name', 'last_name', 'email', 'company'],
            ['John', 'Doe', 'john@example.com', 'Acme Corp'],
            ['Jane', 'Smith', 'jane@example.com', 'Tech Inc'],
            ['Bob', 'Johnson', 'bob@example.com', 'Global Solutions'],
        ]
        
        sample_file = 'recipients_sample.csv'
        with open(sample_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(sample_data)
        
        print(f"✓ Sample CSV created: {sample_file}")
    
    def get_recipient_count(self):
        """Get number of recipients in CSV"""
        recipients = self.load_recipients()
        return len(recipients)
