# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='pycontrolshed',
    version='1.0',
    description="BIGIP pycontrol shell edition",
    author='Tim Freund',
    author_email='tim@freunds.net',
    license = 'GPLv2+',
    url='http://github.com/timfreund/pycontrolshed',
    install_requires=[
        'pycontrol >= 2.0.0',
        'keyring',
                ],
    packages=['pycontrolshed'],
    test_suite='nose.collector',
    tests_require=[
                   'nose',
                   'coverage',
                   ],
    include_package_data=True,
    entry_points="""
    [console_scripts]
    pyctrl-member-disable = pycontrolshed.cli:disable_member
    pyctrl-member-enable = pycontrolshed.cli:enable_member
    pyctrl-member-list = pycontrolshed.cli:members
    pyctrl-member-stats = pycontrolshed.cli:show_member_statistics
    pyctrl-pools = pycontrolshed.cli:pools
    pyctrl-shell = pycontrolshed.cli:shell
    """,
)
