#!/usr/bin/env python
from email.mime.text import MIMEText
import smtplib
import sys

def send(recipient, sender, subject, body):
    message = MIMEText(body, _charset='UTF-8')
    message['Subject'] = subject
    message['From'] = sender
    message['To'] = recipient
    smtp = smtplib.SMTP('localhost')
    result = smtp.sendmail(sender, recipient, message.as_string())
    return result

if __name__ == '__main__':
    recipient = sys.argv[1]
    sender = sys.argv[2]
    subject = sys.argv[3]
    path_file = sys.argv[4]
    with open(path_file) as file_input:
        body = file_input.read()
    result = send(recipient, subject, body)
