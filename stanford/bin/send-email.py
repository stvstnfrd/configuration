#!/usr/bin/env python
from email.mime.text import MIMEText
from subprocess import call
import sys

def send(recipient, sender, sender_name, subject, body):
    with open('configuration/stanford/bin/email_params.txt', 'rt') as fin:
        with open('email.txt', 'wt') as fout:
            for line in fin:
                line = line.replace('{RECIPIENT}', recipient).replace('{SENDER}', sender).replace('{SENDER_NAME}', sender_name).replace('{SUBJECT}', subject).replace('{BODY}', body)
                fout.write(line)

    fout = open('email.txt')
    cmd = ['openssl', 's_client', '-crlf', '-quiet', '-connect', 'email-smtp.us-east-1.amazonaws.com:465']
    call(cmd, stdin=fout)
    fout.close()
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
