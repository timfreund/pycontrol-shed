# Copyright (C) 2011 Tim Freund and contributors.
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.

import ConfigParser
import getpass
import keyring
import os
import sys
from optparse import OptionParser


def create_default_arg_parser():
    parser = OptionParser(usage="usage: %%prog\n%s" % __doc__)
    parser.add_option("-c", "--configuration", dest="configuration",
                      default=os.path.expanduser('~/.pycontrolshed'))
    parser.add_option("-e", "--environment", dest="environment",
                      help="iControl environment")
    parser.add_option("-P", "--partition", dest="partition")
    return parser


def get_configuration(path=None):
    if path is None:
        path = os.path.expanduser('~/.pycontrolshed')

    try:
        os.stat(path)
    except OSError:
        print """You have no configuration file at %s.
We are creating one now, please edit for accuracy""" % (path)

        config_file = open(path, 'w')
        config_file.write("""[global_options]
default_environment=my_environment

[my_environment]
username=my_username
hosts=127.0.0.1,127.0.0.2

[my_other_environment]
username=my_other_username
hosts=127.0.0.3,127.0.0.4

""")

        sys.exit(-1)

    config = ConfigParser.ConfigParser()
    config.read(path)

    return config


def get_password(environment, username):
    default_keyring = keyring.get_keyring()
    password = default_keyring.get_password("pycontrolshed.%s" % environment, username)

    if not(password):
        print "No password found for %s@%s" % (username, environment)
        pass1 = getpass.getpass("Please enter the password for %s@%s: " % (username, environment))
        pass2 = getpass.getpass("Please confirm the password for %s@%s: " % (username, environment))

        if pass1 == pass2:
            default_keyring.set_password('pycontrolshed.%s' % environment, username, pass1)
            password = pass1
        else:
            raise Exception("passwords don't match")

    return password
