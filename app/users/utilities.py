import os
import secrets
from flask import current_app,url_for
from app import mail
from flask_mail import Message
from PIL import Image
import logging
logger = logging.getLogger(__name__)

def save_prof_pic(form_pic):
    rand_hex=secrets.token_hex(8)
    try:
        _, ext = os.path.splitext(form_pic.filename)
        if not ext.lower() in {'.jpg', '.jpeg', '.png'}:
            raise ValueError("Invalid file extension")
    except (ValueError, AttributeError) as e:
        logger.error(f"File processing error: {e}")
        raise
    pic_name=rand_hex+ext
    pic_path=os.path.join(current_app.root_path,'static','profile_pics',pic_name)
    
    output_size=(100,100)
    i=Image.open(form_pic)
    i.thumbnail(output_size)
    i.save(pic_path)
    
    return pic_name

def send_reset_email(user):
    token=user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender=current_app.config['MAIL_DEFAULT_SENDER'],
                  recipients=[user.email])
    
    msg.body = f'''To reset your password, visit the following link:
{url_for('users.reset_token', token=token, _external=True)}
    
If you did not make this request, simply ignore this email and no changes will be made.
    
This link will expire in 10 minutes.
    
Best regards,
Finance Tracker Team
'''
    
    msg.html = f'''
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #4e73df;">Password Reset Request</h2>
        <p>Hello {user.username},</p>
        <p>We received a request to reset your password. Click the button below to reset it:</p>
        <div style="text-align: center; margin: 30px 0;">
            <a href="{url_for('users.reset_token', token=token, _external=True)}" 
               style="background-color: #4e73df; color: white; padding: 12px 30px; 
                      text-decoration: none; border-radius: 5px; display: inline-block;">
                Reset Password
            </a>
        </div>
        <p><strong>This link will expire in 10 minutes.</strong></p>
        <p>If you did not request a password reset, please ignore this email.</p>
        <hr style="border: 1px solid #e3e6f0; margin: 20px 0;">
        <p style="color: #858796; font-size: 12px;">
            If the button doesn't work, copy and paste this link into your browser:<br>
            <a href="{url_for('users.reset_token', token=token, _external=True)}">{url_for('users.reset_token', token=token, _external=True)}</a>
        </p>
    </div>
    '''
    
    mail.send(msg)
