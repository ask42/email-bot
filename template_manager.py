"""
Template manager for loading and rendering HTML email templates.

Features:
  - Load individual templates
  - Render with variable substitution ({{variable}})
  - List available templates
  - Extract variables from templates
  - Save new templates
"""

import os
import re


class TemplateManager:
    """HTML email template manager with variable substitution."""
    
    def __init__(self, templates_dir: str = 'templates') -> None:
        """Initialize template manager with templates directory."""
        self.templates_dir = templates_dir
        if not os.path.exists(templates_dir):
            os.makedirs(templates_dir)
    
    def load_template(self, template_name: str) -> str:
        """Load a template from the templates directory."""
        if not template_name.endswith('.html'):
            template_name += '.html'
        
        template_path = os.path.join(self.templates_dir, template_name)
        
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template not found: {template_path}")
        
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def render(self, template_name, variables):
        """
        Render a template with provided variables
        
        Args:
            template_name (str): Name of the template file
            variables (dict): Dictionary of variables to substitute
                Example: {'first_name': 'John', 'company': 'Acme Corp'}
        
        Returns:
            str: Rendered HTML content
        """
        template = self.load_template(template_name)
        
        # Replace {{variable}} with values from dictionary
        rendered = template
        for key, value in variables.items():
            placeholder = '{{' + key + '}}'
            rendered = rendered.replace(placeholder, str(value))
        
        return rendered
    
    def save_template(self, template_name, content):
        """
        Save a template to the templates directory
        
        Args:
            template_name (str): Name of the template file
            content (str): HTML content to save
        """
        if not template_name.endswith('.html'):
            template_name += '.html'
        
        template_path = os.path.join(self.templates_dir, template_name)
        
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✓ Template saved: {template_path}")
    
    def list_templates(self):
        """
        List all available templates
        
        Returns:
            list: List of template names
        """
        if not os.path.exists(self.templates_dir):
            return []
        
        templates = [f for f in os.listdir(self.templates_dir) if f.endswith('.html')]
        return templates
    
    def get_template_variables(self, template_name):
        """
        Extract placeholder variables from a template
        
        Args:
            template_name (str): Name of the template file
        
        Returns:
            list: List of variable names (e.g., ['first_name', 'company'])
        """
        template = self.load_template(template_name)
        
        # Find all {{variable}} patterns
        pattern = r'\{\{(\w+)\}\}'
        variables = re.findall(pattern, template)
        
        return list(set(variables))  # Return unique variables
    
    def get_template_subject(self, template_name: str) -> str:
        """
        Get the email subject line from template metadata comments.
        Expected format at top of HTML file:
        <!--
        subject: Email subject here
        description: Optional description
        -->
        
        Args:
            template_name (str): Name of the template (without .html)
        
        Returns:
            str: Subject line template with {{variables}}, or empty string if not found
        """
        try:
            template_content = self.load_template(template_name)
            
            # Look for metadata in HTML comments at the top
            import re
            match = re.search(r'<!--\s*([\s\S]*?)\s*-->', template_content)
            if match:
                metadata_block = match.group(1)
                # Extract subject line
                subject_match = re.search(r'subject:\s*(.+)', metadata_block)
                if subject_match:
                    return subject_match.group(1).strip()
        except:
            pass
        
        return ''
    
    def get_template_description(self, template_name: str) -> str:
        """
        Get the template description from metadata comments.
        
        Args:
            template_name (str): Name of the template (without .html)
        
        Returns:
            str: Description, or empty string if not found
        """
        try:
            template_content = self.load_template(template_name)
            
            import re
            match = re.search(r'<!--\s*([\s\S]*?)\s*-->', template_content)
            if match:
                metadata_block = match.group(1)
                # Extract description
                desc_match = re.search(r'description:\s*(.+)', metadata_block)
                if desc_match:
                    return desc_match.group(1).strip()
        except:
            pass
        
        return ''
