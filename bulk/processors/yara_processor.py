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
import logging
import hashlib

# Libary Imports
import yara


class Processor(object):
    """
    A simple wrapper to yara.

    Ideally, this will provide interfaces for updating
    rules files, managing detailed logging, and any
    extra analysis needs (metrics, reporting, etc)).
    """

    def __init__(self, rule_files):
        """
        Default initializer.

        Keyword arguments:
        rules -- dictionary of namespaces:/path/to/file

        """
        # Handle logger
        self.logger = logging.getLogger('bulk')

        self._rule_files = rule_files
        self._rules = None

        # Try to load the rules into yara
        try:
            self.logger.debug('Loading rules into yara: %s' % self._rule_files)
            self._rules = yara.compile(filepaths=self._rule_files)

        except yara.Error as e:
            self.logger.error('Cannot find rules file: %s, \
                              exiting' % self._rule_files)
            raise

    def __str__(self):
        """
        Pretty way to print processor.
        """
        s = 'Processor ' + __name__
        if self._rule_files:
            s += ' running with rules ' + ' '.join(self._rule_files.values())

        return s

    def match(self, data):
        """
        Run yara against a blob of data and True or False
        based on whether a match was found.

        Keyword arguments:
        data -- blob of data to analyze

        Returns True or False.

        """
        self.logger.debug('Running yara against data')
        malicious = self._rules.match(data=data)
        md5 = hashlib.md5(data).hexdigest()
        if malicious:
            for match in malicious:
                self.logger.info('Match found; Rule: \'%s\';'
                                 'Namespace: \'%s\'; MD5: %s' %
                                 (match.rule, match.namespace, md5))

            return True

        return False
