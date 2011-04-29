Configuration
*************

The ``pycontrol-shed`` library and command suite is built to help you
quickly interact with your BIG-IP devices.  Omitting device names,
user names, and passwords from individual commands has been a huge
enhancements, but it requires a bit of configuration.

You must have a configuration file at ``$HOME/.pycontrol-shed``.  Run a
command before creating that file, and the command will offer to
create one for you.

The file is broken into at least two sections: a ``global_options``
section and one section for each of your BIG-IP environments.  A 
sample configuration follows::

  [global_options]
  default_environment=dev
  
  [dev]
  username=timfreund
  hosts=10.27.13.33,10.27.13.34
  
  [prod]
  username=timfreund
  hosts=10.54.26.34,10.54.26.33


Environments
============

All of the ``pycontrol-shed`` commands accept an environment option as
an option (``-e`` or ``--environment=``), and the command will execute
against the environment specified as defined in your configuration
file.  The command will run in your ``default_environment`` if you do
not specify an environment on the command line.

Hosts
=====

Each environment will have a ``hosts`` option, and that option should
contain a comma separated list of devices for the environment.  You
don't need to remember which of your devices is active to run a
command: the library iterates through the hosts in the order provided,
logging in to each, until it finds ``FAILOVER_STATE_ACTIVE``.

Authentication
==============

We make use of the `Python Keyring`_ library for secure password
storage.  You will be asked to provide and confirm a password for new
devices, and that password will be stored in your operating system's
native keyring for later retrieval.  

The Keyring library can also store passwords in an encrypted text file
if you have no native keyring support in your operating system.  This will
be likely if you do most of your work via SSH sessions on remote systems. 


.. _Python Keyring: http://pypi.python.org/pypi/keyring
