from private_password import my_gmail_address, my_gmail_password
import smtplib
import ssl
from email.message import EmailMessage

email_sender = my_gmail_address
email_password = my_gmail_password

def send_email(email_receiver: str, email_type: str):

    if email_type == 'promotion_approved':
        subject = 'Promote-to-director request in MatchScore App'
        body = "Greetings,\n\nWe are happy to inform you that your request for a promotion in MatchScore App was approved!\n\nYou can now organize tournaments and matches.\n\nBest regards,\n\n----------------------------------------\nSteven Atkinson\nSenior Admin | Match Score App - since 2023\n\nEmail: matchscoretelerik@gmail.com\nPhone: +33756495992\nAddress: 51 Alpha street, 1000, Sofia, Bulgaria"
    
    elif email_type == 'promotion_declined':
        subject = 'Promote-to-director request in MatchScore App'
        body = "Greetings,\n\nUnfortunately we must inform you that your request for a promotion was declined!\n\nDon't worry, your player's account will keep being active.\n\nBest regards,\n\n----------------------------------------\nSteven Atkinson\nSenior Admin | Match Score App - since 2023\n\nEmail: matchscoretelerik@gmail.com\nPhone: +33756495992\nAddress: 51 Alpha street, 1000, Sofia, Bulgaria"
    
    elif email_type == 'link_profile_approved':
        subject = 'Link-profile request in MatchScore App'
        body = "Greetings,\n\nWe are happy to inform you that your request to be linked with a player's account in MatchScore App was approved.\n\nYou can now edit your player's account.\n\nBest regards,\n\n----------------------------------------\nSteven Atkinson\nSenior Admin | Match Score App - since 2023\n\nEmail: matchscoretelerik@gmail.com\nPhone: +33756495992\nAddress: 51 Alpha street, 1000, Sofia, Bulgaria"
    
    elif email_type == 'link_profile_declined':
        subject = 'Link-profile request in MatchScore App'
        body = "Greetings,\n\nUnfortunately we must inform you that your request to be linked with a player's account was declined.\n\nBest regards,\n\n----------------------------------------\nSteven Atkinson\nSenior Admin | Match Score App - since 2023\n\nEmail: matchscoretelerik@gmail.com\nPhone: +33756495992\nAddress: 51 Alpha street, 1000, Sofia, Bulgaria"
    
    elif email_type == 'added_to_tournament':
        subject = 'Added to a tournament in MatchScore App'
        body = "Greetings,\n\nYour player's account has been added to a tournament.\n\nPlease visit our MatchScore App to see details.\n\nBest regards,\n\n----------------------------------------\nSteven Atkinson\nSenior Admin | Match Score App - since 2023\n\nEmail: matchscoretelerik@gmail.com\nPhone: +33756495992\nAddress: 51 Alpha street, 1000, Sofia, Bulgaria"
    
    elif email_type == 'added_to_match':
        subject = 'Added to a match in MatchScore App'
        body = "Greetings,\n\nYour player's account has been added to a match.\n\nPlease visit our MatchScore App to see details.\n\nBest regards,\n\n----------------------------------------\nSteven Atkinson\nSenior Admin | Match Score App - since 2023\n\nEmail: matchscoretelerik@gmail.com\nPhone: +33756495992\nAddress: 51 Alpha street, 1000, Sofia, Bulgaria"
    
    elif email_type == 'match_changed':
        subject = 'Date and/or score of a match in MatchScore App'
        body = "Greetings,\n\nA date and/or score in a match in which you participate as a player has been changed.\n\nPlease visit our MatchScore App to see details.\n\nBest regards,\n\n----------------------------------------\nSteven Atkinson\nSenior Admin | Match Score App - since 2023\n\nEmail: matchscoretelerik@gmail.com\nPhone: +33756495992\nAddress: 51 Alpha street, 1000, Sofia, Bulgaria"

    elif email_type == 'verified':
        subject = 'Succesful verification in MatchScore App'
        body = "Greetings,\n\nYou are now a verified user in MatchScore App.\n\nBest regards,\n\n----------------------------------------\nSteven Atkinson\nSenior Admin | Match Score App - since 2023\n\nEmail: matchscoretelerik@gmail.com\nPhone: +33756495992\nAddress: 51 Alpha street, 1000, Sofia, Bulgaria"
    

    # Create 'em' structure of the email
    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(body)

    # Add SSL (layer of security)
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    # Log in and send the email
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())


def send_verification_email(email_receiver: str, verification_code: int):
    subject = 'Please verify your account in MatchScore App'
    body = f"Greetings,\n\nWelcome in MatchScore App!\n\nThe final step of the registration process is to verify your account. Your verification code is: {verification_code}.\n\nBest regards,\n\n----------------------------------------\nSteven Atkinson\nSenior Admin | Match Score App - since 2023\n\nEmail: matchscoretelerik@gmail.com\nPhone: +33756495992\nAddress: 51 Alpha street, 1000, Sofia, Bulgaria"


    # Create 'em' structure of the email
    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(body)

    # Add SSL (layer of security)
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    # Log in and send the email
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())