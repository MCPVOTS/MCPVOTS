#!/usr/bin/env python3
"""
Quick script to fix Unicode logging issues in comprehensive_ecosystem_orchestrator.py
"""
import re

def fix_unicode_logging(file_path):
    """Fix Unicode logging calls in the given file"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to match logger calls with Unicode characters
    pattern = r'(logger\.(info|warning|error|debug)\()"([^"]*[^\x00-\x7F][^"]*)"(\))'
    
    def replace_func(match):
        prefix = match.group(1)  # logger.info(
        log_level = match.group(2)  # info, warning, etc.
        message = match.group(3)   # the message content
        suffix = match.group(4)    # )
        
        return f'{prefix}safe_log("{message}"){suffix}'
    
    # Apply the replacement
    fixed_content = re.sub(pattern, replace_func, content)
    
    # Also fix f-string logging calls
    f_pattern = r'(logger\.(info|warning|error|debug)\()f"([^"]*[^\x00-\x7F][^"]*)"(\))'
    
    def replace_f_func(match):
        prefix = match.group(1)  # logger.info(
        log_level = match.group(2)  # info, warning, etc.
        message = match.group(3)   # the f-string content
        suffix = match.group(4)    # )
        
        return f'{prefix}safe_log(f"{message}"){suffix}'
    
    fixed_content = re.sub(f_pattern, replace_f_func, fixed_content)
    
    # Write back the fixed content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print(f"Fixed Unicode logging calls in {file_path}")

if __name__ == "__main__":
    fix_unicode_logging("C:\\Workspace\\MCPVots\\comprehensive_ecosystem_orchestrator.py")
