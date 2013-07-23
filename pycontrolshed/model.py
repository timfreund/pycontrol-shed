# Copyright (C) 2011 Tim Freund and contributors.
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.

from functools import wraps
from pycontrol import pycontrol
import logging
import pycontrolshed
import socket

# In [1]: route_domains = bigip.Networking.RouteDomain.get_list()
# In [2]: route_domains
# Out[2]: [2220L]

log = logging.getLogger('pycontrolshed.model')

def partitioned(f):
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        partition = kwargs.get('partition', None)
        if partition:
            orig_partition = self.bigip.Management.Partition.get_active_partition()
            self.bigip.active_partition = partition
            rc = f(self, *args, **kwargs)
            self.bigip.active_partition = orig_partition
            return rc
        else:
            return f(self, *args, **kwargs)
    return wrapper


class NodeAssistant(object):
    def __init__(self, bigip):
        self.bigip = bigip

    def disable(self, nodes, partition=None):
        self.enable_disable_nodes(nodes, 'STATE_DISABLED', partition=partition)

    def enable(self, nodes, partition=None):
        self.enable_disable_nodes(nodes, 'STATE_ENABLED', partition=partition)

    @partitioned
    def enable_disable_nodes(self, nodes, target_state, partition=None):
        if isinstance(nodes, basestring):
            nodes = [nodes]

        targets = []
        states = []
        for node in nodes:
            targets.append(self.bigip.host_to_node(node))
            states.append(target_state)

        self.bigip.LocalLB.NodeAddress.set_session_enabled_state(node_addresses=targets,
                                                                 states=states)
        return self.status(nodes)

    @partitioned
    def status(self, nodes, partition=None):
        if isinstance(nodes, basestring):
            nodes = [nodes]

        targets = [self.bigip.host_to_node(node) for node in nodes]
        statuses = self.bigip.LocalLB.NodeAddress.get_session_enabled_state(node_addresses=targets)

        rc = []
        for node, status in zip(targets, statuses):
            rc.append({'node': node,
                       'fqdn': self.bigip.node_to_host(node),
                       'status': status})
        return rc


class VirtualAssistant(object):
    def __init__(self, bigip):
        self.bigip = bigip

    @partitioned
    def servers(self, partition=None):
        return self.bigip.LocalLB.VirtualServer.get_list()

    @partitioned
    def all_server_statistics(self, partition=None):
        return self.bigip.LocalLB.VirtualServer.get_all_statistics()

    @partitioned
    def addresses(self, partition=None):
        return self.bigip.LocalLB.VirtualAddress.get_list()

    @partitioned
    def all_address_statistics(self, partition=None):
        return self.bigip.LocalLB.VirtualAddress.get_all_statistics()


class PoolAssistant(object):
    def __init__(self, bigip):
        self.bigip = bigip

    def create_type(self, type_name):
        return self.bigip.LocalLB.PoolMember.typefactory.create(type_name)

    @partitioned
    def pools(self, partition=None):
        return self.bigip.LocalLB.Pool.get_list()

    @partitioned
    def members(self, pools, partition=None):
        if isinstance(pools, basestring):
            pools = [pools]

        session_status_list = self.bigip.LocalLB.PoolMember.get_session_enabled_state(pools)
        monitor_status_list = self.bigip.LocalLB.PoolMember.get_monitor_status(pools)

        rc = {}
        for pool, sessions, monitors in zip(pools, session_status_list, monitor_status_list):
            members = []
            for session, monitor in zip(sessions, monitors):
                members.append({'address': session.member.address,
                                'port': session.member.port,
                                'monitor': monitor,
                                'session': session})

            rc[pool] = {'members': members}
        return rc

    @partitioned
    def multi_member_statistics(self, pools, members, partition=None):
        seq_members = []
        ippd_seq_seq = self.create_type('Common.IPPortDefinitionSequenceSequence')
        ippd_seq_seq.item = seq_members

        empty_pools = []

        if isinstance(members, list):
            pass
        elif isinstance(members, dict):
            mlist = []
            for k in pools:
                if len(members[k]['members']) == 0:
                    empty_pools.append(k)
                else:
                    mlist.append(members[k]['members'])
            for ep in empty_pools:
                pools.remove(ep)
            members = mlist

        for member_list in members:
            seq_members.append(self.pool_members_to_ippd_seq(member_list))
        stats = self.bigip.LocalLB.PoolMember.get_statistics(pool_names=pools, members=ippd_seq_seq)
        rc = {}
        for p, s in zip(pools, stats):
            s = self.collapse_member_statistics(s)
            rc[p] = s

        return rc

    @partitioned
    def member_statistics(self, pool, member, partition=None):
        # TODO refactor this to be a special case of multi_member_statistics
        pools = [pool]
        if isinstance(member, basestring):
            ipp_member = self.bigip.host_port_to_ipportdef(*member.split(':'))
            member = ipp_member

        ippd_seq_seq = self.create_type('Common.IPPortDefinitionSequenceSequence')
        ippd_seq = self.create_type('Common.IPPortDefinitionSequence')

        ippd_seq_seq.item = ippd_seq
        ippd_seq.item = member

        # this is kind of garbage too...  see TODO above
        stats = self.bigip.LocalLB.PoolMember.get_statistics(pool_names=pools, members=ippd_seq_seq)[0].statistics[0]
        return stats

    def disable_member(self, pool_name, members, partition=None):
        return self.enable_disable_members(pool_name, members, 'STATE_DISABLED', partition=partition)

    def enable_member(self, pool_name, members, partition=None):
        return self.enable_disable_members(pool_name, members, 'STATE_ENABLED', partition=partition)

    @partitioned
    def enable_disable_members(self, pool_name, members, target_state, partition=None):
        pools = [pool_name]

        if isinstance(members, basestring) or members.__class__.__name__.count('IPPortDefinition'):
            members = [members]

        session_states = self.create_type('LocalLB.PoolMember.MemberSessionStateSequence')
        session_states.item = []
        for member in members:
            if isinstance(member, basestring):
                ipp_member = self.bigip.host_port_to_ipportdef(*member.split(':'))
                member = ipp_member

            state = self.create_type('LocalLB.PoolMember.MemberSessionState')
            state.member = member
            state.session_state = target_state
            session_states.item.append(state)

        self.bigip.LocalLB.PoolMember.set_session_enabled_state(pool_names=pools,
                                                                session_states=[session_states])
        return self.members(pools, partition=partition)

    def pool_members_to_ippd_seq(self, members):
        ippd_seq = self.create_type('Common.IPPortDefinitionSequence')
        ippd_members = []
        ippd_seq.item = ippd_members
        for member in members:
            address = None
            port = None
            if isinstance(member, dict):
                address = member['address']
                port = member['port']
            elif isinstance(member, basestring):
                address, port = member.split(':')
            else:
                raise Exception("Unknown member type")
            ippd_members.append(self.bigip.host_port_to_ipportdef(address, port))
        return ippd_seq

    def collapse_member_statistics(self, pool_stats):
        stats = {}
        # LocalLB.PoolMember.MemberStatisticEntry
        for mse in pool_stats.statistics:
            member_id = "%s:%d" % (mse.member.address,
                                   mse.member.port)
            stats[member_id] = {}
            for stat in mse.statistics:
                stats[member_id][stat.type] = {'high': stat.value.high,
                                               'low': stat.value.low}
        return stats


