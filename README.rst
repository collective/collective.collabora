.. This README is meant for consumption by humans and PyPI. PyPI can render rst files so please do not use Sphinx features.
   If you want to learn more about writing documentation, please check out: http://docs.plone.org/about/documentation_styleguide.html
   This text does not appear on PyPI or github. It is a comment.

.. image:: https://github.com/collective/collective.collabora/actions/workflows/plone-package.yml/badge.svg
    :target: https://github.com/collective/collective.collabora/actions/workflows/plone-package.yml

.. image:: https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/gyst/2a12a9fe2dbca0d4337ca96603bd58d7/raw/covbadge.json
    :alt: Coverage

.. image:: https://img.shields.io/pypi/v/collective.collabora.svg
    :target: https://pypi.python.org/pypi/collective.collabora/
    :alt: Latest Version

.. image:: https://img.shields.io/pypi/status/collective.collabora.svg
    :target: https://pypi.python.org/pypi/collective.collabora
    :alt: Egg Status

.. image:: https://img.shields.io/pypi/pyversions/collective.collabora.svg?style=plastic
    :alt: Supported - Python Versions

.. image:: https://img.shields.io/pypi/l/collective.collabora.svg
    :target: https://pypi.python.org/pypi/collective.collabora/
    :alt: License


====================
collective.collabora
====================

Collabora Online integration for Plone.


Introduction
============

`Collabora Online <https://www.collaboraonline.com/>`_ provides collaborative open source document editing, controlled by you.

Collective.collabora brings this capability into Plone. It can be used as-is,
and works out of the box in about any Plone version.

Additionally, collective.collabora provides a building block for integration of
real-time document collaboration into Plone-based applications like
Quaive and iA.Delib.

Features
--------

- Real-time collaborative document editing of office-type documents: Word
  documents, spreadsheets, etc.

- Reading Office files and PDFs in your browser in a Plone page, with comments,
  even if you do not have edit rights.

- Wide compatibility of this add-on across Plone and Python versions.

Status
------

Things that need to implemented/improved/tested:

- Edge case handling (Collabora down, locking conflicts, ...)

Authors
-------

- Johannes Raggam (thet): initial proof of concept (integration, WOPI implementation).

- Guido A.J. Stevens (gyst): production quality code (cleanup, tests, CI, documentation, backporting, release).


Contribute
----------

- Issue Tracker: https://github.com/collective/collective.collabora/issues

- Source Code: https://github.com/collective/collective.collabora


Support
-------

If you are having issues, please let us know via the `issue tracker
<https://github.com/collective/collective.collabora/issues>`_.

This package is part of `Quaive <https://quaive.com>`_ and supported by the
Quaive partners Cosent, Syslab.com and iMio.

Development of this package was sponsored by `iMio <https://imio.be>`_ and
`Syslab.com <https://syslab.com>`_.


License
-------

The project is licensed under the GPLv2.


Installation
============

Install collective.collabora by adding it to your buildout::

    [buildout]

    ...

    eggs =
        collective.collabora


and then run ``bin/buildout``.

You can then install collective.collabora though the add-on control panel.

For this to work, you need to have a Collabora Online service up and running.

See:

- https://sdk.collaboraonline.com/docs/installation/index.html

See docs/deployment.rst for instructions on configuring a production deployment.

See docs/development.rst for instructions on running a development setup.
