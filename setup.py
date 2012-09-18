"""
Flask-Should-DSL
-------------

A flask extension for testing with should-dsl.

This extension adds some basic matchers to should-dsl to allow it to be used
easily along with the standard flask testing setup.

See the Readme at http://github.com/obmarg/flask-should-dsl for more
information
"""

from setuptools import setup

setup(
    name='Flask-Should-DSL',
    version='0.2',
    url='http://github.com/obmarg/flask-should-dsl',
    license='BSD',
    author='Graeme Coupar',
    author_email='grambo@grambo.me.uk',
    description='A flask extension for testing with should-dsl',
    long_description=__doc__,
    # if you would be using a package instead use packages instead
    # of py_modules:
    packages=['flask_should_dsl'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask',
        'should-dsl'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Testing'
    ]
)
