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

# Standard Imports
import smtpd
import logging
import hashlib

# Bulk Imports
from bulk import message


class BulkProxy(smtpd.PureProxy):
    """
    A simple message inspecting SMTP proxy.
    """

    def __init__(self, localaddress, remoteaddress, processors, **kwargs):
        """
        Default initializer.

        Sets up logging and the processing engines.

        """
        # Get a handle to the bulk logger
        self.logger = logging.getLogger('bulk')
        # Basic private variables
        self._localaddress = localaddress
        self._remoteaddress = remoteaddress
        # Processors is a handle to the active analysis engine
        # Currently only one is supported
        self._processors = processors

        # Optional keyword arguments
        self._basedir = kwargs.get('base_directory', '/tmp/')
        self._block = kwargs.get('block', False)
        # This flag changes functionality from a proxy to a server
        # I.E. no forwarding messages upstram, ever
        self._always_block = kwargs.get('always_block', False)
        # Do we want to save attachments?
        self._save_attachments = kwargs.get('save_attachments', False)
        # Do we want to store ALL messages for later anaylsis?
        self._log = kwargs.get('log', False)
        # These paths are hardcoded and based off the base directory
        self._quarantine_directory = self._basedir + 'quarantine/'
        self._message_directory = self._basedir + 'messages/'
        self._attachment_directory = self._basedir + 'attachments/'

        # Call the base class
        smtpd.PureProxy.__init__(self, localaddress, remoteaddress)

    def process_message(self, peer, mailfrom, rcpttos, data):
        """
        process_message is called once per incoming message/email.

        Keyword arguments:
        peer -- tuple containing (ipaddr, port) of the client that made the
        socket connection to our smtp port.

        mailfrom -- raw address the client claims the message is coming
        from.

        rcpttos -- list of raw addresses the client wishes to deliver the
        message to.

        data -- string containing the entire full text of the message,
        headers (if supplied) and all.  It has been `de-transparencied'
        according to RFC 821, Section 4.5.2.  In other words, a line
        containing a `.' followed by other text has had the leading dot
        removed.

        Messages are handed over to a 'processor(s)' which uses yara or
        another engine to analyze the email attachments.
        """
        # Do some logging
        self.logger.info('Messaged received; From: %s; To: %s'
                         % (str(mailfrom), str(rcpttos)))

        msg = message.Message(peer, mailfrom, rcpttos, data)

        # Do we want to log all? Usually no
        if self._log:
            msg.save(self._message_directory)

        # If we don't want to block emails EVER, then
        # we send them along first, then analyze later
        if not self._block:
            self.deliver_message(peer, mailfrom, rcpttos, data)

        # Pull the attachments out of the message
        attachment_names, attachment_contents = msg.get_attachments()

        # Now that we have all the attachments, time to check them
        clean = True
        for i, filename in enumerate(attachment_names):
            md5 = hashlib.md5(attachment_contents[i]).hexdigest()
            self.logger.info('Analyzing attachment; From: %s; To: %s; ' \
                             'Name: %s; MD5:%s' % (str(mailfrom),
                                                  str(rcpttos),
                                                  filename, md5))

            for processor in self._processors:
                malicious = processor.match(attachment_contents[i])

                if malicious:
                    clean = False

        # Once looking at all attachments, we can decide to deliver or not
        if clean:
            self.logger.info('Message clean; From: %s; To: %s'
                         % (str(mailfrom), str(rcpttos)))

            if self._block:
                self.deliver_message(peer, mailfrom, rcpttos, data)

        else:
            if self._block:
                self.logger.info('Message blocked; From: %s; To: %s'
                         % (str(mailfrom), str(rcpttos)))

            msg.save(self._quarantine_directory)

        # Do we want to save attachments?
        if self._save_attachments:
            msg.save_attachments(self._attachment_directory)

    def deliver_message(self, peer, mailfrom, rcpttos, data):
        """
        Delivers a message to final destination if allowed
        """
        if not self._always_block:
            self.logger.info('Sending message; From: %s; To: %s'
                         % (str(mailfrom), str(rcpttos)))
            self._deliver(mailfrom, rcpttos, data)
