flask-should-dsl
================

[![Build Status](https://secure.travis-ci.org/obmarg/flask-should-dsl.png)](http://travis-ci.org/obmarg/flask-should-dsl)

A flask extension for testing with should-dsl

This extension adds some basic matchers to should-dsl to allow it to be used
easily along with the standard flask testing setup.

### Requirements
- Python 2.6 or 2.7 (others may work, but these are all that's tested)
- [Should-DSL](http://www.should-dsl.info/)
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

##### be_xxx / abort_xxx / return_xxx

These matchers (be_200, be_400, be_401, be_403, be_404, be_405, be_500) provide
shortcuts to check the status of a response object.  The matchers are avaliable
with be, abort and return prefixes, to allow for more readable code depending on
the circumstances

```python
>>> resp.status_code = 200
>>> resp |should| be_200
>>> resp |should_not| be_200
Traceback (most recent call last):
...
ShouldNotSatisfied: Expected the status code not to be 200
>>> app.get('/') |should_not| abort_500
>>> app.get('/') |should_not| return_404
```

##### redirect_to

This matcher checks if a response contains a redirect to another page

```python
>>> response.status_code = 301
>>> response.location = 'http://localhost/redir'
>>> response |should| redirect_to('/redir')
>>> response.location = 'http://localhost/elsewhere'
>>> response |should| redirect_to('/redir')
Traceback (most recent call last):
...
ShouldNotSatisfied: Expected a redirect to "http://localhost/redir" but got "http://localhost/elsewhere"
>>> response.status_code = 200
>>> response |should| redirect_to('/redir')
Traceback (most recent call last):
...
ShouldNotSatisfied: Expected a redirect status, but got 200
```

##### have_json

This matcher checks if a response object contains matching JSON.  

```python
>>> r.data = json.dumps({'a': 'b'})
>>> r |should| have_json({'a': 'b'})
>>> r |should| have_json({'b': 'c'})
ShouldNotSatisfied: Expected response to have json:
	{'b': 'c'}
but got:
	{u'a': u'b'}
```

It's also possible to pass in keyword arguments to have_json, which will be
converted into a dictionary before being compared to the json.

```python
>>> r |should| have_json(a='b')
>>> r |should| have_json(b='c')
ShouldNotSatisfied: Expected response to have json:
	{'b': 'c'}
```

##### have_content_type

This matcher checks if a response has it's content_type set to a certain value

```python
>>> r.content_type = 'text/html'
>>> r |should| have_content_type('text/html')
>>> r |should| have_content_type('application/json')
ShouldNotSatisfied: Expected content type 'application/json', got 'text/html'
>>> r |should_not| have_content_type('text/html')
ShouldNotSatisfied: Expected content type to not be 'text/html'
```

This matcher also supports wildcard matches, and if you do not supply both a
type & a subtype, then it will match on either.

```python
>>> r.content_type = 'text/html'
>>> r |should| have_content_type('html')
>>> r |should| have_content_type('text')
>>> r |should| have_content_type('text/*')
>>> r |should| have_content_type('*/html')
```

##### have_header

This matcher checks if a response has a header, and optionally checks if that
header is set to a certain value.

```python
>>> response |should| have_header('Content-Type')
>>> response |should| have_header('Content-Type')
>>> response |should_not| have_header('X-BadHeader')
>>> response |should_not| have_header('X-BadHeader', 'Something')
>>> response |should_not| have_header('X-BadHeader: Something')
>>> response |should| have_header('Content-Length', '100')
ShouldNotSatisfied: Expected header 'Content-Length' to be '100' not '0'
```
