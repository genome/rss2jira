import logging
from requests.auth import HTTPBasicAuth
from jira.client import JIRA
from pprint import pformat


class JiraWrapper(object):

    def __init__(self, name, url, username, password, projectKey, issuetypeName):

        self.name = name
        self.url = url
        self.username = username
        self.password = password
        self.projectKey = projectKey
        self.issuetypeName = issuetypeName
        self.logger = logging.getLogger("rss2jira")

        self.options = {
            'server': url,
            'basic_auth': {
                'username': username,
                'password': password,
            },
        }

        self.jira = JIRA(self.options)
        self._authenticate()

    def _authenticate(self):
        # This is a work around for a reported bug reguarding basic auth:
        # https://bitbucket.org/bspeakmon/jira-python/pull-request/4/fix-for-issue-6-basic-authentication
        # https://bitbucket.org/bspeakmon/jira-python/issue/6/basic-authentication-doesnt-actually-use
        auth_url = self.url + '/rest/auth/1/session'
        auth_data = HTTPBasicAuth(self.username, self.password)
        rv = self.jira._session.get(auth_url, auth=auth_data)
        self.logger.info("Authentication result: {} {}".format(rv.status_code, rv.text))

    def _issue_dict(self, entry):
        return {'project': {'key': self.projectKey}, 'summary': entry.title,
                'description': "Go to {} ({}).".format(self.name, entry.link),
                'issuetype': {'name': self.issuetypeName}}

    def create_issue(self, entry):
        fields = self._issue_dict(entry)
        try:
            return self.jira.create_issue(fields=fields)
        except Exception as ex:
            self.logger.info("Caught exception while creating JIRA issue. " +
                "Reauthenticating and trying again... %s", ex)
            self._authenticate()
            return self.jira.create_issue(fields=fields)

