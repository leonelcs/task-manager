#!/usr/bin/env python3
"""
Test script for alpha whitelist functionality.
"""
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.utils.whitelist import is_email_whitelisted, get_whitelist_emails, get_whitelist_error_message
from app.config.settings import settings

def test_whitelist():
    """Test the whitelist functionality."""
    print("🧪 Testing Alpha Whitelist Functionality")
    print("=" * 50)
    
    # Display current configuration
    print(f"📋 Whitelist Enabled: {settings.ALPHA_WHITELIST_ENABLED}")
    print(f"📋 Configured Emails: {settings.ALPHA_WHITELIST_EMAILS}")
    print()
    
    # Get whitelist emails
    whitelist_emails = get_whitelist_emails()
    print(f"📧 Processed Whitelist Emails ({len(whitelist_emails)}):")
    for email in whitelist_emails:
        print(f"  - {email}")
    print()
    
    # Test cases
    test_cases = [
        "leonelcs@gmail.com",
        "beafurlan52@gmail.com", 
        "LEONELCS@GMAIL.COM",  # Test case sensitivity
        "BeAFurlan52@Gmail.com",  # Test case sensitivity
        "random@gmail.com",  # Should fail
        "test@example.com",  # Should fail
        "",  # Edge case
        "invalid-email"  # Invalid format
    ]
    
    print("🧪 Testing Email Validation:")
    print("-" * 30)
    
    for email in test_cases:
        result = is_email_whitelisted(email)
        status = "✅ ALLOWED" if result else "❌ BLOCKED"
        print(f"{status}: '{email}'")
    
    print()
    print("💬 Error Message Preview:")
    print(f"   {get_whitelist_error_message()}")
    print()
    print("✅ Whitelist test completed!")

if __name__ == "__main__":
    test_whitelist()
