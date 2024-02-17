"""
This module provides a chatbot to entertain scammers, it is going to reply to all users
"""

# Importing system packages
import os
import logging
import time
import email
from email.mime.text import MIMEText
import smtplib
# Import additional classes
import g4f
import sqlite3
from imapclient import IMAPClient

logging.getLogger().setLevel(logging.DEBUG)
logging.getLogger('imapclient').setLevel(logging.WARNING)

class EmptyStringError(Exception):
    """
    Returns a ValueError if string is null or empty
    """
    def __init__(self, message="String is empty or None"):
        self.message = message
        super().__init__(self.message)

class EmailMessage:
    """
    Custom class to better manage emails content
    """
    sender: str
    subject: str
    body: str
    my_email: str #TODO: handle forwarded emails
    reply: str
    
    def __init__(self, sender, subject, body, my_email):
        self.sender = sender
        self.subject = subject
        self.body = body
        self.my_email = my_email
        self.reply = ""
    
    def __str__(self):
        return f"From: {self.sender}\nSubject: {self.subject}\nBody: {self.body}\nReply: {self.reply}"

class EmailClient:
    """
    Wrapper for the imapclient module, provides authentication,
    gets emails and replies to them
    """
    imap_server: IMAPClient
    username: str
    password: str
    imap_address: str
    smtp_address: str
    search_filter: str

    def __init__(self, imap_address, username, password, smtp_address, search_filter) -> None:
        logging.info("Validating connection details...")
        self.username = username
        self.password = password
        self.imap_address = imap_address
        self.smtp_address = smtp_address
        self.search_filter = search_filter
        self.validate_connection_details()
        logging.info("Validation passed, logging into %s as %s", imap_address, username)
        self.imap_server = IMAPClient(imap_address, use_uid=True)
        self.imap_server.login(username, password)

    def validate_connection_details(self):
        """
        Check if all fields are not null or empty

        Raises:
            EmptyStringError: _description_
            EmptyStringError: _description_
            EmptyStringError: _description_
            EmptyStringError: _description_
        """
        if not self.imap_address:
            logging.error("imap_address variable is invalid")
            raise EmptyStringError()
        if not self.username:
            logging.error("username variable is invalid")
            raise EmptyStringError()
        if not self.password:
            logging.error("password variable is invalid")
            raise EmptyStringError()
        if not self.smtp_address:
            logging.error("smtp_address variable is invalid")
            raise EmptyStringError()
        if not self.search_filter:
            logging.error("search_filter variable is invalid")
            raise EmptyStringError()

    def get_unread_emails_cnt(self) -> int:
        """
        Returns the number of unread emails in the INBOX folder       

        Returns:
            int: Count of unread emails in inbox
        """
        select_info = self.imap_server.select_folder('INBOX')
        unread_emails = self.imap_server.search([self.search_filter])
        return len(unread_emails)

    def get_unread_emails(self) -> list:
        """
        Retrieves unread emails from the INBOX folder
        
        Returns:
            list: List of EmailMessage objects representing unread emails
        """
        email_ids = self.imap_server.search([self.search_filter])
        unread_emails = []
        for email_id in email_ids:
            email_data = self.imap_server.fetch([email_id], ['RFC822'])
            raw_email = email_data[email_id][b'RFC822']
            email_message = email.message_from_bytes(raw_email)
            sender = email_message['From']
            subject = email_message['Subject']
            body = email_message.get_payload()
            if len(body) > 1:
                body = body[0]
            else:
                body = body.as_string()
            for part in body.walk():
                if part.get_content_type() == "text/plain":
                    body = str(part)
            email_obj = EmailMessage(sender, subject, body, self.username)
            unread_emails.append(email_obj)
        return unread_emails

    def reply_to_email(self, email_obj: EmailMessage) -> None:
        """
        Reply to an email using SMTP.

        Args:
            email_obj (EmailMessage): The email message object to reply to.
            reply_content (str): The content of the reply message.
        """
        smtp_port = 587  # Change this according to your SMTP server configuration
        
        msg = MIMEText(email_obj.reply)
        msg['From'] = self.username
        msg['To'] = email_obj.sender
        if "Re: " not in msg['Subject']:
            msg['Subject'] = f"Re: {email_obj.subject}"
        else:
            msg['Subject'] = email_obj.subject

        with smtplib.SMTP(self.smtp_address, smtp_port) as server:
            server.starttls()  # Enable TLS encryption
            server.login(self.username, self.password)
            server.sendmail(self.username, email_obj.sender, msg.as_string())

