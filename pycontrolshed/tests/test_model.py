from nose.tools import *
from unittest import TestCase
from pycontrolshed.model import Environment


class EnvironmentTest(TestCase):
    def test_hosts_setattr_list(self):
        env = Environment('test')
        env.hosts = ['192.168.1.1', '192.168.1.2']
        eq_(2, len(env.hosts))
        eq_(env.hosts[0], '192.168.1.1')
        eq_(env.hosts[1], '192.168.1.2')

    def test_hosts_setattr_str(self):
        env = Environment('test')
        env.hosts = '192.168.1.1, 192.168.1.2'
        eq_(2, len(env.hosts))
        eq_(env.hosts[0], '192.168.1.1')
        eq_(env.hosts[1], '192.168.1.2')

    def test_hosts_setattr_unicode(self):
        env = Environment('test')
        env.hosts = u'192.168.1.1, 192.168.1.2'
        eq_(2, len(env.hosts))
        eq_(env.hosts[0], u'192.168.1.1')
        eq_(env.hosts[1], u'192.168.1.2')
