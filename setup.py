#!/usr/bin/env python

from distutils.core import setup

setup(name="noderunner",
      description="NodeJS interoperability module",
      version="0.0.1",
      author="William Hogman",
      author_email="me@whn.se",
      packages=["noderunner"],
      url="http://whn.se/noderunner",
      package_dir={"noderunner": "noderunner"},
      package_data={"noderunner": ["js/*.js"]},
      install_requires=["gevent", "six"],
)
