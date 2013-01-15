#!/usr/bin/env python

from setuptools import setup

setup(
    name='rss2jira',
    version='0.1.13',
    description='Create JIRA issues from RSS entries matching key terms.',
    author='nnutter',
    author_email='iam@nnutter.com',
    url='https://github.com/nnutter/rss2jira',
    packages=['rss2jira'],
    install_requires=['PyYAML>=3.10', 'feedparser>=5.1.2', 'jira-python>=0.12'],
    scripts=['bin/rss2jira', 'bin/rss2jira-email-report'],
    include_package_data=True,
    license='BSD',
    keywords=['rss', 'jira', 'rss2jira'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Bug Tracking',
    ],
)
