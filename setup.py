#!/usr/bin/env python

from distutils.core import setup

setup(
    name='rss2jira',
    version='0.1',
    description='Create JIRA issues from RSS entries matching key terms.',
    author='nnutter',
    author_email='iam@nnutter.com',
    url='https://github.com/nnutter/rss2jira',
    packages=['rss2jira'],
    requires=['PyYAML (>3.10)', 'feedparser (>5.1.2)', 'jira (>0.12)'],
    scripts=['bin/rss2jira'],
    package_data={'rss2jira': ['rss2jira.conf.example']},
    data_files=[('/etc', ['rss2jira.conf.example'])],
)