class PyCtrlShedBIGIP(pycontrol.BIGIP):
    def __init__(self, *args, **kwargs):
        pycontrol.BIGIP.__init__(self, *args, **kwargs)
        self.nodes = NodeAssistant(self)
        self.pools = PoolAssistant(self)
        self.virtual = VirtualAssistant(self)
        self._active_partition = None

    @property
    def active_partition(self):
        if self._active_partition:
            return self._active_partition
        self._active_partition = str(self.Management.Partition.get_active_partition())
        return self._active_partition

    @active_partition.setter
    def active_partition(self, partition):
        self.Management.Partition.set_active_partition(partition)
        self._active_partition = partition
        self._route_domains = self.Networking.RouteDomain.get_list()

    def host_port_to_ipportdef(self, host, port):
        ipp = self.LocalLB.PoolMember.typefactory.create('Common.IPPortDefinition')
        ipp.address = self.host_to_node(host)
        ipp.port = int(port)
        return ipp

    def host_to_node(self, host):
        # If someone provides us with a route domain, we're going to trust
        # that they know what route domain to use.
        if host.count('%'):
            host, route_domain = host.split('%', 1)
            return "%s%%%s" % (socket.gethostbyname(host), route_domain)

        node = socket.gethostbyname(host)
        if (len(self.route_domains) == 1) and self.route_domains[0] != 0:
            node += "%%%d" % self.route_domains[0]
        return node

    def node_to_ip(self, node):
        if node.count('%'):
            return node.split('%')[0]
        return node

    def node_to_host(self, node):
        return socket.getfqdn(self.node_to_ip(node))

    @property
    def route_domains(self):
        if hasattr(self, '_route_domains'):
            return self._route_domains
        self._route_domains = self.Networking.RouteDomain.get_list()
        return self._route_domains

    @property
    def partitions(self):
        partitions = []
        for partition in self.Management.Partition.get_partition_list():
            partitions.append({
                'name': partition['partition_name'],
                'description': partition["description"]
            })
        return partitions


class Environment(object):
    def __init__(self, name, hosts=[], wsdls=None, username=None):
        self.name = name
        self.hosts = hosts
        self.bigips = {}
        self.username = username
        self.wsdls = wsdls

        if self.wsdls is None:
            self.wsdls = [
                'LocalLB.NodeAddress', 'LocalLB.Pool', 'LocalLB.PoolMember',
                'LocalLB.Rule', 'LocalLB.VirtualAddress', 'LocalLB.VirtualServer',
                'Management.Partition', 'Networking.RouteDomain',
                'System.Failover',
            ]

        for host in self.hosts:
            self.connect_to_bigip(host)

    def __setattr__(self, name, value):
        if name in ['hosts', 'wsdls']:
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
    def all_bigip_connections(self):
        return [self.bigips[bigip] for bigip in self.bigips]

    @property
    def active_bigip_connection(self):
        for host in self.hosts:
            bigip = self.connect_to_bigip(host)
            if bigip.System.Failover.get_failover_state() == 'FAILOVER_STATE_ACTIVE':
                return bigip
        raise Exception('No active BIGIP devices were found in this environment (%s)' % self.name)

    def connect_to_bigip(self, host, wsdls=None, force_reconnect=False):
        if not(wsdls):
            wsdls = self.wsdls
        
        if not hasattr(self, 'password'):
            log.debug('No password has been set, attempting to retrive via keychain capabilities')
            password = pycontrolshed.get_password(self.name, self.username)
            if password:
                log.debug('Password retrived from the keychain')
                self.password = password
            else:
                log.error('No password is available')

        if host not in self.bigips or force_reconnect:
            self.bigips[host] = PyCtrlShedBIGIP(host,
                                                self.username,
                                                self.password,
                                                fromurl=True,
                                                wsdls=wsdls)
        return self.bigips[host]
