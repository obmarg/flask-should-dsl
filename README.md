flask-should-dsl
================

[![Build Status](https://secure.travis-ci.org/obmarg/flask-should-dsl.png)](http://travis-ci.org/obmarg/flask-should-dsl)

A flask extension for testing with should-dsl

This extension adds some basic matchers to should-dsl to allow it to be used
easily along with the standard flask testing setup.

### Requirements
- Python 2.6, 2.7 or PyPi (others may work, but these are all that's tested)
- [Should-DSL](http://www.should-dsl.info/)
- [Flask](http://flask.pocoo.org/)

### Installing

The recommended way to install flask is via `pip`:

    pip install flask-should-dsl

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

The matchers provided by flask-should-dsl are intended to be used with the
response objects that are returned by the flask test client.

The following matchers are provided by flask-should-dsl:

##### have_status

This checks the status of a response object

```python
>>> response = app.get('/ok')
>>> response |should| have_status(200)
>>> response |should| have_status(400)
Traceback (most recent call last):
...
ShouldNotSatisfied: Expected the status code 400, but got 200
```

##### be_xxx / abort_xxx / return_xxx

These matchers (be_200, be_404, be_500 etc.) provide shortcuts to check the
status of a response object.  The matchers are avaliable with be, abort and
return prefixes, to allow for more readable code depending on the
circumstances.  There should be matchers for each status code supported by
werkzeug. If you need a status code that is unsupported, the `have_status`
matcher may be used (or alternatively, file a bug and I'll add support for it)

```python
>>> response = app.get('/ok')
>>> response |should| be_200
>>> response |should_not| be_200
Traceback (most recent call last):
...
ShouldNotSatisfied: Expected the status code not to be 200
>>> app.get('/') |should_not| abort_500
>>> app.get('/') |should_not| return_404
```

##### redirect_to

This matcher checks if a response contains a redirect to another page

```python
>>> response = app.get('/redirect')
>>> response.location = 'http://localhost/redir'
>>> response |should| redirect_to('/redir')
>>> response.location = 'http://localhost/elsewhere'
>>> response |should| redirect_to('/redir')
Traceback (most recent call last):
...
ShouldNotSatisfied: Expected a redirect to "http://localhost/redir" but got "http://localhost/elsewhere"
>>> response = app.get('/ok')
>>> response |should| redirect_to('/redir')
Traceback (most recent call last):
...
ShouldNotSatisfied: Expected a redirect status, but got 200
```

##### have_json

This matcher checks if a response object contains matching JSON.  

```python
>>> response = app.get('/json')
>>> response |should| have_json({'a': 'b'})
>>> response |should| have_json({'b': 'c'})
ShouldNotSatisfied: Expected response to have json:
	{'b': 'c'}
but got:
	{u'a': u'b'}
```

It's also possible to pass in keyword arguments to have_json, which will be
converted into a dictionary before being compared to the json.

```python
>>> response |should| have_json(a='b')
>>> response |should| have_json(b='c')
ShouldNotSatisfied: Expected response to have json:
	{'b': 'c'}
```

##### have_content_type

This matcher checks if a response has it's content_type set to a certain value

```python
>>> response = app.get('/ok')
>>> response |should| have_content_type('text/html')
>>> response |should| have_content_type('application/json')
ShouldNotSatisfied: Expected content type 'application/json', got 'text/html'
>>> r |should_not| have_content_type('text/html')
ShouldNotSatisfied: Expected content type to not be 'text/html'
```

This matcher also supports wildcard matches, and if you do not supply both a
type & a subtype, then it will match on either.

```python
>>> response = app.get('/ok')
>>> response |should| have_content_type('html')
>>> response |should| have_content_type('text')
>>> response |should| have_content_type('text/*')
>>> response |should| have_content_type('*/html')
```

##### have_header

This matcher checks if a response has a header, and optionally checks if that
header is set to a certain value.

```python
>>> response = app.get('/ok')
>>> response |should| have_header('Content-Type')
>>> response |should_not| have_header('X-BadHeader')
>>> response |should_not| have_header('X-BadHeader', 'Something')
>>> response |should_not| have_header('X-BadHeader: Something')
>>> response |should| have_header('Content-Length', '100')
ShouldNotSatisfied: Expected header 'Content-Length' to be '100' not '0'
```

##### have_content

This matcher checks if a response contains certain content.  By default, it
expects the content to exactly match the input, but this can be overridden
with the `find` option.

```python
>>> response = app.get('/hello')
>>> response |should| have_content('hello')
>>> response |should_not| have_content('hello')
ShouldNotSatisfied: Expected content not to be 'hello'
>>> response |should| have_content('ello', find=True)
>>> response |should| have_content('hell', find=True)
>>> response |should| have_content('bye', find=True)
ShouldNotSatisfied: Expected to find 'bye' in 'hello'
```
