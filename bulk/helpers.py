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
import sys
import time
import errno


def directory_name(dn):
    """
    Appends proper directory path seperator to a directory path.

    Keyword arguments:
    dn -- the directory path

    """
    return os.path.normpath(dn) + os.sep


def convert_rules(rules):
    """
    Converts a list of rule files to a dict of rule files.

    Keyword arguments:
    rules -- list of rule files as fully qualified paths

    Argparse returns a list of files, use this to convert it
    to a dictionary in the format of:
    {'RuleFile0' : '/path/to/first', 'RuleFile1' : '/path/to/second', ... }

    Returns a dictionary of rule files.

    """
    results = {}
    for i, fn in enumerate(rules):
        results['RuleFile%s' % i] = fn

    return results


def create_sub_directories(basedir):
    """
    Create the necessary Bulk sub directories inside
    of a base directory.

    Keyword arguments:
    basedir -- base path to use in creating directories

    """
    # Create the sub directories for the log
    for each in ['messages', 'quarantine', 'attachments']:
        dir = directory_name(basedir + each)

        try:
            os.makedirs(dir)

        except OSError as e:
            # If file exists
            if e.args[0] == errno.EEXIST:
                pass

            else:
                raise


def build_processor(module_name, rules=None):
    """
    Imports a module and instantiates a Processor.

    Keyword arguments:
    module_name -- name of the module to import
    rules -- dictionary of rule files

    Returns a processor instance.

    """
    try:
        mod = __import__(module_name, fromlist=['processors'])

    except ImportError:
        print 'Cannot import %s as processor, exiting!' % module_name
        sys.exit(1)

    try:
        return mod.Processor(rules)

    except AttributeError:
        print "Module %s must define a 'Processor' class." \
              "See README" % module_name
        sys.exit(1)


def timeit(func):
    """
    Simple decorator to time functions
    """
    def wrapper(*arg):
        """
        """
        t1 = time.time()
        res = func(*arg)
        t2 = time.time()
        print '%s took %0.3f ms' % (func.func_name, (t2 - t1) * 1000.0)
        return res

    return wrapper
