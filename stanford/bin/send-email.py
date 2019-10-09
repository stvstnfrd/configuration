#!/usr/bin/env python
from email.mime.text import MIMEText
import os
from subprocess import call
import sys

def send(recipient, sender, sender_name, subject, body):
    email_params_file = 'configuration-secure/jenkins/cut-release-branch/email_params.txt'
    email_params_file = os.environ.get('CONFIGURATION_EMAIL_PARAMS', email_params_file)
    with open(email_params_file, 'rt') as fin:
        with open('email.txt', 'wt') as fout:
            for line in fin:
                line = line.replace('{RECIPIENT}', recipient).replace('{SENDER}', sender).replace('{SENDER_NAME}', sender_name).replace('{SUBJECT}', subject).replace('{BODY}', body)
                fout.write(line)

    cmd = ['openssl', 's_client', '-crlf', '-quiet', '-connect', 'email-smtp.us-east-1.amazonaws.com:465']
    with open('email.txt') as fout:
        call(cmd, stdin=fout)
    call(['rm', 'email.txt'])

if __name__ == '__main__':
    recipient = sys.argv[1]
    sender = sys.argv[2]
    sender_name = sys.argv[3]
    subject = sys.argv[4]
    path_file = sys.argv[5]
    with open(path_file) as file_input:
        body = file_input.read()
    result = send(recipient, sender, sender_name, subject, body)
