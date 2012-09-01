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
        return 'Expected the status code {}, but got {}'.format(
                self._expected, self._actual
                )

    def message_for_failed_should_not(self):
        return 'Expected the status code not to be {}'.format(self._expected)


def make_status_checker(status):
    '''
    Gets a status checker class
    :param status:  The status the checker should check for
    :returns:       A class that will check for the status
    '''
    class Checker(object):
        name = 'be_{}'.format(status)

        def __call__(self):
            return self

        def match(self, response):
            self._actual = response.status_code
            return self._actual == status

        def message_for_failed_should(self):
            return 'Expected the status code {}, but got {}'.format(
                    status, self._actual
                    )

        def message_for_failed_should_not(self):
            return 'Expected the status code not to be {}'.format(status)
    return Checker


# Make be_xxx matchers for all the status codes
_status_codes = [200, 400, 401, 403, 404, 405, 500]
for code in _status_codes:
    matcher(make_status_checker(code))


@matcher
class RedirectMatcher(object):
    ''' A matcher to check for redirects '''
    name = 'be_redirect_to'

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
            return 'Expected a redirect to "{}" but got "{}"'.format(
                    self._expected, self._actual_location
                    )
        else:
            return 'Expected a redirect status, but got {}'.format(
                    self._actual_status
                    )

    def message_for_failed_should_not(self):
        return 'Did not expect a redirect to "{}"'.format(
                self._expected
                )
