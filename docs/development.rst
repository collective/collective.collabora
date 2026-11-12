Development
===========

For full SDK integration documentation docs, see:

- https://sdk.collaboraonline.com/docs/advanced_integration.html

Development setup
-----------------

A Collabora server for development is provided with this package. To run it::

  docker compose -f docker/docker-compose.yaml create --remove-orphans
  docker compose -f docker/docker-compose.yaml start

Then run a Plone 6.2 site with this package installed in development mode.
You will need to define a host alias ``host.docker.internal``, see below.

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

Integrating the editor in another UI
------------------------------------

``@@collabora-edit`` renders the editor iframe ``#cool-iframe``. The iframe
carries what ``edit.js`` needs as its own attributes, so an integration can
inject just that element into its own page, as Quaive does:

- ``collabora_server_url``: the target origin for ``postMessage`` calls.
- ``plone_version``: the host UI, from the view property of that name.
  ``edit.js`` sizes the iframe to the viewport from it: ``quaive`` uses the
  Quaive offset, any other value the Plone 6 offset. The value is also a CSS
  class on the two sections of the page, for host-specific styles.

To support another host UI, override ``plone_version`` in a subclass of
``CollaboraEditView``, register it for ``collabora-edit`` on your browser layer,
and load ``++resource++collective.collabora/edit.js`` on the pages that show
the iframe. The action buttons call the global ``collabora_action_*`` functions
of ``edit.js``.

Building, testing and CI
------------------------

This package is configured with `plone.meta <https://github.com/plone/meta>`_.
``tox`` drives the linters and the test runners.

Version 2.x supports Plone 6.2 on Python 3.11 to 3.14.
For older Plone versions, Archetypes or Python 2.7, use the 1.x series.

To run the whole matrix in parallel, with ``tox-uv`` fetching any missing
Python version::

  uvx --with tox-uv tox -p auto -o

Plain ``tox`` works too, if Python 3.11 to 3.14 are installed.

To list the environments::

  tox -l

To run all tests on one Python version::

  tox -e py312-plone62

To run a single test and spawn a debugger::

  tox -e py312-plone62 -- -t your_test_substring -D -x

To run the linters, and to reformat the code::

  tox -e lint
  tox -e format

To check that the package declares all its dependencies::

  tox -e dependencies

Github CI testing is configured in::

  .github/workflows/meta.yml
  .github/workflows/test-matrix.yml

For the tox CLI documentation, see:

- https://tox.wiki/en/latest/cli_interface.html

Contributing
------------

Please open an issue on `Github <https://github.com/collective/collective.collabora/issues>`_ if you have a problem.
Provide a full description of the problem you're encountering, including all necessary steps to reproduce.

To fix an issue, open a PR.
Please make sure all tests pass locally::

  uvx --with tox-uv tox -p auto -o

Add a change log entry as a file in ``news/``, see
`towncrier <https://towncrier.readthedocs.io/>`_.
