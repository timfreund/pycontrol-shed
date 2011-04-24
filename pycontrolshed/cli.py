# Copyright (C) 2011 Tim Freund and contributors.
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.

from pycontrolshed.model import Environment
from optparse import Option
import pycontrolshed
import socket
import sys

def members_validator(arg_parser, options, args):
    if (args is not None and len(args) > 0) or (options.pool is not None):
        return True
    print "Please supply one or more pool names"
    return False

def member_action_validator(arg_parser, options, args):
    if options.pool is None or options.member is None:
        print "Must supply pool and member arguments"
        return False
    return True

def parse_options(additional_options=[], validator=None, custom_usage=None):
    arg_parser = pycontrolshed.create_default_arg_parser()
    for option in additional_options:
        arg_parser.add_option(option)

    if custom_usage:
        arg_parser.usage = custom_usage

    (options, args) = arg_parser.parse_args()

    if validator is not None:
        if not validator(arg_parser, options, args):
            arg_parser.print_help()
            sys.exit(-1)

    options.configuration = pycontrolshed.get_configuration(options.configuration)

    if options.environment is None:
        if options.configuration.has_option('global_options', 'default_environment'):
            options.environment = options.configuration.get('global_options', 'default_environment')
        else:
            print "Environment must be supplied on the command line or provided"
            print "in your configuration file as default_environment"
            arg_parser.print_help()
            sys.exit(-1)

    options.environment = Environment(options.environment)
    options.environment.configure(options.configuration)

    return (options, args)

def members():
    options, args = parse_options([Option('-s', '--statistics',
                                          action="store_true", default=False, dest='statistics'),
                                   Option('-p', '--pool', dest='pool', help='Not strictly necessary, but it aligns the command options with other member related commands')],
                                  validator=members_validator,
                                  custom_usage="%prog pool_name1 [pool_name2 pool_name3 ...]")

    if options.pool is not None:
        args.append(options.pool)

    environment = options.environment
    bigip = environment.active_bigip_connection

    session_status_list = bigip.LocalLB.PoolMember.get_session_enabled_state(args)
    monitor_status_list = bigip.LocalLB.PoolMember.get_monitor_status(args)

    for pool, sessions, monitors in zip(args, session_status_list, monitor_status_list):
        for session, monitor in zip(sessions, monitors):
            member = session.member
            print "%s,%s:%d,%s,%s" % (pool,
                                      member.address,
                                      member.port,
                                      session.session_state,
                                      monitor.monitor_status)

def enable_disable_member(target_state):
    options, args = parse_options([Option('-p', '--pool', dest='pool', help='pool name'),
                                   Option('-m', '--member', dest='member',
                                          help='member address (host:port)')],
                                  member_action_validator)

    environment = options.environment
    bigip = environment.active_bigip_connection

    member = bigip.LocalLB.PoolMember.typefactory.create('Common.IPPortDefinition')
    addr, port = options.member.split(':')
    member.address = addr
    member.port = int(port)

    session_state = bigip.LocalLB.PoolMember.typefactory.create('LocalLB.PoolMember.MemberSessionState')
    session_state.member = member
    session_state.session_state = target_state
    
    session_states = bigip.LocalLB.PoolMember.typefactory.create('LocalLB.PoolMember.MemberSessionStateSequence')
    session_states.item = [session_state]

    bigip.LocalLB.PoolMember.set_session_enabled_state(pool_names=[options.pool],
                                                       session_states=[session_states])
    

def enable_member():
    enable_disable_member('STATE_ENABLED')

def disable_member():
    enable_disable_member('STATE_DISABLED')

def enable_node():
    enable_disable_node('STATE_ENABLED')

def disable_node():
    enable_disable_node('STATE_DISABLED')

def enable_disable_node(target_state):
    options, args = parse_options([],
                                  None,
                                  '%%prog node1 [node2 node3 node4]')
    if not len(args):
        print "No nodes provided"
    else:
        environment = options.environment
        bigip = environment.active_bigip_connection

        nodes = []
        states = []
        for node in args:
            nodes.append(socket.gethostbyname(node))
            states.append(target_state)
        
        bigip.LocalLB.NodeAddress.set_session_enabled_state(node_addresses=nodes, states=states)

def show_node_status():
    options, args = parse_options([],
                                  None,
                                  '%%prog node1 [node2 node3 node4]')
    if not len(args):
        print "No nodes provided"
    else:
        environment = options.environment
        bigip = environment.active_bigip_connection

        nodes = []
        for node in args:
            nodes.append(socket.gethostbyname(node))
        statuses = bigip.LocalLB.NodeAddress.get_session_enabled_state(node_addresses=nodes)

        for node, status in zip(nodes, statuses):
            print "%s (%s): %s" % (node, socket.getfqdn(node), status)

def show_member_statistics():
    # TODO refactor this and enable_disable_member to share common code
    options, args = parse_options([Option('-p', '--pool', dest='pool', help='pool name'),
                                   Option('-m', '--member', dest='member',
                                          help='member address (host:port)')],
                                  member_action_validator)
    environment = options.environment
    bigip = environment.active_bigip_connection

    member = bigip.LocalLB.PoolMember.typefactory.create('Common.IPPortDefinition')
    addr, port = options.member.split(':')
    member.address = addr
    member.port = int(port)

    ippd_seq_seq = bigip.LocalLB.PoolMember.typefactory.create('Common.IPPortDefinitionSequenceSequence')
    ippd_seq = bigip.LocalLB.PoolMember.typefactory.create('Common.IPPortDefinitionSequence')

    ippd_seq_seq.item = ippd_seq
    ippd_seq.item = member
    
    stats = bigip.LocalLB.PoolMember.get_statistics(pool_names=[options.pool], members=ippd_seq_seq)
    member_stats = stats[0].statistics[0]
    # member_stats.member is the IPPortDefinition
    for statistic in member_stats.statistics:
        print "%s,%d,%d" % (statistic.type, statistic.value.high, statistic.value.low)

def pools():
    options, args = parse_options()

    environment = options.environment
    bigip = environment.active_bigip_connection
    pools = bigip.LocalLB.Pool.get_list()
    pools.sort()

    for p in pools:
        print p

def shell():
    options, args = parse_options()
    environment = options.environment
    bigip = environment.active_bigip_connection

    print "Your BIGIP device is in a variable named bigip."
    from IPython.Shell import IPShellEmbed; IPShellEmbed([])()
