"""
Alpha release whitelist utilities for ADHD Task Manager.
"""
from typing import List
import logging
from app.config.settings import settings

logger = logging.getLogger(__name__)

def get_whitelist_emails() -> List[str]:
    """
    Get the list of whitelisted emails for alpha release.
    
    Returns:
        List[str]: List of whitelisted email addresses
    """
    if not settings.ALPHA_WHITELIST_EMAILS:
        return []
    
    emails = [email.strip().lower() for email in settings.ALPHA_WHITELIST_EMAILS.split(',')]
    return [email for email in emails if email]  # Filter out empty strings

def is_email_whitelisted(email: str) -> bool:
    """
    Check if an email address is whitelisted for alpha release.
    
    Args:
        email (str): Email address to check
        
    Returns:
        bool: True if email is whitelisted or whitelist is disabled, False otherwise
    """
    if not settings.ALPHA_WHITELIST_ENABLED:
        logger.info("🔓 Alpha whitelist is disabled - allowing all emails")
        return True
    
    email_lower = email.strip().lower()
    whitelist_emails = get_whitelist_emails()
    
    if not whitelist_emails:
        logger.warning("⚠️ Alpha whitelist is enabled but no emails configured - denying access")
        return False
    
    is_whitelisted = email_lower in whitelist_emails
    
    if is_whitelisted:
        logger.info(f"✅ Email {email} is whitelisted for alpha release")
    else:
        logger.warning(f"❌ Email {email} is NOT whitelisted for alpha release")
        logger.info(f"📝 Whitelisted emails: {', '.join(whitelist_emails)}")
    
    return is_whitelisted

def get_whitelist_error_message() -> str:
    """
    Get the error message to display when an email is not whitelisted.
    
    Returns:
        str: Error message explaining the alpha release restriction
    """
    return (
        "🚀 We're currently in alpha release! "
        "Access is limited to approved beta testers. "
        "Please contact the development team if you'd like to join our beta program."
    )
