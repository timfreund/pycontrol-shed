# Copyright (C) 2011 Tim Freund and contributors.
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.

from pycontrol import pycontrol
import pycontrolshed

class Environment(object):
    def __init__(self, name, **kwargs):
        self.name = name
        self.hosts = []
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __getattr__(self, name):
        if name == 'password':
            return pycontrolshed.get_password(self.name, self.username)
        else:
            return self.__getattribute__(name)

    def __setattr__(self, name, value):
        if name == 'hosts':
            if isinstance(value, str) or isinstance(value, unicode):
                object.__setattr__(self, name, [host.strip() for host in value.split(',')])
            else:
                object.__setattr__(self, name, value)
        else:
            object.__setattr__(self, name, value)

    def configure(self, config):
        for k, v in config.items(self.name):
            setattr(self, k, v)

    @property
    def active_bigip_connection(self):
        for host in self.hosts:
            bigip = self.connect_to_bigip(host)
            if 'FAILOVER_STATE_ACTIVE' == bigip.System.Failover.get_failover_state():
                return bigip
        raise Exception('No active BIGIP devices were found in this environment (%s)' % self.name)

    def connect_to_bigip(self, host, wsdls=['LocalLB.NodeAddress', 'LocalLB.Pool', 'LocalLB.PoolMember', 
                                            'LocalLB.VirtualAddress', 'LocalLB.VirtualServer', 
                                            'Management.Partition', 'System.Failover']):
        bigip = pycontrol.BIGIP(host,
                                self.username,
                                self.password,
                                fromurl=True,
                                wsdls=wsdls)
        return bigip

