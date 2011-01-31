from pycontrolshed.model import Environment
from optparse import Option
import pycontrolshed
import sys

def members_validator(arg_parser, options, args):
    if args is not None and len(args) > 0:
        return True
    print "Please supply one or more pool names"
    return False

def state_switch_validator(arg_parser, options, args):
    if options.pool is None or options.member is None:
        print "Must supply pool and member arguments"
        return False
    return True

def parse_options(additional_options=[], validator=None):
    arg_parser = pycontrolshed.create_default_arg_parser()
    for option in additional_options:
        arg_parser.add_option(option)

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
    options, args = parse_options(validator=members_validator)

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
                                          help='member addres (host:port)')],
                                  state_switch_validator)

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

def pools():
    options, args = parse_options()

    environment = options.environment
    bigip = environment.active_bigip_connection
    pools = bigip.LocalLB.Pool.get_list()
    pools.sort()

    for p in pools:
        print p
