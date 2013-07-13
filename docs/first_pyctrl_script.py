from pycontrolshed.model import Environment

# There are things we can do to put this configuration into
# a configuration file, but that'll come later.  Let's do 
# everything as explicitly as possible for now.

# Configuration values have been changed to protect the 
# innocent.  Please change the following four lines appropriately.
environment = Environment("development_network",
                          hosts=['127.0.0.2', '127.0.0.2'],
                          username='joe_sysadmin')
environment.password = "this_is_a_terrible_password"

# We have multiple hosts configured above.  If we want to get
# a list of all the BIGIP devices already connected and ready
# for us to run, we do

bigip_list = environment.all_bigip_connections

# More commonly, we just want to work on the BIGIP device that's
# currently active in the cluster:

bigip = environment.active_bigip_connection

# What partition are we in? 
print bigip.active_partition

# What partitions are available?
for partition_data in bigip.partitions:
    print '%s: %s' % (partition_data['name'], 
                      partition_data['description'])

# What if we want to change the partition that we're working in?
bigip.active_partition = 'Common'

# Let's get a list of pools:
for pool_name in bigip.pools.pools():
    print pool_name

# Let's get a list of members for the first pool in our list of pools:
pool_name = bigip.pools.pools()[0]
members = bigip.pools.members(pool_name)

# 'members' is actually a dictionary.  Keys are pool names, values 
# are member data
member_data = members[pool_name]

# member_data is also a dictionary.  In this case there's only one key:
# 'members'.  That sounds a little lame, but it gives us flexibilty to
# grab lots of information about pools through the same functional 
# interface.

for member in member_data['members']:
    print "%s %s" % (member['address'], member['monitor'].monitor_status)

