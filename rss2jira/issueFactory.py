import logging
from requests.auth import HTTPBasicAuth
from jira.client import JIRA
from pprint import pformat


class JiraWrapper(object):

    def __init__(self, name, url, username, password, projectKey, issuetypeName):
        options = {
            'server': url,
            'basic_auth': {
                'username': username,
                'password': password,
            },
        }
        self.name = name
        self.projectKey = projectKey
        self.issuetypeName = issuetypeName

        self.jira = JIRA(options)

        # This is a work around for a reported bug reguarding basic auth:
        # https://bitbucket.org/bspeakmon/jira-python/pull-request/4/fix-for-issue-6-basic-authentication
        # https://bitbucket.org/bspeakmon/jira-python/issue/6/basic-authentication-doesnt-actually-use
        auth_url = url + '/rest/auth/1/session'
        auth_data = HTTPBasicAuth(username, password)
        self.jira._session.get(auth_url, auth=auth_data)

    def create_issue(self, entry):
        fields = {'project': {'key': self.projectKey}, 'summary': entry.title,
                'description': "Go to {} ({}).".format(self.name, entry.link),
                'issuetype': {'name': self.issuetypeName}}
        logging.debug(pformat(fields))
        return self.jira.create_issue(fields=fields)

