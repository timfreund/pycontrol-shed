==============
 Introduction
==============

Thanks for checking out the PyControl Shell Edition package.   This code 
builds on the `pyControl v2` library to provide a shell friendly way of 
interacting with F5 BIG-IP devices.  

This library grows on an as-needed basis.  There are features missing
because I haven't needed them and no one else has `asked`_ or 
`submitted a patch`_, so don't be shy.  

Features
========

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

We use BIGIP devices that are in an Active/Standby configuration at my
day job.  The pycontrol-shed library logs into all configured devices
in an environment, finds the active device, and returns it to the
calling program.

Questions
=========

Why not use the web interface?
------------------------------
It's really slow, especially when upgrading over 100 application servers.

Why not use the SSH interface?
------------------------------

1. I'm a developer with a limited access account on the devices at my day job,
   so I am not authorized to use the SSH interface. 
2. It's easier to script.

.. _Python Keyring: http://pypi.python.org/pypi/keyring
.. _asked: https://github.com/timfreund/pycontrol-shed/issues
.. _pyControl v2: http://devcentral.f5.com/Community/GroupDetails/tabid/1082223/asg/4/Default.aspx
.. _submitted a patch: https://github.com/timfreund/pycontrol-shed/pulls


