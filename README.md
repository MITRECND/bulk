# Bulk - A content inspecting SMTP Proxy

Bulk is a content inspecting SMTP proxy/server. By default, it will
pull attachments from emails and analyze them with Yara.

```
Approved for Public Release; Distribution Unlimited. 13-0510
Copyright: ©2014 The MITRE Corporation. ALL RIGHTS RESERVED.
```

## Dependencies

Bulk has been tested with Python 2.7.
Bulk REQUIRES Python 2.7+ due to its use of argparse. Easy
installation of bulk requires setuptools.
There is no desire at this time to add compatibility for
older versions of Python.

1. [PCRE](http://www.pcre.org/)
1. [Yara](http://plusvic.github.io/yara/)
1. [Yara-Python](https://github.com/plusvic/yara/tree/master/yara-python)
1. [setuptools](https://pypi.python.org/pypi/setuptools)

## Build & Install

After installing the dependencies, install bulk by:

```
tar xzvf bulk-<version>.tar.gz
cd bulk-version
python setup.py build
sudo python setup.py install
```

Bulk scripts, such as bulk_proxy.py, can be placed in non-default locations
by using `--install-scripts /path/you/want` when calling `python setup.py install`.
This is useful if you managing multiple versions of python on a machine.

You can test your installation by invoking Python and trying to import bulk.

```
python
Python 2.7.2 (default, Feb  9 2012, 21:50:01)
[GCC 4.2.1 Compatible Apple Clang 3.0 (tags/Apple/clang-211.12)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> import bulk
>>>
```

# Basic Usage

Bulk is essentially an SMTP proxy, so you can run it as a listening service.
Otherwise, you can daemonize it in your OS's fashion. Bulk comes with scripts
to be run as services.

To run it as a service (with default options):

`bulk_proxy.py`

Or to check the help

```
bulk_proxy.py --help

usage: bulk_proxy.py [-h] [--bind_address BIND_ADDRESS]
                     [--bind_port BIND_PORT] [--remote_address REMOTE_ADDRESS]
                     [--remote_port REMOTE_PORT]
                     [--base_log_directory BASE_LOG_DIRECTORY]
                     [--log_all_messages] [--block] [--always_block]
                     [--save_attachments] [--log_config LOG_CONFIG]
                     --processor PROCESSORS [PROCESSORS ...]

A content inspecting mail relay built on smtpd

optional arguments:
  -h, --help            show this help message and exit
  --bind_address BIND_ADDRESS
                        Address to bind to and listen on for incoming mail.
                        Default is 127.0.0.1
  --bind_port BIND_PORT
                        Port to bind to and to listen on for incoming mail.
                        Default is 1025
  --remote_address REMOTE_ADDRESS
                        Remote address to forward outbound mail. Default is
                        127.0.0.1
  --remote_port REMOTE_PORT
                        Remote port to forward outbound mail. Default is 25
  --base_log_directory BASE_LOG_DIRECTORY
                        Directory to write log files, messages, and
                        attachments. Default is /tmp/bulk/
  --log_all_messages    Log all messages to /base_log_directory/messages/
  --block               Block mail with quarantined attachments. Default is
                        False
  --always_block        Turn the proxy into a server (block all). Default is
                        false
  --save_attachments    Experimental: Save all attachments as seperate files.
                        Default is false.
  --log_config LOG_CONFIG
                        Logging config file. Default is /etc/bulk/logging.conf

required:
  --processor PROCESSORS [PROCESSORS ...]
                        Choose a processing engine by supplying an import
                        string as the first positional argument and multiple
                        rules files as optional following arguments. For
                        example: --processor bulk.processors.basic
                        /etc/bulk/rules/simple
```

# Logging

Logging is accomplished via [Python's logging module](http://docs.python.org/library/logging.html).

To configure logging for bulk, use a configuration file. You can
see the default configuration file in `conf/logging.conf`. You can
pass a logging.conf file using the `--logging` command line option.

# Contributing
We love to hear from people using our tools and code.
Feel free to discuss issues on our issue tracker and make pull requests!
