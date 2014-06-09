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

# Standard Imports
import re
import os
import errno
import argparse
import asyncore
import logging
import logging.config

# Bulk Imports
from bulk.proxy import BulkProxy
from bulk.helpers import *


class CreateProcessor(argparse.Action):
    """
    A custom argparse action.

    Instantiates a processing engine to be used in Bulk
    and appends it to the list of actively used processing
    engines.

    """

    def __call__(self, parser, namespace, values, option_string=None):
        """
        Instantiate a processing engine and append it to the active set.
        """
        module_name = values[0]
        rule_files = values[1:]

        # check the rules files
        for fn in rule_files:
            if os.path.isfile(fn):
                try:
                    with open(fn):
                        pass

                except IOError:
                    raise IOError((errno.EACCES,
                                  'Cannot open and read rules file.', fn))

            else:
                raise IOError((errno.ENOENT, 'Cannot find rules file.', fn))

        current_processors = getattr(namespace, self.dest)
        current_processors.append(build_processor(module_name,
                                                  convert_rules(rule_files)))
        setattr(namespace, self.dest, current_processors)


def setup_logging(config):
    """
    Configure logging for Bulk.

    Keyword arguments:
    config -- path to logging config file

    Returns a logger.

    """
    done = False
    while not done:
        try:
            logging.config.fileConfig(config)

        except IOError as e:
            if e.args[0] == errno.ENOENT and e.filename:

                print "The full path to the log file (%s) does not exist!" \
                      " Trying to recover." % e.filename
                fp = os.path.dirname(e.filename)

                if not os.path.exists(fp):
                    os.makedirs(fp)

                else:
                    print "Failed to setup logging, exiting."
                    raise

            else:
                print "Failed to setup logging," \
                      " check permissions on log file."
                raise

        except Exception as e:
            print "Something went wrong with the logging setup!"
            raise

        else:
            done = True

    logger = logging.getLogger('bulk')
    return logger


def validate_arguments(args):
    """
    Validate command line arguments.

    Keyword arguments:
    args -- a populated argument namespace from argparse

    Returns error messages, or none upon success.

    """

    # Check the IP addresses are actually IP addresses
    # Check the quarantine_directory is exists and is writable

    # Check the IP addresses first
    valid_ip = (
        "^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}"
        "([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$")

    if not re.match(valid_ip, args.remote_address):
        return 'remote_address parameter must be in IPv4 format' \
               ' (Ex. 127.0.0.1)'

    if not re.match(valid_ip, args.bind_address):
        return 'bind_address parameter must be in IPv4 format (Ex. 127.0.0.1)'

    # Then check the logging config file
    if os.path.isfile(args.log_config):
        try:
            with open(args.log_config):
                pass

        except IOError:
            return 'Cannot open and read logging config file "%s",' \
                   ' exiting' % args.log_config

    else:
        return 'Cannot find the logging config file "%s",' \
               ' exiting' % args.log_config

    # Then check the directories
    # filter(None, list) simple returns all non-none entities
    for directory in filter(None, [args.base_log_directory]):
        if os.path.isdir(directory):
            try:
                with open(directory + 'test.txt', 'wb') as f:
                    f.write('Testing write access to "%s"' % directory)

            except IOError:
                return 'Cannot write to directory "%s", exiting' % directory

            else:
                # If we get here, we know the file wrote, so remove it
                os.remove(directory + 'test.txt')

        else:
            create_sub_directories(directory)

    # Don't return an error string if we made it here
    return None


def run():
    """
    Start Bulk.

    Handles all commmand line arguments, logging setup,
    and kicking off the network listener.

    """
    parser = argparse.ArgumentParser(description='A content inspecting \
                                     mail relay built on smtpd')

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

    parser.add_argument(
        '--remote_address',
        default='127.0.0.1',
        help='Remote address to forward outbound mail. \
              Default is 127.0.0.1'
    )

    parser.add_argument(
        '--remote_port',
        default=25,
        type=int,
        help='Remote port to forward outbound mail. Default is 25'
    )

    # Note that type can be a function
    parser.add_argument(
        '--base_log_directory',
        default='/tmp/bulk/',
        type=directory_name,
        help='Directory to write log files, messages, and attachments. \
              Default is /tmp/bulk/'
    )

    parser.add_argument(
        '--log_all_messages',
        action='store_true',
        help='Log all messages to /base_log_directory/messages/'
    )

    parser.add_argument(
        '--block',
        action='store_true',
        help='Block mail with quarantined attachments. Default is False'
    )

    parser.add_argument(
        '--always_block',
        action='store_true',
        help='Turn the proxy into a server (block all). Default is false'
    )

    parser.add_argument(
        '--save_attachments',
        action='store_true',
        help='Experimental: Save all attachments as seperate files. \
             Default is false.'
    )

    parser.add_argument(
        '--log_config',
        default='/etc/bulk/logging.conf',
        help='Logging config file. Default is /etc/bulk/logging.conf'
    )

    # add a group to mark certain arguments as required
    req = parser.add_argument_group('required')
    # the processor arg is the only required argument
    req.add_argument(
        '--processor',
        default=[],
        required=True,
        nargs='+',
        action=CreateProcessor,
        dest='processors',
        help='Choose a processing engine by supplying an import string as the \
             first positional argument and multiple rules files as optional \
             following arguments. For example: \
             --processor bulk.processors.basic /etc/bulk/rules/simple'
    )

    args = parser.parse_args()
    err = validate_arguments(args)

    if err:
        raise Exception(err)

    create_sub_directories(args.base_log_directory)

    # Setup logging
    logger = setup_logging(args.log_config)
    logger.info('Starting Bulk Proxy')

    logger.info('Listening on %s:%s' %
                (args.bind_address, args.bind_port))

    if not args.always_block:
        logger.info('Forwarding to %s:%s' %
                    (args.remote_address, args.remote_port))

    logger.info('Bulk matches will be logged to %squarantine/'
                % args.base_log_directory)

    if args.block:
        logger.info('Emails that match a processor rule will be BLOCKED')

    if args.always_block:
        logger.info('Bulk set to BLOCK ALL mail')

    if args.log_all_messages:
        logger.info('Logging ALL messages to %smessages/'
                    % args.base_log_directory)

    if args.save_attachments:
        logger.info('Saving attachments to %sattachments/'
                    % args.base_log_directory)

    if args.processors:
        for p in args.processors:
            logger.info('Bulk using %s' % p)

    server = BulkProxy((args.bind_address, args.bind_port),
                       (args.remote_address, args.remote_port),
                       args.processors,
                       base_directory=args.base_log_directory,
                       block=args.block,
                       always_block=args.always_block,
                       log=args.log_all_messages,
                       save_attachments=args.save_attachments)

    # Kick off the main process
    asyncore.loop()


def stop():
    """
    Responsible for safely stopping Bulk.
    """

    logger = logging.getLogger('bulk')
    logger.info('Received a keyboard interrupt, stopping Bulk')


if __name__ == '__main__':
    try:
        run()

    except KeyboardInterrupt:
        stop()
