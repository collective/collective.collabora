Development
===========

For full SDK integration documentation docs, see:

- https://sdk.collaboraonline.com/docs/advanced_integration.html

Development setup
-----------------

A working development setup is provided with this package. To run it::

  docker compose -f docker/docker-compose.yaml create --remove-orphans
  docker compose -f docker/docker-compose.yaml start
  make start61

This will start Collabora and build and start Plone. You will need to
define a host alias ``host.docker.internal``, see below.

The ``collective.collabora:default`` profile configures the registry record
``collective.collabora.collabora_server_url`` to point at the :ref:`Collabora server URL`.

No localhost
++++++++++++

Use ``host.docker.internal`` instead of ``localhost``.

.. important::

   For this package to work you *cannot* access your Plone site on ``localhost``.

Plone provides its own URL to Collabora, and Collabora performs callbacks on
that URL. Obviously if Collabora tries to access localhost, it will reach itself
and not Plone. Protections against this misconfiguration are built into the
code.

Instead, add an alias in your ``/etc/hosts``::

  172.17.0.1      host.docker.internal

which binds to the docker bridge IP. This will enable COOL to connect to Plone.

Using a proxy to avoid CORS mode
++++++++++++++++++++++++++++++++

The docker example deployment provided, also starts an Nginx server configured
to listen on ``http://host.docker.internal``, which then proxies to both Plone
and Collabora.

To make that work for Collabora, you will need to manually configure the registry
record ``collective.collabora.server_url`` to ``http://host.docker.internal/collabora``.

See :ref:`Avoiding CORS` in the deployment configuration section.

Adapting to custom file fields
------------------------------

The ``IStoredFile`` interface and adapters feature ``file_field_name`` powered
getattr/setattr access to the underlying file field of the context object.
This is intended to make it easier to support objects whose file field has
a name which is different from ``file``: just subclass and provide the correct
``file_field_name`` in your subclass; you won't have to copy any of the actual logic.

Building, testing and CI
------------------------

This package uses ``tox`` to drive buildout and test runners.

See the provided ``Makefile`` for some usage pointers.
To build and test all environments::

  make all

To run a single development server::

  make start61

To run all tests for only that environment::

  tox -e py312-Plone61

To run a single test in a single environment and spawn a debugger::

  tox -e py312-Plone61 -- -t your_test_substring -D -x

To run all linters in parallel::

  tox -p -f lint

Github CI testing is configured in::

  .github/workflows/plone-package.yml

For the tox CLI documentation, see:

- https://tox.wiki/en/latest/cli_interface.html

Contributing
------------

Please open an issue on `Github <https://github.com/collective/collective.collabora/issues>`_ if you have a problem.
Provide a full description of the problem you're encountering, including all necessary steps to reproduce.

To fix an issue, open a PR.
Please make sure all tests pass locally::

  tox -p


Running the tests locally ensures, that your changes do not break backward compatibility
with older Plone versions running on Python 2.7.

.. note::

   The Github actions CI runs only Python 3.x tests. It does not run Python 2.7 tests.
