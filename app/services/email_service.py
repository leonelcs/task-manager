"""
Email service for sending group invitations and notifications.
"""
from typing import Optional
from app.schemas.invitation import InvitationEmailData
import logging

logger = logging.getLogger(__name__)


async def send_invitation_email(email_data: InvitationEmailData):
    """
    Send group invitation email with ADHD-friendly messaging.
    
    For now, this is a placeholder that logs the email content.
    In production, this would integrate with an email service like SendGrid, Mailgun, etc.
    """
    try:
        # Log the email content for development
        logger.info("=" * 60)
        logger.info("📧 GROUP INVITATION EMAIL (DEVELOPMENT MODE)")
        logger.info("=" * 60)
        logger.info(f"To: {email_data.recipient_email}")
        logger.info(f"Subject: You're invited to join '{email_data.group_name}' - ADHD Support Group")
        logger.info("")
        logger.info("⚠️  IMPORTANT FOR DEVELOPMENT:")
        logger.info(f"   Since email is not configured, the user should visit:")
        logger.info(f"   🔗 {email_data.invitation_url}")
        logger.info(f"   📧 Or check their invitations at: http://localhost:3000/invitations")
        logger.info("")
        logger.info("Email Content:")
        logger.info("-" * 30)
        
        email_content = generate_invitation_email_html(email_data)
        logger.info(email_content[:500] + "..." if len(email_content) > 500 else email_content)
        
        logger.info("=" * 60)
        logger.info("💡 To enable real email sending:")
        logger.info("   1. Configure SendGrid, Mailgun, or similar service")
        logger.info("   2. Add email service credentials to environment")
        logger.info("   3. Uncomment the email sending code below")
        logger.info("=" * 60)
        
        # TODO: Integrate with actual email service
        # Example with SendGrid:
        # import sendgrid
        # from sendgrid.helpers.mail import Mail
        # 
        # sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
        # message = Mail(
        #     from_email='noreply@adhdtaskmanager.com',
        #     to_emails=email_data.recipient_email,
        #     subject=f"You're invited to join '{email_data.group_name}' - ADHD Support Group",
        #     html_content=email_content
        # )
        # response = sg.send(message)
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to send invitation email: {str(e)}")
        return False


