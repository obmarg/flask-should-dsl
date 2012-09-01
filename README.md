flask-should-dsl
================

[![Build Status](https://secure.travis-ci.org/obmarg/flask-should-dsl.png)](http://travis-ci.org/obmarg/flask-should-dsl)

A flask extension for testing with should-dsl

This extension adds some basic matchers to should-dsl to allow it to be used
easily along with the standard flask testing setup.

### Requirements
- Python 2.6 or 2.7 (others may work, but these are all that's tested)
- [Should-DSL 2.0a3](http://www.should-dsl.info/)
- [Flask](http://flask.pocoo.org/)

### Installing

Currently, flask-should-dsl needs to be installed from the github repository.
I hope to add it to pypi at some point in the future, but currently I'm testing
things to ensure they work. 

Assuming you have pip installed, the following command should work:

    pip install git+git://github.com/obmarg/flask-should-dsl.git

### Contributing

To contribute to flask-should-dsl:
- Create a fork of the repository on github
- Create a feature branch off the develop branch
- Do work
- When you're ready to contribute, create a pull request on github.

Usage
---

To enable the flask-should-dsl matchers, simply import the module:

```python
import flask.ext.should_dsl
```

### Matchers

The following matchers are provided by flask-should-dsl:

##### have_status

This checks the status of a response object

```python
>>> resp.status_code = 200
>>> resp |should| have_status(200)
>>> resp |should| have_status(400)
Traceback (most recent call last):
...
ShouldNotSatisfied: Expected the status code 400, but got 200
```

##### be_xxx

These matchers (be_200, be_400, be_401, be_403, be_404, be_405, be_500) provide
shortcuts to check the status of a response object.

```python
>>> resp.status_code = 200
>>> resp |should| be_200
>>> resp |should_not| be_200
Traceback (most recent call last):
...
ShouldNotSatisfied: Expected the status code not to be 200
```

##### be_redirect_to

This matcher checks if a response object represents a redirect.

```python
>>> response.status_code = 301
>>> response.location = 'http://localhost/redir'
>>> response |should| be_redirect_to('/redir')
>>> response.location = 'http://localhost/elsewhere'
>>> response |should| be_redirect_to('/redir')
Traceback (most recent call last):
...
ShouldNotSatisfied: Expected a redirect to "http://localhost/redir" but got "http://localhost/elsewhere"
>>> response.status_code = 200
Traceback (most recent call last):
...
ShouldNotSatisfied: Expected a redirect status, but got 200
```
