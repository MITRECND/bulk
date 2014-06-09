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

import argparse

from bulk import message
from bulk.helpers import *


def get_message(filename):
    """
    Load message from file.

    Keyword arguments:
    filename -- path to message

    """
    try:
        with open(filename) as f:
            lines = f.readlines()

    except IOError:
        print 'Cannot open email file %s, exiting!' % filename
        raise

    # Filter a list of strings by removing all strings starting with 'BULKMSG:'
    # Then concatenate all the remaining strings into one string
    # and return it
    return ''.join([line for line in lines if not line.startswith('BULKMSG:')])


def save(name, contents):
    """
    Write contents to file.

    Keyword arguments:
    name -- file to write to
    contents -- contents to write to file

    """
    try:
        with open(name, 'wb') as f:
            f.write(contents)

    except IOError:
        print 'Cannot write file %s to disk, skipping!' % name

if __name__ == '__main__':
    """
    Main
    """
    parser = argparse.ArgumentParser(description='A simple tool to pull \
                                     attachments out of an email')

    parser.add_argument(
        '--infile',
        type=str,
        required=True,
        help='Email file to pull attachments out of'
    )

    parser.add_argument(
        '--output_path',
        default='./',
        type=str,
        help='Optional path to write attachments to. \
             Default is current directory.'
    )

    args = parser.parse_args()

    print 'Reading email from file %s' % args.infile
    msg = message.Message(None, None, None, get_message(args.infile))

    (names, contents) = msg.get_attachments()

    for i, name in enumerate(names):
        print 'Writing attachment %s to disk' % name
        save(directory_name(args.output_path) + name, contents[i])
