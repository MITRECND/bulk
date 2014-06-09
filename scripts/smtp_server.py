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

import smtpd
import email
import asyncore
import argparse


class CustomSMTPServer(smtpd.SMTPServer):
    """
    A simple SMTP server.
    """

    def process_message(self, peer, mailfrom, rcpttos, data):
        """
        Process each message as it arrives
        """
        print 'Receiving message from:', peer
        print 'Message addressed from:', mailfrom
        print 'Message addressed to  :', rcpttos
        print 'Message length        :', len(data)

        filenames = []
        attachments = []

        msg = email.message_from_string(data)

        for k, v in msg.items():
            print k + " -- " + v

        for part in msg.walk():
            #help(part)
            fn = part.get_filename()

            if fn:
                filenames.append(fn)
                attachments.append(part.get_payload(decode=True))


if __name__ == '__main__':
    """
    Main
    """
    parser = argparse.ArgumentParser(description='A simple SMTP Server')

    parser.add_argument(
        '--bind_address',
        default='127.0.0.1',
        help='Address to bind to and listen on for incoming mail. \
              Default is 127.0.0.1'
    )

    parser.add_argument(
        '--bind_port',
        default=1025,
        type=int,
        help='Port to bind to and to listen on for incoming mail. \
              Default is 1025'
    )

    args = parser.parse_args()
    server = CustomSMTPServer((args.bind_address, args.bind_port), None)

    try:
        print 'Starting Server'
        asyncore.loop()

    except KeyboardInterrupt:
        print 'Stopping Server'