def gpt_response(email_body) -> str:
    """
    Wrapper for GPT4Free library, provides the personality
    and the body of the email to the AI model in order to
    get a reply to be sent back

    Args:
        email_body (_type_): _description_

    Returns:
        str: _description_
    """
    # GPT4Free settings
    g4f.debug.logging = True  # Enable debug logging
    g4f.debug.version_check = False  # Disable automatic version checking

    personality = os.getenv('SCAMMERREPLIER_PERS')
    if not personality:
        logging.debug("Applying default personality")
        personality = "Sei Luca, una persona che ha ricevuto questa mail da parte di un truffatore e vuole mantenere attiva la conversazione con il truffatore per fargli perdere tempo ed evitare che truffi altre persone, non sono richiesti consulti legali o consulenze, devi solo rispondergli come fossi un utente che ha abboccato:"
    else:
        logging.debug("Using custom personality")

    ## Normal response
    response = g4f.ChatCompletion.create(
        model=g4f.models.gpt_4,
        messages=[{"role": "user", "content": f"{personality}\n\n\"{email_body}\""}],
    )
    if len(response) > 10:
        logging.debug("Got a response from the chatbot: %s", response)
        return response
    else:
        logging.warning("Chatbot returned: %s", response)
        return ""

def init_mail_server() -> EmailClient:
    """
    Initialize connection with the mail server

    Raises:
        SystemExit: _description_

    Returns:
        EmailClient: email server as configured from env
    """
    try:
        mail_server = EmailClient(
                        os.getenv('SCAMMERREPLIER_IMAP'),
                        os.environ.get('SCAMMERREPLIER_USER'),
                        os.environ.get('SCAMMERREPLIER_PASS'),
                        os.environ.get('SCAMMERREPLIER_SMTP'),
                        os.environ.get("SCAMMERREPLIER_FILTER", default="UNSEEN").upper())
    except Exception as ret_exc:
        logging.error("Cannot access mail server, error: %s", ret_exc)
        raise SystemExit from ret_exc
    
    return mail_server

def get_unread_emails_from_imap(mail_server) -> list[EmailMessage]:
    """
    Process emails from the imap server

    Raises:
        SystemExit: Thrown if we cannot access to mailbox
    Returns:
        A list of EmailMessage(s) to be processed
    """
    # Init email client
    try:
        unread_emails_cnt = mail_server.get_unread_emails_cnt()
    except Exception as ret_exc:
        logging.error("Cannot access mail server, error: %s", ret_exc)
        raise SystemExit from ret_exc
    if unread_emails_cnt > 0:
        logging.debug("Hurray! We got %i email(s) to process!", unread_emails_cnt)
        unread_emails = mail_server.get_unread_emails()
        return unread_emails
    else:
        logging.debug("No new emails to process")

def generate_replies(input_list: list[EmailMessage]) -> list[EmailMessage]:
    """
    Generates a reply for each unread message

    Args:
        input_list (list[EmailMessage]): List of emails to be read and processed

    Returns:
        list[EmailMessage]: Same list of emails but with a reply to be sent
    """

    for new_email in input_list:
        logging.debug("Generating answer for email from: [%s], subject: [%s]", str(new_email.sender), str(new_email.subject))
        logging.debug("\tBody: %s", new_email.body)
        if len(new_email.body) > 5:
            new_email.reply = gpt_response(new_email.body)
        else:
            logging.warning("Body: [%s] is too short to be processed", str(new_email.body))

    return input_list

def main():
    """
    Performs a check every 15 minutes to the email box,
    reads if any email is in there and tries to reply
    """
    while True:
        mail_server = init_mail_server()
        unread_emails = get_unread_emails_from_imap(mail_server)
        if unread_emails:
            emails_with_replies = generate_replies(unread_emails)
            # for single_email in emails_with_replies:
            #     if len(single_email.reply) > 5:
            #         mail_server.reply_to_email(single_email)
            #     else:
            #         logging.warning("Reply [%s] is too short to be sent", single_email.reply)
        # Waits for next execution
        logging.info("Waiting for next execution...")
        time.sleep(int(os.getenv('SCAMMERREPLIER_TIME', default="600")))

if __name__ == "__main__":
    main()