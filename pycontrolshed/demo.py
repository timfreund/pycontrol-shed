from pycontrolshed import *
from pycontrolshed.model import *
import sys

def main():
    arg_parser = create_default_arg_parser()
    (options, args) = arg_parser.parse_args()
    
    config = get_configuration(options.configuration)

    environment = options.environment
    if environment is None:
        if config.has_option('global_options', 'default_environment'):
            environment = config.get('global_options', 'default_environment')
        else:
            print "Environment must be supplied on the command line or provided"
            print "in your configuration file as default_environment"
            arg_parser.print_help()
            sys.exit(-1)

    environment = Environment(environment)
    environment.configure(config)
    bigip = environment.active_bigip_connection

    from IPython.Shell import IPShellEmbed; IPShellEmbed([])()


