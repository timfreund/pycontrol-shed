# Copyright (C) 2011 Tim Freund and contributors.
# See LICENSE for details.

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
    return parser

def get_configuration(path=None):
    if path is None:
        path = os.path.expanduser('~/.pycontrolshed')

    config = ConfigParser.ConfigParser()
    config.read(path)

    return config

def get_password(environment, username):
    default_keyring = keyring.get_keyring()
    password = default_keyring.get_password("pycontrolshed.%s" % environment, username)

    if password is None:
        print "No password found for %s@%s" % (username, environment)
        pass1 = getpass.getpass("Please enter the password for %s@%s: " % (username, environment))
        pass2 = getpass.getpass("Please confirm the password for %s@%s: " % (username, environment))

        if pass1 == pass2:
            default_keyring.set_password('pycontrolshed.%s' % environment, username, pass1)
            password = pass1
        else:
            raise Exception("passwords don't match")

    return password
        
