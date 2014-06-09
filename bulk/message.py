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
import os
import uuid
import email
import datetime
import logging
import hashlib
import pickle


class Message(object):
    """
    A simple wrapper to access email data.
    """

    def __init__(self, peer, mailfrom, rcpttos, data):
        """
        Default initializer

        Sets up logging and parses pieces of the message.

        """
        self.logger = logging.getLogger('bulk')

        self._peer = peer
        self._mailfrom = mailfrom
        self._rcpttos = rcpttos
        self._data = data

        self._parsed_message = email.message_from_string(data)

        # Attachments
        self._attachment_names = []
        self._attachment_contents = []

    def __str__(self):
        """
        A nice way to print a message.
        """
        s = 'BULKMSG: Received message from : %s\n' % str(self._peer)
        s += 'BULKMSG: Message addressed from: %s\n' % str(self._mailfrom)
        s += 'BULKMSG: Message addressed to  : %s\n' % str(self._rcpttos)
        s += 'BULKMSG: Message length        : %s\n' % str(len(self._data))
        s += 'BULKMSG: Original message seen below\n'
        s += self._data

        return s

    def save(self, location):
        """
        Writes the message to a unique file in the
        supplied location.

        Keyword arguments:
        location -- path to write message to

        """
        fn = self.get_unique_filepath(location)
        self.logger.info('Saving message to %s' % fn)

        try:
            with open(fn, 'wb') as f:
                f.write(str(self))

        except IOError:
            self.logger.error('Cannot write to %s' % fn)
            self.logger.error('Ensure the directory exists \
                              and permissions are correct')

    def get_unique_filepath(self, basepath):
        """
        Given a base directory path, return a unique filename.

        Keyword arguments:
        basepath -- base directory path to append to

        """
        # Don't print '<>' when there is no sender
        if self._mailfrom == '<>':
            print "NORMALIZING FROM"
            mailfrom = 'None'

        else:
            mailfrom = self._mailfrom

        fn = basepath
        fn += '%s' % mailfrom
        fn += datetime.datetime.now().strftime('_%Y-%m-%d_%H-%M-%S_')
        fn += str(uuid.uuid4())

        return fn

    def get_attachments(self):
        """
        Pull attachments from a message.

        Returns two lists, one of the attachment names
        and another of the attachment contents.

        """

        attachment_names = []
        attachment_contents = []

        for part in self._parsed_message.walk():
            attachment_name = part.get_filename()

            if attachment_name:
                self.logger.info('Found attachment; Name: %s' % attachment_name)
                attachment_names.append(attachment_name)
                attachment_contents.append(part.get_payload(decode=True))

        self._attachment_names = attachment_names
        self._attachment_contents = attachment_contents
        return (attachment_names, attachment_contents)

    def save_attachments(self, location):
        """
        Save attachments and report to a directory.

        Keyword arguments:
        location -- directory to save attachements to

        Attachments are saved to <md5>.file.
        Reported info is saved to <md5>.report.
        """
        self.logger.debug('Saving attachments to disk')
        # In case the attachments have not been
        # populated, we can try ourselves.
        if not self._attachment_names:
            self.logger.debug('No attachments found, trying to parse them now')
            self.get_attachments()

        for i, filename in enumerate(self._attachment_names):
            # Write a report file
            md5 = hashlib.md5(self._attachment_contents[i]).hexdigest()
            report = location + md5 + '.pkl'

            fn = location + md5 + '.file'
            try:
                with open(fn, 'wb') as f:
                    f.write(str(self._attachment_contents[i]))

            except IOError:
                self.logger.error('Cannot write to %s' % fn)
                self.logger.error('Ensure the directory exists \
                                  and permissions are correct')

            # Going to pickle this data to disk for now
            content = {}
            content['name'] = filename
            content['size'] = str(os.path.getsize(fn))
            content['from'] = str(self._peer)
            content['mailed_from'] = str(self._mailfrom)
            content['to'] = str(self._rcpttos)
            content['email'] = str(self)
            content['attachment'] = fn
            content['md5'] = md5

            try:
                with open(report, 'wb') as f:
                    pickle.dump(content, f)

            except IOError:
                self.logger.error('Cannot write to %s' % report)
                self.logger.error('Ensure the directory exists \
                                  and permissions are correct')
