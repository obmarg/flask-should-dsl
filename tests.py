
import flask_should_dsl
from flask import Flask, abort, redirect
from unittest import TestCase
from should_dsl import should, should_not
from should_dsl.dsl import ShouldNotSatisfied

app = Flask('Flask-Should-DSL-Test')

# Keep pep8 happy
flask_should_dsl
have_status = None
be_200 = None
be_400 = None
be_401 = None
be_403 = None
be_404 = None
be_405 = None
be_500 = None
be_redirect_to = None


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