def generate_invitation_email_html(email_data: InvitationEmailData) -> str:
    """
    Generate ADHD-friendly invitation email HTML content.
    """
    recipient_name = email_data.recipient_name or "there"
    
    # Build ADHD features list
    features_html = ""
    if email_data.group_features:
        features_list = []
        if email_data.group_features.get("group_focus_sessions"):
            features_list.append("🎯 Group Focus Sessions (Body Doubling)")
        if email_data.group_features.get("shared_energy_tracking"):
            features_list.append("⚡ Shared Energy Tracking")
        if email_data.group_features.get("group_dopamine_celebrations"):
            features_list.append("🎉 Group Dopamine Celebrations")
        if email_data.group_features.get("collaborative_task_chunking"):
            features_list.append("🔧 Collaborative Task Chunking")
        if email_data.group_features.get("accountability_features"):
            features_list.append("🤝 Accountability Features")
        
        if features_list:
            features_html = "<ul>" + "".join([f"<li>{feature}</li>" for feature in features_list]) + "</ul>"
    
    # Personal message section
    personal_message_html = ""
    if email_data.invitation_message:
        personal_message_html = f"""
        <div style="background: #f0f9ff; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #3b82f6;">
            <h3 style="color: #1e40af; margin: 0 0 10px 0;">💬 Personal Message from {email_data.inviter_name}:</h3>
            <p style="margin: 0; font-style: italic; color: #374151;">"{email_data.invitation_message}"</p>
        </div>
        """
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ADHD Support Group Invitation</title>
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #374151; max-width: 600px; margin: 0 auto; padding: 20px;">
        
        <!-- Header -->
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #3b82f6; margin: 0; font-size: 28px;">🧠✨ ADHD Task Manager</h1>
            <p style="color: #6b7280; margin: 5px 0 0 0;">Your ADHD-friendly productivity companion</p>
        </div>
        
        <!-- Main Invitation -->
        <div style="background: linear-gradient(135deg, #dbeafe 0%, #f3e8ff 100%); padding: 30px; border-radius: 12px; text-align: center; margin-bottom: 30px;">
            <h2 style="color: #1e40af; margin: 0 0 15px 0; font-size: 24px;">🎉 You're Invited!</h2>
            <p style="margin: 0 0 20px 0; font-size: 18px; color: #374151;">
                <strong>{email_data.inviter_name}</strong> has invited you to join
            </p>
            <h3 style="color: #7c3aed; margin: 0 0 10px 0; font-size: 22px;">"{email_data.group_name}"</h3>
            {f'<p style="color: #6b7280; margin: 0; font-size: 16px;">{email_data.group_description}</p>' if email_data.group_description else ''}
        </div>
        
        {personal_message_html}
        
        <!-- Why Join Section -->
        <div style="margin: 30px 0;">
            <h3 style="color: #059669; margin: 0 0 15px 0;">🌟 Why Join an ADHD Support Group?</h3>
            <ul style="color: #374151; padding-left: 20px;">
                {chr(10).join([f'<li style="margin: 8px 0;">{benefit}</li>' for benefit in email_data.adhd_benefits])}
            </ul>
        </div>
        
        {f'''
        <!-- Group Features -->
        <div style="margin: 30px 0;">
            <h3 style="color: #7c2d12; margin: 0 0 15px 0;">🚀 This Group's ADHD Features:</h3>
            {features_html}
        </div>
        ''' if features_html else ''}
        
        <!-- CTA Button -->
        <div style="text-align: center; margin: 40px 0;">
            <a href="{email_data.invitation_url}" 
               style="display: inline-block; background: #3b82f6; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 16px; margin: 10px;">
                🎯 Accept Invitation
            </a>
            <br>
            <p style="color: #6b7280; font-size: 14px; margin: 15px 0 0 0;">
                Or copy and paste this link: <br>
                <span style="font-family: monospace; background: #f9fafb; padding: 5px; word-break: break-all;">{email_data.invitation_url}</span>
            </p>
        </div>
        
        <!-- Community Guidelines Preview -->
        <div style="background: #f9fafb; padding: 20px; border-radius: 8px; margin: 30px 0;">
            <h4 style="color: #374151; margin: 0 0 15px 0;">💗 Our Community Values:</h4>
            <ul style="color: #6b7280; font-size: 14px; margin: 0; padding-left: 20px;">
                <li>🤝 Support over judgment</li>
                <li>🎯 Progress over perfection</li>
                <li>💬 Understanding over criticism</li>
                <li>🌟 Celebration over comparison</li>
            </ul>
        </div>
        
        <!-- Expiry Notice -->
        {f'''
        <div style="background: #fef3c7; padding: 15px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #f59e0b;">
            <p style="margin: 0; color: #92400e; font-size: 14px;">
                ⏰ <strong>This invitation expires on {email_data.expires_at.strftime("%B %d, %Y at %I:%M %p") if email_data.expires_at else "in 7 days"}</strong>
            </p>
        </div>
        ''' if email_data.expires_at else ''}
        
        <!-- Footer -->
        <div style="border-top: 1px solid #e5e7eb; padding-top: 20px; margin-top: 40px; text-align: center; color: #6b7280; font-size: 14px;">
            <p>Need help? Have questions about ADHD and productivity?</p>
            <p>Reply to this email or visit our support page.</p>
            <p style="margin-top: 20px;">
                <em>This invitation was sent by {email_data.inviter_name} through ADHD Task Manager</em>
            </p>
        </div>
    </body>
    </html>
    """
    
    return html_content


async def send_welcome_email(user_email: str, user_name: str, group_name: str):
    """
    Send welcome email after user joins a group.
    """
    logger.info(f"📧 Welcome email would be sent to {user_email} for joining {group_name}")
    # TODO: Implement welcome email
    pass


async def send_group_notification(shared_group_id: str, message: str, notification_type: str = "info"):
    """
    Send notification to all group members.
    """
    logger.info(f"📧 Group notification would be sent to group {shared_group_id}: {message}")
    # TODO: Implement group notifications
    pass
