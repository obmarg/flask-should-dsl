import flask_should_dsl
from collections import namedtuple
from unittest import TestCase
from flask import Flask, abort, redirect, jsonify
from should_dsl import should, should_not
from should_dsl.dsl import ShouldNotSatisfied

app = Flask('Flask-Should-DSL-Test')

# Keep pep8 happy
flask_should_dsl
have_status = None
be_200 = be_400 = be_401 = be_403 = be_404 = be_405 = be_500 = None
abort_404 = abort_500 = raise_404 = raise_500 = None
be_redirect_to = None
have_json = None

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

    def should_have_raise_aliases(self):
        self.app.get('/missing') |should| raise_404
        self.app.get('/ok') |should_not| raise_500


class TestRedirects(BaseTest):
    def should_handle_redirects(self):
        response = self.app.get('/redir')
        response |should| be_redirect_to('/redir_target')
        response = self.app.get('/redir2')
        response |should_not| be_redirect_to('/redir_target')
        response = self.app.get('/ok')
        response |should_not| be_redirect_to('/redir_target')

    def should_handle_no_redirect(self):
        response = self.app.get('/redir')
        self.assertRaises(
                ShouldNotSatisfied,
                lambda: response |should| be_redirect_to('/redir_target2')
                )
        self.assertRaises(
                ShouldNotSatisfied,
                lambda: response |should_not| be_redirect_to('/redir_target')
                )
        response = self.app.get('/ok')
        self.assertRaises(
                ShouldNotSatisfied,
                lambda: response |should| be_redirect_to('/redir_target2')
                )


class TestHasJson(BaseTest):
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

