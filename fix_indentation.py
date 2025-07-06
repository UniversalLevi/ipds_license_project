#!/usr/bin/env python3
"""
Fix indentation issues in all Python files
"""

import os
import re

def fix_file_indentation(filepath):
    """Fix indentation in a single file"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Replace tabs with 4 spaces
        content = re.sub(r'\t', '    ', content)
        
        # Fix specific indentation issues
        lines = content.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            # Fix specific problematic lines
            if 'hw_fingerprint = self.hardware_fingerprint.generate_fingerprint()' in line:
                # This line should be indented properly
                line = '                ' + line.strip()
            elif 'print(f"{Fore.GREEN}✅ Hardware fingerprint generated{Style.RESET_ALL}")' in line:
                # This line should be indented properly
                line = '                ' + line.strip()
            elif 'print(f"{Fore.CYAN}🔗 API CONNECTION TEST{Style.RESET_ALL}")' in line:
                # This line should be indented properly
                line = '            ' + line.strip()
            elif 'print(f"{Fore.YELLOW}🔄 Testing connection to: {self.api_url}{Style.RESET_ALL}")' in line:
                # This line should be indented properly
                line = '            ' + line.strip()
            elif 'print(f"{Fore.GREEN}✅ API connection successful!{Style.RESET_ALL}")' in line:
                # This line should be indented properly
                line = '                ' + line.strip()
            elif 'print(f"{Fore.RED}❌ API connection failed{Style.RESET_ALL}")' in line:
                # This line should be indented properly
                line = '                ' + line.strip()
            elif 'print(f"{Fore.RED}❌ API connection test failed: {e}{Style.RESET_ALL}")' in line:
                # This line should be indented properly
                line = '            ' + line.strip()
            elif 'fingerprint = self.hardware_fingerprint.generate_fingerprint()' in line:
                # This line should be indented properly
                line = '                ' + line.strip()
            elif 'print(f"{Fore.GREEN}✅ Hardware fingerprint generated{Style.RESET_ALL}")' in line and 'fingerprint' in lines[i-1]:
                # This line should be indented properly
                line = '                ' + line.strip()
            elif 'print(f"{Fore.WHITE}Fingerprint: {Fore.CYAN}{fingerprint}{Style.RESET_ALL}")' in line:
                # This line should be indented properly
                line = '                ' + line.strip()
            
            fixed_lines.append(line)
        
        # Write back the fixed content
        with open(filepath, 'w') as f:
            f.write('\n'.join(fixed_lines))
        
        print(f"✅ Fixed indentation in: {filepath}")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing {filepath}: {e}")
        return False

def fix_all_python_files():
    """Fix indentation in all Python files"""
    python_files = []
    
    # Find all Python files
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    print(f"🔍 Found {len(python_files)} Python files to check...")
    
    fixed_count = 0
    for filepath in python_files:
        if fix_file_indentation(filepath):
            fixed_count += 1
    
    print(f"✅ Fixed indentation in {fixed_count} files")

if __name__ == "__main__":
    fix_all_python_files() 