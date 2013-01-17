import json
from should_dsl import matcher

from werkzeug.http import HTTP_STATUS_CODES

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
            self._response_data = response.data
            return self._actual == status

        def message_for_failed_should(self):
            message = 'Expected the status code {0}, but got {1}.'.format(
                      status, self._actual
                      )
            if self._response_data:
                response = 'Response Data:\n"{0}"'.format(self._response_data)
                message = '\n'.join([message, response])
            return message

        def message_for_failed_should_not(self):
            return 'Expected the status code not to be {0}'.format(status)
    return Checker


# Make be_xxx matchers for all the status codes
_status_codes = HTTP_STATUS_CODES.keys()
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
        #       Thinking a diff option might be good for this one too
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
        self._mimetype = content_type.find(';') == -1
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
        if self._expected == '*':
            return True
        if self._mimetype:
            self._actual = response.mimetype
            sections = self._actual.split('/')
            if self._match_either:
                return any(True for sec in sections if sec == self._expected)
            if self._wildcard:
                expectedsections = self._expected.split('/')
                for actual, expected in zip(sections, expectedsections):
                    if actual != expected and expected != '*':
                        return False
                return True
        else:
            self._actual = response.content_type
        return self._actual == self._expected

    def message_for_failed_should(self):
        return "Expected content type '{0}', got '{1}'".format(
            self._expected, self._actual
            )

    def message_for_failed_should_not(self):
        return "Expected content type to not be '{0}'".format(self._expected)


@matcher
class HeaderMatcher(object):
    ''' A matcher to check the headers returned '''
    name = 'have_header'

    def __call__(self, *pargs):
        if len(pargs) == 1:
            # One argument - this is either just the header name,
            # or the full header text
            expected = pargs[0].split(':')
        elif len(pargs) == 2:
            # Two arguments - should be header name & header value
            expected = pargs
        else:
            raise Exception('has_header accepts one or two arguments')
        self._expected_name = expected[0]
        try:
            self._expected_value = expected[1].strip()
            self._check_value = True
        except IndexError:
            self._check_value = False
        return self

    def match(self, response):
        self._value_found = None
        for name, value in response.header_list:
            if name == self._expected_name:
                self._value_found = value
                if not self._check_value:
                    return True
                elif value == self._expected_value:
                    return True
        return False

    def message_for_failed_should(self):
        if self._value_found:
            # We did find a header with this name
            return "Expected header '{0}' to be '{1}' not '{2}'".format(
                self._expected_name, self._expected_value, self._value_found
                )
        return "Expected header '{0}' was not found".format(
            self._expected_name
            )

    def message_for_failed_should_not(self):
        if self._check_value:
            return "Expected header '{0}' to not be '{1}'".format(
                self._expected_name, self._expected_value
                )
        return "Expected header '{0}' to not exist".format(
            self._expected_name
            )


@matcher
class ContentMatcher(object):
    ''' A matcher to check if a response has some content '''
    name = 'have_content'

    def __call__(self, content, find=False):
        self._expected = content
        self._find = find
        return self

    def match(self, response):
        self._actual = response.data
        if self._find:
            return self._actual.find(self._expected) != -1
        else:
            return self._actual == self._expected

    def message_for_failed_should(self):
        # TODO: An optional diff might be nice if we've got longer
        #       data.
        if self._find:
            if self._multiline:
                message = "Expected to find:\n{0}\n\nContained within:\n{1}"
            else:
                message = "Expected to find '{0}' in '{1}'"
        else:
            if self._multiline:
                message = "Expected content:\n{0}\n\nBut got:\n{1}"
            else:
                message = "Expected content '{0}' but got '{1}'"
        return message.format(self._expected, self._actual)

    def message_for_failed_should_not(self):
        if self._find:
            if self._multiline:
                message = "Did not expect to find:\n{0}\n\n" + \
                          "Contained within:\n{1}"
            else:
                message = "Did not expect to find '{0}' in '{1}'"
            return message.format(self._expected, self._actual)
        else:
            if self._multiline:
                message = "Expected content not to be:\n{0}"
            else:
                message = "Expected content not to be '{0}'"
            return message.format(self._expected)

    @property
    def _multiline(self):
        '''
        Property that checks if _expected or _actual is likely to take up
        more than one line
        '''
        for string in [self._expected, self._actual]:
            if len(string) > 80 or string.find('\n') != -1:
                return True
        return False
