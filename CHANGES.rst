Changelog
=========

NB: all releases >= 1.2.0 and < 2.0 are refused by PyPi, which now requires collective_collabora as a name, instead of collective.collabora). Changing that would break python 2.7 compatibility and will only happen once 2.x is released.

Until then, the 1.x series >= 1.2.0 is only available via the private server pypi.quaive.net.
If you need updates, the suggested bridge until 2.x is available, is to re-release an egg to your own private server.

1.3.1 (2026-07-09)
------------------

- Fix Collabora menu bar overflow in non-English UI. [gyst]


1.3.0 (2026-06-22)
------------------

- Fix IStoredFile's file field name [cadam, gyst]

- Declare and test python3.14 and Plone 6.2 supported [gyst]

- More Github CI infra upgrades [gyst]


1.2.0 (2026-06-17)
------------------

- Reset File object actions on uninstall [gyst]

- Propagate UI language setting to Collabora [gyst]

- Update Github CI infrastructure [gyst]


1.1.0 (2025-07-25)
------------------

- Make it easier to provide custom IStoredField adapters for varying file field names. [gyst]


1.0.1 (2025-04-18)
------------------

- Fix documentation URL in setup.py [gyst]


1.0.0 (2025-04-18)
------------------

- Cleanup unused code [thet]

- Add translations [macagua, gyst]

- Extract documentation to readthedocs [gyst]

- Configure build tooling [gyst]

- Remove unneeded CORS headers [gyst]

- Let Collabora handle locking conflicts [gyst]

- Increase log level on file writes, and document that Collabora
  always saves changes, even on browser exit. [gyst]

- Disable CSRF protection, after exhausting all other options. [gyst]


0.9.0 (2025-04-10)
------------------

- Initial release. [gyst, ale-rt]
