Pycontrol Shell Edition
=======================

The Pycontrol Shell Edition package builds on the pycontrol2 library
provided by F5 for use with their suite of BIGIP network devices.  

It contains some command line utilities to help administrators and 
developers gather information from and alter the configuration of 
their BIGIP devices.  

This library grows on an as-needed basis.  There are features missing
because I haven't needed them and no one else has asked or submitted 
a patch, so don't be shy.  

Authentication
--------------

This package uses the `Python Keyring`_ library to securely manage
credentials.  If you're on Gnome, it should securely store passwords
in your Gnome keychain.  KDE users should automatically use KWallet,
and similar native configurations for Windows and OS X users.  

It's tempting to drop credentials into a plain text configuration file
or script, and I hope that the inclusion of Keyring support will help
you stay secure.

Multiple Environment Support
----------------------------
Folks who use BIGIP devices typically have multiple environments:  test and prod,
data center A and data center B, etc.  The configuration file supports 
multiple environments and a default_environment option.  All commands 
support an --environment (-e) option as well. 

Failover Support
----------------

I use BIGIP devices that are in an Active/Standby configuration.  The
pycontrolshed library is capable of logging into all configured devices 
in an environment and return the active device to the calling program.

Questions
---------

Why not use the web interface?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
It's really slow, especially when upgrading over 100 application servers.

Why not use the SSH interface?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
I'm a developer with a limited access account on the devices at my day job,
so I am not authorized to use the SSH interface. 


.. _Python Keyring: http://pypi.python.org/pypi/keyring
