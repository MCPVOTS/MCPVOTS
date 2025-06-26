#!/usr/bin/env python3
"""
Unicode Logging Fix for Windows
Fixes the Unicode encoding issues in console output
"""

import os
import sys
import logging
from io import StringIO

def fix_unicode_logging():
    """Fix Unicode logging issues on Windows"""
    
    # Set environment variables for UTF-8 encoding
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONUTF8'] = '1'
    
    # Reconfigure stdout and stderr to use UTF-8
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    if sys.stderr.encoding != 'utf-8':
        sys.stderr.reconfigure(encoding='utf-8')
    
    # Create custom logging handler that removes Unicode characters
    class UnicodeCleanHandler(logging.StreamHandler):
        def emit(self, record):
            try:
                msg = self.format(record)
                # Remove or replace Unicode characters that cause issues
                msg = msg.encode('ascii', 'replace').decode('ascii')
                stream = self.stream
                stream.write(msg + self.terminator)
                self.flush()
            except (KeyboardInterrupt, SystemExit):
                raise
            except:
                self.handleError(record)
    
    # Configure logging with Unicode-clean handler
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('unicode_clean.log', encoding='utf-8'),
            UnicodeCleanHandler()
        ],
        force=True
    )
    
    print("Unicode logging fix applied successfully")

if __name__ == "__main__":
    fix_unicode_logging()
    
    # Test with some Unicode characters
    logger = logging.getLogger(__name__)
    logger.info("Testing Unicode fix - Robot: 🤖, Rocket: 🚀, Check: ✅")
    logger.info("Unicode characters should be replaced with ASCII equivalents")
