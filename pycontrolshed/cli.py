# Copyright (C) 2011 Tim Freund and contributors.
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.

from pycontrolshed.model import Environment
from optparse import Option
import pycontrolshed
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

    pools = bigip.pools.members(args, partition=options.partition)
    for pool_name, pool in pools.items():
        for member in pool['members']:
            print "%s,%s:%d,%s,%s" % (pool_name,
                                      member['address'],
                                      member['port'],
                                      member['session'].session_state,
                                      member['monitor'].monitor_status)


def pool_member_actor(function, **kwargs):
    options, args = parse_options([Option('-p', '--pool', dest='pool', help='pool name'),
                                   Option('-m', '--member', dest='member',
                                          help='member address (host:port)')],
                                  member_action_validator)

    environment = options.environment
    bigip = environment.active_bigip_connection

    member = options.member

    kwargs['bigip'] = bigip
    kwargs['member'] = member
    kwargs['pool'] = options.pool
    kwargs['partition'] = options.partition

    function(**kwargs)


def enable_disable_member(bigip, member, pool, target_state, partition=None):
    bigip.pools.enable_disable_members(pool, member, target_state, partition=partition)


def enable_member():
    pool_member_actor(enable_disable_member, target_state='STATE_ENABLED')


def disable_member():
    pool_member_actor(enable_disable_member, target_state='STATE_DISABLED')


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

        statuses = bigip.nodes.enable_disable_nodes(args, target_state,
                                                    partition=options.partition)
        print_node_statuses(args, statuses)


def show_node_status():
    options, args = parse_options([],
                                  None,
                                  '%%prog node1 [node2 node3 node4]')
    if not len(args):
        print "No nodes provided"
    else:
        environment = options.environment
        bigip = environment.active_bigip_connection

        statuses = bigip.nodes.status(args, partition=options.partition)
        print_node_statuses(args, statuses)


def print_node_statuses(nodes, statuses):
    for node, status in zip(nodes, statuses):
        if node == status['fqdn']:
            print "%s: %s" % (node, status['status'])
        else:
            print "%s (%s): %s" % (node, status['fqdn'], status['status'])


def show_member_statistics(bigip, pool, member, partition=None):
    member_stats = bigip.pools.member_statistics(pool, member, partition=partition)
    for statistic in member_stats.statistics:
        print "%s,%d,%d" % (statistic.type, statistic.value.high, statistic.value.low)


def show_member_statistics_cmd():
    pool_member_actor(show_member_statistics)


def pools():
    options, args = parse_options()

    environment = options.environment
    bigip = environment.active_bigip_connection
    pools = bigip.pools.pools(partition=options.partition)
    pools.sort()

    for p in pools:
        print p


def shell():
    options, args = parse_options()
    environment = options.environment
    bigip = environment.active_bigip_connection

    print "Your BIGIP device is in a variable named bigip."

    import IPython
    from IPython.config.loader import Config
    cfg = Config()
    IPython.embed(config=cfg)
