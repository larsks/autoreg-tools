=============
Autoreg Tools
=============

This is a collection of tools for interacting with the Harvard FAS network
registration system, Autoreg.

Installation
============

These tools require the ``configdict`` module, which should install
automatically, and ``lxml``, which is often easier to install using your
system's package management tools (e.g., "yum install python-lxml", etc.).

So:

#. Install lxml.
#. Run ``setup.py``::

     python setup.py install

Using the audit script
======================

Configuration
-------------

You need to provide your Autoreg credentials to the audit script.  By
default it will try to open ``autoreg.conf`` in your current directory; you
can specify an alternate location with the ``-f`` command line option.

The file is an INI-style configuration file and should look something like
this::

  [autoreg]

  username = your_username
  password = your_password

Running
-------

To produce an audit of a network::

  audit-scope -o audit.csv 140.247.x.y

You can turn on slightly more verbose logging with ``-v``:

  audit-scope -v -o audit.csv 140.247.x.y

