==========
 Commands
==========

Don't feel like guessing at the intent of pycontrolshed's commands?  A
summary of each follows:

pyctrl-member-disable, pyctrl-member-enable
===========================================

Disable or enable a pool member, respectively.  Pool name and member
identifiers are required::

  $ pyctrl-member-disable -p webservers -m 10.0.0.22:80
  $ pyctrl-member-enable -p webservers -m 10.0.0.22:80

No output is provided when the commands succeed.

pyctrl-member-list
==================

List members of a pool.  At least one pool name is required, and multiple
pool names are supported::

  $ pyctrl-member-list -p webservers
  webservers,10.0.0.22:80,STATE_ENABLED,MONITOR_STATUS_UP
  webservers,10.0.0.23:80,STATE_ENABLED,MONITOR_STATUS_UP
  
  $ pyctrl-member-list webservers tomcats
  webservers,10.0.0.22:80,STATE_ENABLED,MONITOR_STATUS_UP
  webservers,10.0.0.23:80,STATE_ENABLED,MONITOR_STATUS_UP
  tomcats,10.0.0.22:8080,STATE_ENABLED,MONITOR_STATUS_UP
  tomcats,10.0.0.23:8080,STATE_DISABLED,MONITOR_STATUS_DOWN

pyctrl-member-stats
===================

Get detailed statistics for a pool member::

  $ pyctrl-member-stats -p tomcats -m 10.0.0.23:8080
  STATISTIC_SERVER_SIDE_BYTES_IN,0,0
  STATISTIC_SERVER_SIDE_BYTES_OUT,0,0
  STATISTIC_SERVER_SIDE_PACKETS_IN,0,0
  STATISTIC_SERVER_SIDE_PACKETS_OUT,0,0
  STATISTIC_SERVER_SIDE_CURRENT_CONNECTIONS,0,0
  STATISTIC_SERVER_SIDE_MAXIMUM_CONNECTIONS,0,0
  STATISTIC_SERVER_SIDE_TOTAL_CONNECTIONS,0,0
  STATISTIC_PVA_SERVER_SIDE_BYTES_IN,0,0
  STATISTIC_PVA_SERVER_SIDE_BYTES_OUT,0,0
  STATISTIC_PVA_SERVER_SIDE_PACKETS_IN,0,0
  STATISTIC_PVA_SERVER_SIDE_PACKETS_OUT,0,0
  STATISTIC_PVA_SERVER_SIDE_CURRENT_CONNECTIONS,0,0
  STATISTIC_PVA_SERVER_SIDE_MAXIMUM_CONNECTIONS,0,0
  STATISTIC_PVA_SERVER_SIDE_TOTAL_CONNECTIONS,0,0
  STATISTIC_TOTAL_REQUESTS,0,0
  STATISTIC_TOTAL_PVA_ASSISTED_CONNECTIONS,0,0
  STATISTIC_CURRENT_PVA_ASSISTED_CONNECTIONS,0,0

pyctrl-node-disable and pyctrl-node-enable
==========================================

Disable or enable an entire node without touching individual pools.
This is especially helpful when removing a system (or systems) for
maintenance::

  $ pyctrl-node-disable www01.example.org
  $ pyctrl-node-disable db01.example.org db02.example.org
  $ pyctrl-node-enable www01.example.org
  $ pyctrl-node-enable db01.example.org db02.example.org

No output is generated when these commands succeed.

pyctrl-node-status
==================

Forgot what the status is for a node?  Run this::

  $ pyctrl-node-status www01.example.org
  10.0.0.22 (www01.example.org): STATE_DISABLED

pyctrl-pools
============

Get a sorted list of all the pools configured on your device::

  $ pyctrl-pools
  database
  tomcats
  webservers

pyctrl-shell
============

Maybe you want to explore the API yourself from the comfort of
an IPython prompt?  Give this a spin::

  $ pyctrl-shell
  Your BIGIP device is in a variable named bigip.
  
  
  In [1]: bigip.System.Failover.get_failover_mode
  
  Out[1]: <suds.client.Method instance at 0x4fba4d0>
  
  In [2]: bigip.System.Failover.get_failover_mode()
  
  Out[2]: FAILOVER_MODE_ACTIVE_STANDBY
  ...

