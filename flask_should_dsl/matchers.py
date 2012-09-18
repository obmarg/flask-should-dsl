import json
from should_dsl import matcher


@matcher
class GenericStatusChecker(object):
    '''
    Generic status checking class
    '''
    name = 'have_status'

    def __call__(self, expected):
        self._expected = expected
        return self

    def match(self, response):
        self._actual = response.status_code
        return self._actual == self._expected

    def message_for_failed_should(self):
        return 'Expected the status code {0}, but got {1}'.format(
                self._expected, self._actual
                )

    def message_for_failed_should_not(self):
        return 'Expected the status code not to be {0}'.format(self._expected)


def make_status_checker(nameprefix, status):
    '''
    Gets a status checker class
    :param nameprefix:  The name prefix to use
    :param status:      The status the checker should check for
    :returns:           A class that will check for the status
    '''
    class Checker(object):
        name = '{0}_{1}'.format(nameprefix, status)

        def __call__(self):
            return self

        def match(self, response):
            self._actual = response.status_code
            return self._actual == status

        def message_for_failed_should(self):
            return 'Expected the status code {0}, but got {1}'.format(
                    status, self._actual
                    )

        def message_for_failed_should_not(self):
            return 'Expected the status code not to be {0}'.format(status)
    return Checker


# Make be_xxx matchers for all the status codes
_status_codes = [200, 400, 401, 403, 404, 405, 500]
for code in _status_codes:
    matcher(make_status_checker('be', code))
    matcher(make_status_checker('abort', code))
    matcher(make_status_checker('return', code))


@matcher
class RedirectMatcher(object):
    ''' A matcher to check for redirects '''
    name = 'redirect_to'

    def __call__(self, location):
        self._expected = 'http://localhost' + location
        self._status_ok = True
        return self

    def match(self, response):
        self._actual_status = response.status_code
        self._actual_location = response.location
        if self._actual_status not in (301, 302):
            self._status_ok = False
            return False
        return self._actual_location == self._expected

    def message_for_failed_should(self):
        if self._status_ok:
            return 'Expected a redirect to "{0}" but got "{1}"'.format(
                    self._expected, self._actual_location
                    )
        else:
            return 'Expected a redirect status, but got {0}'.format(
                    self._actual_status
                    )

    def message_for_failed_should_not(self):
        return 'Did not expect a redirect to "{0}"'.format(
                self._expected
                )


@matcher
class JsonMatcher(object):
    ''' A matcher to check for json responses '''
    name = 'have_json'

    def __call__(self, *pargs, **kwargs):
        if len(pargs) > 1:
            raise Exception('have_json only accepts one positional argument')
        if len(kwargs) > 0:
            if len(pargs) != 0:
                raise Exception(
                        "have_json can't accept positional arguments"
                        "& keyword arguments"
                        )
            self._expected = dict(**kwargs)
        else:
            self._expected = pargs[0]
        return self

    def match(self, response):
        try:
            self._actual = response.json
        except AttributeError:
            self._actual = json.loads(response.data)
        return self._actual == self._expected

    def message_for_failed_should(self):
        # TODO: Formatting on this could probably be better
        return "Expected response to have json:\n\t{0}\nbut got:\n\t{1}".format(
                self._expected, self._actual
                )

    def message_for_failed_should_not(self):
        # TODO: Formatting on this could probably be better
        return "Did not expect response to contain json:\n\t{0}".format(
                self._expected
                )


@matcher
class ContentTypeMatcher(object):
    ''' A matcher to check the content type '''
    name = 'have_content_type'

    def __call__(self, content_type):
        # If there's a ; in the expected type we want to check
        # the whole thing.
        self._split = content_type.find(';') == -1
        # If there's no / we want to match either half of the
        # content-type
        self._match_either = content_type.find('/') == -1
        # Check if we have any wildcards
        self._wildcard = any(
            True for sec in content_type.split('/') if sec == '*'
            )
        self._expected = content_type
        return self

    def match(self, response):
        self._actual = response.content_type
        if self._expected == '*':
            return True
        if self._split:
            self._actual = self._actual.split(';')[0]
            sections = self._actual.split('/')
            if self._match_either:
                return any(True for sec in sections if sec == self._expected)
            if self._wildcard:
                expectedsections = self._expected.split('/')
                for actual, expected in zip(sections, expectedsections):
                    if actual != expected and expected != '*':
                        return False
                return True
        return self._actual == self._expected

    def message_for_failed_should(self):
        return "Expected content type '{0}', got '{1}'".format(
            self._expected, self._actual
            )

    def message_for_failed_should_not(self):
        return "Expected content type to not be '{0}'".format(self._expected)


