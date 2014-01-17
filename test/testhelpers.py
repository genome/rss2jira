import re

class RegexMatcher(object):
    def __init__(self, regex, ignore_case=True):
        flags = 0
        if ignore_case is True:
            flags |= re.IGNORECASE
        self.regex = re.compile(regex, flags)

    def __eq__(self, x):
        return self.regex.search(x)

    def __repr__(self):
        return "Any string containing regex {}".format(self.regex)

    def __str__(self):
        return self.regex
