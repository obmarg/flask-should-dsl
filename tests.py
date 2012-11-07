import flask_should_dsl
from collections import namedtuple
from unittest import TestCase
from flask import Flask, abort, redirect, jsonify, make_response
from should_dsl import should, should_not
from should_dsl.dsl import ShouldNotSatisfied

app = Flask('Flask-Should-DSL-Test')

# Keep pep8 happy
flask_should_dsl
have_status = None
be_200 = be_400 = be_401 = be_403 = be_404 = be_405 = be_500 = None
abort_404 = abort_500 = return_404 = return_500 = None
redirect_to = None
have_content = have_json = have_content_type = have_header = None
have_content = None

JSON_DATA = {'a': 'b', 'c': 'd'}


@app.route('/ok')
def ok_route():
    return ''


@app.route('/missing')
def missing():
    abort(404)


@app.route('/redir')
def redir():
    return redirect('/redir_target')


@app.route('/redir2')
def redir2():
    return redirect('/redir_target2')


@app.route('/json')
def json_route():
    return jsonify(JSON_DATA)


@app.route('/headers')
def header_route():
    response = make_response('')
    response.headers['X-Wing'] = 'Awesome'
    return response


@app.route('/hello')
def hello_route():
    return "hello"


class BaseTest(TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()


class TestHaveStatus(BaseTest):
    def should_handle_success(self):
        response = self.app.get('/ok')
        response |should| have_status(200)
        response |should_not| have_status(400)

        response = self.app.get('/missing')
        response |should| have_status(404)
        response |should_not| have_status(200)

    def should_handle_failure(self):
        response = self.app.get('/ok')
        self.assertRaises(
                ShouldNotSatisfied,
                lambda: response |should| have_status(404)
                )
        self.assertRaises(
                ShouldNotSatisfied,
                lambda: response |should_not| have_status(200)
                )


class TestBeXxx(BaseTest):
    def should_handle_success(self):
        response = self.app.get('/ok')
        response |should| be_200
        response |should_not| be_404

        response = self.app.get('/missing')
        response |should| be_404
        response |should_not| be_500

    def should_handle_failure(self):
        response = self.app.get('/ok')
        self.assertRaises(
                ShouldNotSatisfied,
                lambda: response |should| be_404
                )
        self.assertRaises(
                ShouldNotSatisfied,
                lambda: response |should_not| be_200
                )

    def should_have_abort_aliases(self):
        self.app.get('/missing') |should| abort_404
        self.app.get('/ok') |should_not| abort_500

    def should_have_return_aliases(self):
        self.app.get('/missing') |should| return_404
        self.app.get('/ok') |should_not| return_500


class TestRedirects(BaseTest):
    def should_handle_redirects(self):
        response = self.app.get('/redir')
        response |should| redirect_to('/redir_target')
        response = self.app.get('/redir2')
        response |should_not| redirect_to('/redir_target')
        response = self.app.get('/ok')
        response |should_not| redirect_to('/redir_target')

    def should_handle_no_redirect(self):
        response = self.app.get('/redir')
        self.assertRaises(
                ShouldNotSatisfied,
                lambda: response |should| redirect_to('/redir_target2')
                )
        self.assertRaises(
                ShouldNotSatisfied,
                lambda: response |should_not| redirect_to('/redir_target')
                )
        response = self.app.get('/ok')
        self.assertRaises(
                ShouldNotSatisfied,
                lambda: response |should| redirect_to('/redir_target2')
                )


class TestHaveJson(BaseTest):
    def should_handle_expected_json(self):
        response = self.app.get('/json')
        response |should| have_json(JSON_DATA)
        response |should_not| have_json({})
        response |should_not| have_json({'e': 'f'})

    def should_handle_unexpected_json(self):
        response = self.app.get('/json')
        self.assertRaises(
                ShouldNotSatisfied,
                lambda: response |should| have_json({})
                )
        self.assertRaises(
                ShouldNotSatisfied,
                lambda: response |should_not| have_json(JSON_DATA)
                )

    def should_use_json_attribute(self):
        # Tests that the json attribute is used if it's there
        # (for use with flask-testing or whatever)
        fakeResponse = namedtuple('fakeResponse', ['json'])
        response = fakeResponse(JSON_DATA)
        response |should| have_json(JSON_DATA)
        response |should_not| have_json({})
        response |should_not| have_json({'e': 'f'})

    def should_accept_keyword_arguments(self):
        response = self.app.get('/json')
        response |should| have_json(**JSON_DATA)

    def should_reject_multiple_pos_arguments(self):
        response = self.app.get('/json')
        self.assertRaises(
                Exception,
                lambda: response |should| have_json(1, 2)
                )

    def should_reject_pos_and_keyword_arguments(self):
        response = self.app.get('/json')
        self.assertRaises(
                Exception,
                lambda: response |should| have_json(2, arg='')
                )


class TestHaveContentType(BaseTest):
    CTFakeResponse = namedtuple('CTFakeResponse', ['content_type'])
    MTFakeResponse = namedtuple('MTFakeResponse', ['mimetype'])

    def should_check_mime_type_by_default(self):
        # This tests a content_type without extra fields
        response = self.MTFakeResponse('application/json')
        response |should| have_content_type('application/json')
        self.assertRaises(
            ShouldNotSatisfied,
            lambda: response |should| have_content_type('text/html')
            )
        self.assertRaises(
            ShouldNotSatisfied,
            lambda: response |should_not| have_content_type('application/json')
            )

    def should_check_content_type_if_requested(self):
        response = self.CTFakeResponse('text/html; charset=utf-8')
        response |should| have_content_type('text/html; charset=utf-8')
        self.assertRaises(
            ShouldNotSatisfied,
            lambda: response |should| have_content_type(
                'text/html; charset=utf-16'
                )
            )

    def should_be_able_to_match_either(self):
        response = self.app.get('/ok')
        response |should| have_content_type('text')
        response |should| have_content_type('html')
        response |should_not| have_content_type('json')
        response |should_not| have_content_type('application')

    def should_accept_wildcards(self):
        response = self.app.get('/ok')
        response |should| have_content_type('text/*')
        response |should| have_content_type('*/html')
        response |should_not| have_content_type('application/*')
        response |should_not| have_content_type('*/json')
        response |should| have_content_type('*/*')
        response |should| have_content_type('*')

    def should_handle_actual_response(self):
        # This one tests an actual response
        response = self.app.get('/ok')
        response |should| have_content_type('text/html')
        response = self.app.get('/json')
        response |should| have_content_type('application/json')


class TestHaveHeader(BaseTest):
    def should_reject_too_many_arguments(self):
        response = self.app.get('/headers')
        self.assertRaises(
            Exception,
            lambda: response |should| have_header('x', 'y', 'z')
            )
        # Check too few while we're at it
        self.assertRaises(
            Exception,
            lambda: response |should| have_header()
            )

    def should_handle_header_text_in_single_argument(self):
        response = self.app.get('/headers')
        response |should| have_header('X-Wing: Awesome')
        response |should_not| have_header('X-Wing: Bad')
        response |should_not| have_header('X-Something: Bad')

    def should_check_header_presence(self):
        response = self.app.get('/headers')
        response |should| have_header('X-Wing')
        response |should_not| have_header('X-Something')

    def should_check_header_value(self):
        response = self.app.get('/headers')
        response |should| have_header('X-Wing', 'Awesome')
        response |should_not| have_header('X-Wing', 'Bad')
        response |should_not| have_header('X-Something', 'Bad')


class TestHaveContent(BaseTest):
    def should_handle_non_find_success(self):
        response = self.app.get('/hello')
        response |should| have_content('hello')
        response |should_not| have_content('bye')

    def should_handle_non_find_failure(self):
        response = self.app.get('/hello')
        # TODO: would be good to test the error messages from these
        self.assertRaises(
                ShouldNotSatisfied,
                lambda: response |should| have_content('bye')
                )
        self.assertRaises(
                ShouldNotSatisfied,
                lambda: response |should_not| have_content('hello')
                )

    def should_handle_find_success(self):
        response = self.app.get('/hello')
        response |should| have_content('hell', find=True)
        response |should| have_content('hello', find=True)
        response |should_not| have_content('oreo', find=True)

    def should_handle_find_failure(self):
        response = self.app.get('/hello')
        # TODO: would be good to test the error messages from these
        self.assertRaises(
                ShouldNotSatisfied,
                lambda: response |should| have_content('hello man', find=True)
                )
        self.assertRaises(
                ShouldNotSatisfied,
                lambda: response |should_not| have_content('ello', find=True)
                )
