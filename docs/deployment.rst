Deployment
==========


Collabora server URL
--------------------


There is a required registry record you need to configure:
``collective.collabora.collabora_server_url``. This should be a publicly accessible URL
that accesses your Collabora server.


By default, ``collective.collabora.collabora_server_url`` is configured to
``http://host.docker.internal/collabora``. This requires a reverse proxy to be
set up, see below.

.. important::

   You will need to configure this value to match your deployment URL.

.. important::

   Any configuration of this record on the Plone side, needs to match the corresponding
   ``service_root`` record of the Collabora server in ``coolwsd.xml``. See below.

Avoiding CORS
+++++++++++++

Ideally, you will want to run the Collabora server on the same hostname and port
as your Plone site. This avoids any CORS (Cross-Origin Resource Sharing) problems.
Specifically, to be able to toggle fullscreen mode from the Plone side, requires
such a setup where Collabora runs in the same URL space as Plone.

To realize this setup, you need to:

1. Proxy to Collabora

  You need to configure your http server to proxy to Collabora.
  In the `./docker/nginx <https://github.com/collective/collective.collabora/tree/main/docker/nginx>`_ directory
  in this package you will find an example configuration that realizes this
  on the ``/collabora`` URL namespace.

2. Configure Collabora

  Configure the Collabora ``coolwsd.xml`` config file, to set the record
  ``service_root`` to the value of the proxied URL path (i.e. ``/collabora``).
  In the `./docker <https://github.com/collective/collective.collabora/tree/main/docker>`_ directory in this package you will find an ``coolwsd.xml``
  example configuration that realizes this configuration.

3. Configure Plone

  Configure the registry record ``collective.collabora.collabora_server_url``
  to ``https://your.plone.server/collabora``.

  .. hint::

     This needs to be a fully qualified URL.
     Configuring this record to only the path ``/collabora`` is invalid
     and will show an error in the UI and server logs.

See:

- https://sdk.collaboraonline.com/docs/installation/Proxy_settings.html

- https://sdk.collaboraonline.com/docs/installation/Configuration.html#network-settings


Collabora UI defaults
---------------------

You can configure the Collabora UI defaults on a per-site basis, by configuring the
registry record ``collective.collabora.ui_defaults``.

Collective.collabora ships with a default ui configuration that is compact and uncluttered::

  UIMode=compact;TextSidebar=false;TextRuler=false;PresentationStatusbar=false;SpreadsheetSidebar=false;

Once users change their UI preferences, this is persisted in browser local storage.

See:

- https://sdk.collaboraonline.com/docs/theming.html


Other Collabora configuration changes
-------------------------------------

To change the Collabora Online configuration, extract ``/etc/coolwsd/coolwsd.xml`` from the docker container.
Make changes, then use e.g. a bind mound to map your changed configuration back into the docker container.
See the provided example in ./docker (which only changes ``service_root``).

Session security
----------------

The Collabora Online `security architecture <https://sdk.collaboraonline.com/docs/architecture.html>`_
isolates all user document sessions from each other.

The only place where Collabora Online interacts with user data is what it gets
from ``@@collabora-wopi`` (including the document name). The
`personal data flow within Collabora <https://sdk.collaboraonline.com/docs/personal_data_flow.html>`_
can be further anonymized, see ``anonymize_user_data`` in the Collabora
``coolwsd.xml`` configuration file.

The collective.collabora ``@@collabora-edit`` view passes a authentication token to
the Collabora Online server. The Collabora Online server uses that
authentication token, to retrieve information from Plone via the
collective.collabora ``@@collabora-wopi`` view.

Collabora Online interacts with Plone exclusively though the ``@@collabora-wopi``
view, logged in as the user who opened the ``@@collabora-edit`` view. Both those
Plone views are protected with the ``zope2.View`` permission through normal ZCML
configuration. Additionally, performing a document save on ``@@collabora-wopi`` is
protected with the ``ModifyPortalContent`` permission in python.

Protection against potential session hijacking can be configured by enabling
`WOPI Proof <https://sdk.collaboraonline.com/docs/advanced_integration.html#wopi-proof>`_
in your production deployment of Collabora Online. I'm not sure that makes sense in
Plone though, since we already perform both authentication checks (twice: JWT +
protect tokens) and full RBAC authorization checks.

Deployment security configuration
---------------------------------

You will typically deploy a Collabora Online server behind a reverse proxy,
and otherwise firewall it from the open internet.

.. note::

   Whatever your network topology,
   Collabora Online needs to be able to connect to Plone on the public URL of your
   Plone site (or use the special direct URL, see below).

For a production deployment, you need to take the following security configurations into account:

- `Proxy settings <https://sdk.collaboraonline.com/docs/installation/Proxy_settings.html>`_
- `SSL configuration <https://sdk.collaboraonline.com/docs/installation/Configuration.html#ssl-configuration>`_
- `Content Security Policy <https://sdk.collaboraonline.com/docs/advanced_integration.html#content-security-policy>`_
- Other `security settings <https://sdk.collaboraonline.com/docs/installation/Configuration.html#security-settings>`_

Multihost configuration
-----------------------

If you want to use the same Collabora server to integrate with multiple sites,
you will need to configure
`host allow/deny policies <https://sdk.collaboraonline.com/docs/installation/Configuration.html#multihost-configuration>`_.

Direct Collabora-to-Plone connection
------------------------------------

Collabora performs direct calls to Plone, on the ``@@collabora-wopi`` view on File objects.
By default, this uses the same portal url where users access your Plone site in their browser.
In a full production setup, this means Collabora emits a request that travels outward from
wherever the Collabora server sits in your network, typically to the Nginx or Apache server
that performs your SSL termination; to then traverse your full frontend stack via Varnish
and HAProxy, to end up at a Plone instance.

In case that traversal outward-and-back-in-again gives problems, you can optionally
configure Collabora to hit a different URL to access Plone directly, by setting the
registry record ``collective.collabora.plone_server_url`` to point to a URL
that routes to Plone in a way that bypasses your frontend stack.

.. caution::

   Don't configure this, unless you know you need to.
