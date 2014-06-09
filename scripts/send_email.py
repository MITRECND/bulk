#!/usr/bin/env python

# Copyright (c) 2014 The MITRE Corporation. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.

import os
import sys
import argparse
import smtplib
import email
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import formatdate
from email import Encoders


def send_mail(send_from, send_to, subject, text,
              files=[], server="localhost", port=1024):
    """
    Send an email.

    Keyword arguments:
    send_from -- sender's email address
    send_to -- recipient's email address
    subject -- email subject
    text -- email text body
    files -- email attachments
    server -- email server to use
    port -- server's listening port

    """
    assert type(files) == list

    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = send_to
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach(MIMEText(text))

    for f in files:
        part = MIMEBase('application', "octet-stream")
        part.set_payload(open(f, "rb").read())
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition',
                        'attachment; filename="%s"' % os.path.basename(f))
        msg.attach(part)

    smtp = smtplib.SMTP(server, port)
    smtp.sendmail(send_from, send_to, msg.as_string())
    smtp.close()

if __name__ == "__main__":
    """
    Main
    """
    parser = argparse.ArgumentParser(description='A simple SMTP Server')

    parser.add_argument(
        '--server',
        default='127.0.0.1',
        type=str,
        help='Address of remote server. Default is 127.0.0.1'
    )

    parser.add_argument(
        '--port',
        default=1025,
        type=int,
        help='Remote port to connect to to send mail. Default is 1025'
    )

    parser.add_argument(
        '--to',
        default='example@example.com',
        type=str,
        help='Recipient for email, default is example@example.com'
    )

    parser.add_argument(
        '--from',
        default='example@example.com',
        type=str,
        dest='recipient',
        help='Sender for email, default is example@example.com'
    )

    parser.add_argument(
        '--subject',
        default='Test message',
        type=str,
        help='Subject for message, default is "Test message"'
    )

    parser.add_argument(
        '--text',
        default='This is a short email',
        type=str,
        help='Main message body. Default is "This is a short email"'
    )

    parser.add_argument(
        '--text_file',
        type=str,
        dest='textfile',
        help='Read email body from a text file'
    )

    parser.add_argument(
        '--attachment',
        type=str,
        help='Path to file to use as attachment'
    )

    args = parser.parse_args()
    send_to = email.utils.formataddr(('Recipient', args.to))
    send_from = email.utils.formataddr(('Author', args.recipient))

    if args.attachment:
        files = [args.attachment]

    else:
        files = []

    if args.textfile:
        if os.path.isfile(args.textfile):
            try:
                with open(args.textfile, 'r') as f:
                    args.text = f.read()

            except IOError as e:
                print 'Cannot open and read text file %s, ' \
                      'exiting' % args.textfile
                sys.exit(1)

        else:
            print 'Cannot find text file %s, exiting' % args.textfile
            sys.exit(1)

    print 'Trying to send mail...'
    send_mail(send_from, send_to, args.subject, args.text,
              files, args.server, args.port)
    print 'Mail successfully sent!'
