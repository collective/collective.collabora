Adding and updating locales
---------------------------

For every language you want to translate into you need a
locales/[language]/LC_MESSAGES/collective.task.po
(e.g. locales/de/LC_MESSAGES/collective.task.po)

For German

.. code-block:: console

    $ mkdir de

For updating locales

.. code-block:: console

    $ ./bin/update_locale

If the script is not existing at the ``./bin/update_locale`` path, alternativelly you can run the script
from the root of the locales directory:

.. code-block:: console

    $ ./locales/update_locale.sh

Note
----

The script uses gettext package for internationalization.

Install it before running the script.

On macOS
--------

.. code-block:: console

    $ brew install gettext

On Windows
----------

see https://mlocati.github.io/articles/gettext-iconv-windows.html

i18ndude
--------

The bask script also uses i18ndude package for performs various tasks related to ZPT's, Python Scripts and i18n.

Install it before running the script.

macOS/Linux/WSL on Windows
--------------------------

.. code-block:: console

    $ pip3 install i18ndude

see https://github.com/collective/i18ndude
